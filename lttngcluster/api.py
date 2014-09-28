from collections import OrderedDict
from fabric.api import task, run, parallel, env, get
from fabric.tasks import execute
from os.path import dirname, basename, join
import time
import yaml


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

env.tracename = "default"

def run_bg(cmd):
    run('nohup %s > cmd.out 2> cmd.err < /dev/null &' % (cmd), pty=False)

@parallel
def trace_start(opts):
    dest = opts.get_trace_dir()
    run("lttng destroy -a")
    run("test -f /usr/local/bin/control-addons.sh && control-addons.sh load")
    run("lttng create -o %s" % dest)
    run("lttng enable-channel k -k --subbuf-size 16384 --num-subbuf 4096")
    kev = opts.get('events', {}).get('kernel', default_kernel_events)
    ev_string = ",".join(kev)
    run("lttng enable-event -k -c k %s" % ev_string)
    run("lttng enable-event -k -c k -a --syscall")
    run("lttng add-context -k -c k -t tid -t procname")
    run("lttng start")

@parallel
def trace_stop(opts):
    run("lttng stop")
    run("lttng destroy -a")

@task
def trace_fetch(opts):
    dest = opts.get_trace_dir()
    print("fetch trace %s" % (dest))
    remote_src = join(dest, "*")
    local_dst = join(dest, "%(host)s", "%(path)s")
    get(remote_src, local_dst)
    # run("rm -rf ~/lttng-traces/%s" % (env.tracename))

def merge_dict(dst, src):
    for k in src.keys():
        if (isinstance(dst.get(k, None), dict) and
            isinstance(src.get(k, None), dict)):
            merge_dict(dst[k], src[k])
        else:
            dst[k] = src[k]

class TraceRunnerDefault(object):
    '''Run an experiment under tracing'''
    def run(self, exp):
        opts = exp.get_options()
        hosts_list = opts.get_hosts()
        exp.before()
        execute(trace_start, opts, hosts=hosts_list)
        exp.action()
        execute(trace_stop, opts, hosts=hosts_list)
        exp.after()
        execute(trace_fetch, opts, hosts=hosts_list)

class RecipeErrorCollection(object):
    def __init__(self):
        self.errors = []

    def add(self, error):
        self.errors.append(error)

    def __len__(self):
        return len(self.errors)

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
        'experiment': None,
        'username': default_username,
        'events': {
            'kernel': default_kernel_events,
            'userspace': default_userspace_events
        },
        'rolesdef': {},
        'params': {},
        'tracedir' : default_trace_dir,
    }

    import_key = 'import'
    name_key = 'name'
    yaml_ext = ".yaml"

    def __init__(self, *args, **kwargs):
        self._loaded = []
        self._hosts = []
        self._time = time.strftime("%Y%m%d-%H%M%S")
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
        self._update_hosts()

    def load(self, stream):
        opt = yaml.load(stream)
        if opt is None:
            opt = {}
        merge_dict(self, opt)
        self._update_hosts()

    def get_trace_dir(self, **kwargs):
        base = self.get('tracedir', default_trace_dir)
        name = self.get('name', default_trace_name)
        name = "%s-%s" % (name, self._time)
        for k, v in kwargs.items():
            name = "%s-%s=%s" % (name, k, v)
        return join(base, name)

    def get_hosts(self):
        return self._hosts

    def _update_hosts(self):
        hosts = []
        roles = self.get('rolesdef', {})
        for k, v in roles.items():
            if isinstance(v, list):
                hosts += v
            elif isinstance(v, str):
                hosts.append(v)
            else:
                raise TypeError("invalid type for rolesdef %s" % k)
        self._hosts = list(OrderedDict.fromkeys(hosts))

