# kubuculum
Benchmarking tool for predicting I/O performance of Kubernetes clusters.

[It's not a word, but it could be. BTW, orbuculum is a crystal orb, or
crystal ball]

## Introduction

kubuculum is a tool for running fio and other benchmarks in a k8s
environment.  One of its main goals is to support troubleshooting
of performance problems across organizational boundaries. A
typical scenario is a user outside your organization who is not
an expert in your storage solution, running it and reporting
performance issues; with kubuculum, you can have them run
specific benchmarks and share with you benchmark output and
statistics from the run for analysis. To this end:

- The tool is written to be very simple to use. It should be
possible to get it up and running in under 10 minutes.

- Output from a run is collected into a timestamped directory.
This directory can be tarred and shared, e.g. by attaching it to
a defect tracking tool.

- Output from a run includes not only output of the benchmark but
also other information that is needed to validate that the run.
For example, the fio benchmarks in kubuculum store not only fio
output, but also ls -l output of the data directory that shows
number of files created and their sizes. Simiilarly, mongodb runs
include output of commands like replication status and db
settings.

- kubuculum can also collect system stats (iostat, sar, top) from
specified nodes in text format into the run output directory, to
facilitate analysis of the run.

## Quick Start

### Prerequisites

This tool is run on a system that has kubectl set up to control a
kubernetes cluster. The prerequisites for running the tool are:

- A kubernetes cluster up and running.

- The system running the tool should have kubectl set up to
work against said kubernetes cluster.

- The kubernetes cluster should have a default StorageClass. This
is used by the tool for dynamically provisioning storage.
Alternatively, you can specify a StorageClass to use; see below.

- The system running the tool should have ansible installed.
passwordless ssh to localhost should work [try a simple command 
like 'ssh localhost date' to test that it does].

In addition, the access policy for the kubernetes cluster should
should allow the kubectl commands issued by the tool: create a
namespace, list nodes, create statefulsets and pods, to list a
few. In this context, note that:

- kubuculum has an option to collect system stats (iostat, sar,
top) during runs. This option is disabled by default; if enabled,
it needs to create a daemonset of privileged pods.

- kubuculum has an option to drop linux kernel caches at points
in the benchmark runs. This option is disabled by default; if
enabled, it needs to create a daemonset of privileged pods with
root access that execute vm.drop_caches command on specified
nodes.


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

For example, you can specify results directory, and the 
StorageClass for dynamically provisioning storage using the 
variables below:

```
run_basedir="/home/mpillai/runs" 
run_storageclass="ocs-storagecluster-ceph-rbd"
```


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

