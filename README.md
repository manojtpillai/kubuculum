# kubuculum
Benchmarking tool for predicting I/O performance of Kubernetes clusters.

[It's not a word, but it could be. BTW, orbuculum is a crystal orb, or
crystal ball]

## Quick Start

### Prerequisites

- You have a kubernetes cluster up and running.
- The system where you are running the tool has kubectl set up to
work against this kubernetes cluster.
- You should have ansible installed on the system where you are
running the tool.

### Get Started

```
git clone https://github.com/manojtpillai/kubuculum.git
cd kubuculum
ansible-playbook -i inventory perform_benchrun.yml
```

This should run an fio test, against the default storage class of
your kubernetes cluster, and collect results of the run in a
timestamped directory /tmp/run_\<timestamp\>.

The tool creates the k8s resources, e.g. pods, that it needs in a
separate namespace, nm-kubuculum by default.

It is easiest to control your benchmark runs by editing variables
in the inventory file.


## Overview

The tool is evolving. It is written as a collection of simple
ansible roles and a few ansible playbooks that tie these roles
together. The major role types are:

- benchmark roles: the reason we are here
- calm roles: set up a background load for benchmarking
- stats roles: gather various statistics to help analyze benchmark run

The playbooks generally assume that each type of role supports
certain "actions" like start, stop, that make sense for that type
of role. Generally, each action maps to an ansible playlist that
has a sequence of tasks to accomplish that action.

### Benchmark Roles

Many storage benchmarks, e.g. ycsb and sysbench, have a load
phase, where a data set is created, and a run phase, where a
representative workload is executed against the previously
created data set. It is useful for various reasons to have
benchmark roles that maintain this separation.

Benchmark roles are written to support the following actions:
1. prepare: corresponds to the load phase of many benchmarks.
1. run: corresponds to the run phase of many benchmarks.
1. gather: collect benchmark results and any related output.
1. cleanup: no explanation needed.

It is upto the individual benchmark role to decide what tasks are
performed for each action. A benchmark role also can decide to do
nothing on a particular action.

### CALM Roles

CALM stands for Controlled Ambient Load Mixing, a benchmarking
technique meant for environments where applications coexist with
noisy-neighbors. These roles generally setup a steady background
load, and a benchmark role can then be run with that load in the
background to gauge the impact of such noise.


CALM roles are written to support the following actions:
1. start:
1. ensure_ready: will wait until initialization has completed
and the steady load is being generated.
1. gather: collect output for the calm role.
1. stop:

### Statistics Roles

These roles collect CPU, memory, disk statistics during the run.
Currently, a single stats role exists: stats_sysstat. But that
will likely change in future. stats_systat uses a daemonset to
start pods on each of a subset of the kubernetes nodes. The pods
collect iostat, top (thread and proc) and sar output from the
nodes.

stats roles are written to support the following actions:
1. start
1. gather
1. stop

