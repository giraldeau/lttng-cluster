lttng-cluster
=============

Setup and trace a cluster using LTTng

## Scope ##

* Start and stop tracing in parallel (DONE)
* Execute a command remotely under tracing (DONE)
* Collect traces either live after tracing (DONE)
* Install LTTng (stable, devel, addons, etc.) (see scripts)
* Check if tracer is available (TODO)
* Start/stop/restart lttng-sessiond (TODO)

## Usage ##

Requirements:
 * fabric
 * python-yaml

Install requirements for Ubuntu 14.04:
`sudo apt-get install fabric python-yaml`

Install command:
`sudo python setup.py install`

Or run it from the repo by sourcing `env.sh`.

You need a recipe file to set variables of the experiment and define commands
to executes under tracing. The recipe is a YAML file. Common settings can be
imported. If a setting is redefined in a file, it overrides the imported
setting.

The following settings are available:

 * username: SSH user to connect to the remote hosts. Public key must be configured for password less connexion. (string)
 * events: (only kernel events are supported for now)
   ** kernel: list of kernel events to enable (list)
 * import: yaml file to import (without .yaml, must be in the same directory) (string)
 * roledefs: named group of machines. (dict)
 * execute: commands to executes under tracing (list of dict)
   ** command: shell command, where %(key)s are substituted at runtime with the powerset of parameters (see parameters below)
   ** roles: groups to run the command on (list)
   ** method: either ~~background~~ (non-blocking) or ~~foreground~~ (blocking), default foreground. If a command is spawned in the background, make sure to include a command to terminate the task at the end, because they are not terminated automatically.
 * parameters: define parameter values to be used in commands. One trace will be generated for each combinations of parameters. The trace directory includes parameters values. (dict)

See files `recipe/base.yaml` and `recipe/sleep.yaml` for examples.

The following command runs the experiment:

`lttng-cluster recipe trace recipe/sleep.yaml`

And produces the following traces under `~/lttng-traces/` of the machine where
the command is launched:
`
sleep-20141130-184830-delay=1
sleep-20141130-184830-delay=2
sleep-20141130-184830-delay=3
`

Happy hacking!

