# kubuculum
Storage performance benchmarking in Kubernetes.

[It's not a word, but it could be. BTW, orbuculum is a crystal orb, or
crystal ball]

## Introduction

kubuculum is a tool for running fio and other benchmarks in a k8s
environment.  One of its main goals is to support troubleshooting
of performance problems across organizational boundaries. A
typical scenario: a user outside your organization is running
your storage solution and reporting performance issues; with
kubuculum, you can have them run specific benchmarks and share
benchmark output and system statistics with you for analysis. To
this end:

- The tool is written to be very simple to use. It should be
possible to get going with it in a few minutes.

- Output from a run is collected into a timestamped directory.
Users can then *tar/zip* this directory and share it, e.g. by
attaching it to a defect tracking tool.

- Output from a run includes not only output of the benchmark but
also other information that is useful in validating the run.  For
example, the fio benchmarks in kubuculum store not only fio
output, but also *ls -l* output of the data directory that shows
number of files created and their sizes. 

- kubuculum can also collect system statistics (*iostat, sar,
top*) in text format from specified nodes into the run output
directory to facilitate analysis of the run.

Another goal of the tool is to support experimentation with
benchmarking techniques for noisy-neighbor environments like k8s.
In particular, the tool currently provides basic support for a
technique called Controlled Ambient Load Mixing (CALM), where a
background load can be applied during benchmark runs to simulate
noisy neighbors.

## Scope

Testing during development has been limited to Red Hat's
Openshift. Known usage of the tool has also been on Openshift.


## Getting Started

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
Passwordless ssh to localhost should work [try a simple command 
like '*ssh localhost date*' to test that it does].

In addition, the access policy for the kubernetes cluster should
allow the kubectl commands issued by the tool: create a
namespace, list nodes, create statefulsets and pods, to list a
few. In this context, note that:

- kubuculum has an option to collect system stats (*iostat, sar,
top*) during runs. This option is disabled by default; when enabled,
it creates a daemonset of privileged pods.

- kubuculum has an option to drop linux kernel caches at points
during the benchmark runs. This option is disabled by default;
when enabled, it creates a daemonset of privileged pods with root
access, on specified nodes, that execute the *sysctl
vm.drop_caches* command.

### Quick Start

```
git clone https://github.com/manojtpillai/kubuculum.git
cd kubuculum
ansible-playbook -i inventory perform_benchrun.yml
```

Based on settings in the inventory file, this will run an fio
test, against the default StorageClass of your kubernetes
cluster, and collect results of the run in a timestamped
directory */tmp/run_\<timestamp\>*.  A quick examination of this
directory should give a sense of how the tool organizes output.

The tool creates the k8s resources that it needs, e.g. pods, in a
separate namespace, *nm-kubuculum* by default. In case of a failed
run, use the cleanup playbook:

```
ansible-playbook -i inventory cleanup.yml
```

### A More Realistic Run

The default values for the run parameters are appropriate for
quickly trying things out; for actual performance bencmarking you
should expect to provide more reasonable values for them.  It is
easiest to control your benchmark runs by supplying variables and
values in the inventory file. The sample inventory file has most
of the variables you'll need listed, but commented out. 

Below is the inventory file modified for a typical run of the
bench_fiorand benchmark, which runs an fio random I/O workload:

```
[hosts]
localhost

[all:vars]

run_basedir="/root/mpillai/runs"
run_storageclass="gp2"
run_namespace="nm-kubuculum"

stats_enabled=True
stats_role="stats_sysstat"
dropcaches_postprepare=True
allow_osrootpods=True

os_rootpods_nodelabel="node-role.kubernetes.io/worker=''"
stats_sysstat_nodelabel="node-role.kubernetes.io/worker=''"

benchmark_role="bench_fiorand"
bench_fiorand_ninstances=1
bench_fiorand_fsz_gb=16
bench_fiorand_njobs=4
bench_fiorand_bs_kb=8
bench_fiorand_run_sec=120
bench_fiorand_servernodelabel="node-role.kubernetes.io/worker=''"
```

This run enables stats collection and dropping of OS caches on
k8s worker nodes. It also provides more reasonable parameters for
the fio test. 

The output is collected in the bench_fiorand sub-directory in the
run output directory. The key metric for this benchmark is IOPS,
and the relevant output from the run is shown below:

```
# cat run_2020-08-12_1597246044/bench_fiorand/fio-pjkt4/fio.randread.run.txt | grep -A 1 "All clients"
All clients: (groupid=0, jobs=4): err= 0: pid=0: Wed Aug 12 15:40:00 2020
   read: IOPS=3025, BW=23.6Mi (24.8M)(2837MiB/120012msec)

# cat run_2020-08-12_1597246044/bench_fiorand/fio-pjkt4/fio.randwrite.run.txt | grep -A 1 "All clients"
All clients: (groupid=0, jobs=4): err= 0: pid=0: Wed Aug 12 15:42:05 2020
  write: IOPS=3025, BW=23.6Mi (24.8M)(2837MiB/120022msec)
```

## Architecture

The tool is evolving. It is written as a collection of ansible
roles and a few ansible playbooks that tie these roles together.
The major role types are:

- benchmark roles: The reason we are here. 
- CALM roles: These serve to set up a background load for benchmarking.
- stats roles: These gather various statistics to help analyze
benchmark runs.

By convention, the role name prefix (e.g. *bench_* ) is chosen to
denote the type of role.

## Additional Details

Please refer to the documentation of individual roles for more
details.

