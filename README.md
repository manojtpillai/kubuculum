# kubuculum
Benchmarking tool for predicting I/O performance of Kubernetes clusters.

[It's not a word, but it could be. BTW, orbuculum is a crystal orb, or
crystal ball]

## Quick Start

```
git clone https://github.com/manojtpillai/kubuculum.git
cd kubuculum
ansible -i inventory perform_benchrun.yml
```

This should run an fio test, against the default storage class of
your kubernetes cluster, and collect results of the run in a
timestamped directory /tmp/run_<timestamp>.

It is easiest to control your benchmark runs by editing variables
in the inventory file.


## Overview

The tool is evolving. It is written as a collection of simple
roles and a few playbooks that tie these together. The major role
types are:

- benchmark roles: the reason we are here
- stats roles: gather various statistics to help analyze benchmark run
- calm roles: set up a background load for benchmarking

### Benchmark Roles

Many storage benchmarks, e.g. ycsb and sysbench, have a load
phase where a data set is created, and a run phase where a representative
workload is executed against the previously created data set. It
is useful for various reasons to be able to separate the load and
run phases.

Benchmark roles are written to support the following actions:
1. prepare
1. run
1. gather
1. cleanup

It is upto the individual benchmark role to decide what tasks are
performed for each action.

### CALM Roles

CALM stands for Controller Ambient Load Mixing, a benchmarking
technique that attempts to simulate the fact that in a cluster
there will be noisy neighbors running concurrently with your
aplication, and to help analyze application performance in the
presence of such noise.

A CALM role is designed to inject a steady load according to
specified parameters.

CALM roles are written to have the following actions:
1. start
1. ensure_ready
1. gather
1. stop

