# kubuculum
Benchmarking tool for predicting I/O performance of Kubernetes clusters.

[It's not a word, but it could be. BTW, orbuculum is a crystal orb, or
crystal ball]

## Quick Start

### Prerequisites

This tool is run on a system that has kubectl set up to control a
kubernetes cluster. The prerequisites for running the tool are:
- A kubernetes cluster up and running.
- The kubernetes cluster has a default StorageClass. This will be
used by the tool for dynamically provisioning storage.
- The system running the tool should have kubectl set up to
work against said kubernetes cluster.
- The system running the tool should have ansible installed.

### Get Started

```
git clone https://github.com/manojtpillai/kubuculum.git
cd kubuculum
ansible-playbook -i inventory perform_benchrun.yml
```

This will run an fio test, against the default StorageClass of
your kubernetes cluster, and collect results of the run in a
timestamped directory /tmp/run_\<timestamp\>.

The tool creates the k8s resources that it needs, e.g. pods, in a
separate namespace, nm-kubuculum by default.

It is easiest to control your benchmark runs by supplying
variables and values in the inventory file. The sample inventory
file has most of the variables you'll need listed, but commented
out. So typically, it is just a matter of uncommenting the ones
you need.

## Overview

### Goals

This tool is meant as much for experimenting with benchmarking
techniques for platforms like k8s, as it is for evaluating
storage performance of a cluster.  It came about from a feeling
that performance benchmarking methodology for such platforms,
where many performance critical applications run concurrently,
still needs refining.

### Structure

The tool is evolving. It is written as a collection of ansible
roles and a few ansible playbooks that tie these roles together.
The major role types are:

- benchmark roles: The reason we are here. 
- CALM roles: These serve to set up a background load for benchmarking.
- stats roles: These gather various statistics to help analyze
benchmark runs.

By convention, the role name prefix (e.g. bench_ ) is chosen to
denote the type of role.

The playbooks expect each type of role to support certain
"actions" like start, stop, that make sense for that type of
role.  Each action generally maps to an ansible playlist to
accomplish that action.

### Benchmark Roles

Many storage benchmarks, e.g. ycsb, sysbench, have a load
phase, where a data set is created, and a run phase, where a
representative workload is executed against the previously
created data set. It is useful for various reasons to have
benchmark roles that maintain this separation.

Benchmark roles are written to support the following actions:
1. prepare: corresponds to the load phase of many benchmarks.
1. run: corresponds to the run phase of many benchmarks.
1. gather: collect benchmark results and any related output.
1. cleanup: delete any resources created by the role.

It is upto the individual benchmark role to decide what tasks are
performed for each action. 

### CALM Roles

CALM stands for Controlled Ambient Load Mixing, a benchmarking
technique meant for environments where applications coexist with
noisy-neighbors. These roles generally setup a steady background
load, so that a benchmark role can then be run with that load in
the background to gauge the impact of such noise.


CALM roles are written to support the following actions:
1. start:
1. ensure_ready: will wait until initialization has completed
and the steady load is being generated.
1. gather: collect output for the calm role.
1. stop:

### Stats Roles

These roles collect CPU, memory, disk and other statistics during
the run.  Currently, a single stats role exists: stats_sysstat,
but that will likely change in future. stats_systat uses a
daemonset to start privileged pods on each of a subset of the
kubernetes nodes. The pods collect iostat, top (thread and
process level) and sar output from the nodes.

stats roles are written to support the following actions:
1. start
1. gather
1. stop

### Playbooks

The main playbook for executing benchmark runs is
perform_benchrun.yml. The code is simple and readable, and
probably does not need more explanation.

The playbook has an option, enabled by default, to drop caches
between benchmark prepare and benchmark run phases.  Currently,
this is the only place where caches are dropped. The ability to
drop caches at arbitrary points in a benchmark's execution has not
yet been implemented. The drop-caches functionality is currently
only implemented for rook-ceph because that is the only storage
solution this tool has been used with.

## Additional Details

Please refer to the documentation of individual roles for more
details.

