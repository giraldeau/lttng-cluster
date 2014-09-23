import copy
from fabric.api import task, run, local, parallel, env, get
from fabric.tasks import execute
from os.path import dirname, join
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

env.tracename = "default"

def run_bg(cmd):
    run('nohup %s > cmd.out 2> cmd.err < /dev/null &' % (cmd), pty=False)

@parallel
def trace_start():
    run("lttng destroy -a")
    run("rm -rf ~/lttng-traces/*")  # FIXME: trace to a tmp directory
    ctx = { "host": env.host, "tracename": env.tracename }
    run("lttng create peer-%(host)s -o ~/lttng-traces/%(tracename)s" % ctx)
    run("lttng enable-channel k -k --subbuf-size 16384 --num-subbuf 4096")
    ev_string = ",".join(default_kernel_events)
    run("lttng enable-event -k -c k %s" % ev_string)
    run("lttng enable-event -k -c k -a --syscall")
    run("lttng add-context -k -c k -t tid -t procname")
    run("lttng start")

@parallel
def trace_stop():
    run("lttng stop")
    run("lttng destroy -a")

# TODO: fix this command
@task
def trace_fetch():
    print("fetch trace %s" % (env.tracename))
    # get("/home/ubuntu/lttng-traces/%s/*" % (env.tracename), env.dest + "/%(host)s/%(path)s")
    # run("rm -rf ~/lttng-traces/%s" % (env.tracename))

def merge_dict(dst, src):
    for k in src.keys():
        if (isinstance(dst.get(k, None), dict) and
            isinstance(src.get(k, None), dict)):
            merge_dict(dst[k], src[k])
        else:
            dst[k] = src[k]

class TraceRunner(object):
    '''Run an experiment under tracing'''
    def __init__(self, exp):
        self.exp = exp
    def run(self):
        self.exp.before()
        execute(trace_start)
        self.exp.action()
        execute(trace_stop)
        self.exp.after()
        execute(trace_fetch)

class TraceExperiment(object):
    '''Experiment definition'''

    def before(self):
        print("before")
    def after(self):
        print("after")
    def action(self):
        print("action")

class TraceExperimentOptions(dict):

    default_options = {
        'experiment': None,
        'username': default_username,
        'events': {
            'kernel': default_kernel_events,
            'userspace': default_userspace_events
        },
        'rolesdef': {},
        'params': {},
    }

    import_key = 'import'

    def __init__(self, *args, **kwargs):
        self._loaded = []
        super(TraceExperimentOptions, self).__init__(*args, **kwargs)

    def load_path(self, path):
        with open(path) as f:
            opt = yaml.load(f)
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
            merge_dict(self, opt)

    def load(self, stream):
        opt = yaml.load(stream)
        merge_dict(self, opt)

class TraceExperimentSimple(TraceExperiment):
    def __init__(self, cmd='date'):
        self.cmd = cmd
        super(TraceExperimentSimple, self).__init__()
    def action(self):
        local(self.cmd)
