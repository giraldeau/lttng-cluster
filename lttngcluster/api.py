from collections import OrderedDict
from fabric.api import task, run, parallel, env, get, settings
from fabric.tasks import execute
from os.path import dirname, basename, join
import sys
import time
from traceback import print_exception
import yaml
from lttngcluster.utils import dict_product


default_kernel_events = [
    "sched_ttwu",
    "sched_switch",
    "sched_process_fork",
    "sched_process_exec",
    "sched_process_exit",
    "inet_sock_local_out",
    "inet_sock_local_in",
    "softirq_entry",
    "softirq_exit",
    "hrtimer_expire_entry",
    "hrtimer_expire_exit",
    "irq_handler_entry",
    "irq_handler_exit",
    "lttng_statedump_end",
    "lttng_statedump_process_state",
    "lttng_statedump_start",
]

default_userspace_events = []
default_username = 'ubuntu'
default_trace_name = 'auto'
default_trace_dir = '~/lttng-traces'
default_tmp_dir = '~/lttng-traces-tmp'

env.tracename = "default"

def run_foreground(cmd):
    run(cmd)

def run_background(cmd):
    run('nohup %s > cmd.out 2> cmd.err < /dev/null &' % (cmd), pty=False)

@parallel
def trace_start(opts):
    dest = opts.get_trace_dir_ctx('tmpdir')
    name = opts.get_session_name_ctx()
    run("lttng destroy -a")
    run("test -f /usr/local/bin/control-addons.sh && control-addons.sh load")
    run("lttng create %s -o %s" % (name, dest))
    run("lttng enable-channel k -k --subbuf-size 16384 --num-subbuf 4096")
    kev = opts.get('events', {}).get('kernel', default_kernel_events)
    ev_string = ",".join(kev)
    run("lttng enable-event -k -c k %s" % ev_string)
    run("lttng enable-event -k -c k -a --syscall")
    run("lttng add-context -k -c k -t tid -t procname")
    run("lttng start")

@parallel
def trace_stop(opts):
    name = opts.get_session_name_ctx()
    with settings(warn_only=True):
        run("lttng stop %s" % name)
        run("lttng destroy %s" % name)

@task
def trace_fetch(opts):
    dest_remote = opts.get_trace_dir_ctx('tmpdir')
    dest_local = opts.get_trace_dir_ctx('tracedir')
    print("fetch trace %s" % (dest_remote))
    remote_src = join(dest_remote, "*")
    local_dst = join(dest_local, "%(host)s", "%(path)s")
    get(remote_src, local_dst)
    run('rm -rf %s' % (dest_remote))

def merge_dict(dst, src):
    for k in src.keys():
        if (isinstance(dst.get(k, None), dict) and
            isinstance(src.get(k, None), dict)):
            merge_dict(dst[k], src[k])
        else:
            dst[k] = src[k]

class TraceRunnerDefault(object):
    '''Run an experiment under tracing'''
    def __init__(self):
        self._dry_run = False
    def set_dry_run(self, dry_run):
        self._dry_run = dry_run
    def run(self, exp):
        opts = exp.get_options()
        for ctx in opts.context_generator():
            status = self._run_one(exp)
            if not status:
                break

    def _run_one(self, exp):
        opts = exp.get_options()
        hosts_list = opts.get_hosts()
        success = True
        try:
            exp.before()
            if not self._dry_run:
                execute(trace_start, opts, hosts=hosts_list)
            exp.action()
        except Exception:
            t, v, tb = sys.exc_info()
            print_exception(t, v, tb)
            success = False
        finally:
            if not self._dry_run:
                execute(trace_stop, opts, hosts=hosts_list)
        exp.after()
        if success and not self._dry_run:
            execute(trace_fetch, opts, hosts=hosts_list)
        return success

class RecipeErrorCollection(object):
    def __init__(self):
        self.errors = []

    def add(self, error):
        self.errors.append(error)

    def __len__(self):
        return len(self.errors)

    def __repr__(self):
        return repr(self.errors)

class TraceExperiment(object):
    '''Experiment definition'''
    def __init__(self):
        self._options = {}
    def set_options(self, options):
        self._options = options
    def get_options(self):
        return self._options
    def validate(self, errors):
        raise NotImplementedError()
    def before(self):
        pass
    def action(self):
        raise NotImplementedError()
    def after(self):
        pass

class TraceExperimentOptions(dict):

    default_options = {
        'name': default_trace_name,
        'experiment': 'TraceExperimentShell',
        'username': default_username,
        'events': {
            'kernel': default_kernel_events,
            'userspace': default_userspace_events
        },
        'roledefs': {},
        'parameters': {},
        'tracedir' : default_trace_dir,
        'tmpdir': default_tmp_dir,
        'dry_run': False,
    }

    import_key = 'import'
    name_key = 'name'
    yaml_ext = ".yaml"

    def __init__(self, *args, **kwargs):
        self._loaded = []
        self._hosts = []
        self._time = time.strftime("%Y%m%d-%H%M%S")
        self._current_context = {}
        super(TraceExperimentOptions, self).__init__(*args, **kwargs)

    def load_path(self, path):
        with open(path) as f:
            opt = yaml.load(f)
            if opt is None:
                opt = {}
            # load submodule
            imp = opt.get(self.import_key, [])
            if not hasattr(imp, '__iter__'):
                imp = [imp]
            for mod in imp:
                if mod not in self._loaded:
                    self._loaded.append(mod)
                    base = dirname(path)
                    p = join(base, mod + '.yaml')
                    self.load_path(p)
            if opt.has_key(self.import_key):
                del opt[self.import_key]
            if not opt.has_key('name') and \
                    path.endswith(self.yaml_ext):
                name = basename(path[:-len(self.yaml_ext)])
                self['name'] = name
            merge_dict(self, opt)
        # fix roledefs type
        roles = self.get('roledefs', {})
        if not isinstance(roles, dict):
            raise ValueError('roledefs must be a dict: %s' % path)
        for k, v in roles.items():
            if not hasattr(v, '__iter__'):
                roles[k] = [v]
        parameters = self.get('parameters', {})
        if not isinstance(parameters, dict):
            raise ValueError('parameters must be a dict: %s' % path)

    def load(self, stream):
        opt = yaml.load(stream)
        if opt is None:
            opt = {}
        merge_dict(self, opt)

    def get_session_name_ctx(self):
        return self.get_session_name(**self._current_context)

    def get_session_name(self, **kwargs):
        name = self.get('name', default_trace_name)
        name = "%s-%s" % (name, self._time)
        for k, v in kwargs.items():
            name = "%s-%s=%s" % (name, k, v)
        return name

    def get_trace_dir_ctx(self, kind='tracedir'):
        return self.get_trace_dir(kind, **self._current_context)

    def get_trace_dir(self, kind='tracedir', **kwargs):
        base = self.get(kind, default_trace_dir)
        name = self.get_session_name(**kwargs)
        return join(base, name)

    def get_hosts(self):
        self._update_hosts()
        return self._hosts

    def get_context(self):
        return self._current_context

    def context_generator(self):
        parameters = self.get('parameters', {})
        context = dict_product(parameters)
        for ctx in context:
            self._current_context = ctx
            yield ctx

    def _update_hosts(self):
        hosts = []
        roles = self.get('roledefs', {})
        for k, v in roles.items():
            if isinstance(v, list):
                hosts += v
            elif isinstance(v, str):
                hosts.append(v)
            else:
                raise TypeError("invalid type for roledefs %s" % k)
        self._hosts = list(OrderedDict.fromkeys(hosts))

