# kubuculum
Storage performance benchmarking in Kubernetes.

The name kubuculum comes from orbuculum, which means crystal ball.

## Introduction

kubuculum is a tool for running fio and other benchmarks in a k8s
environment.  One of its goals is to support troubleshooting of
performance problems across organizational boundaries, when users
report performance issues.  You can have them run specific benchmarks
and share benchmark output and system statistics with you for
analysis.  Below are some of the characteristics of the tool that are
suited for such workflows:

- The tool is written to be very simple to get started with. It should
be possible for a new user to get going with it in a few minutes.

- Output from a run is collected into a timestamped directory.
Users can then *tar/zip* this directory and share it, e.g. by
attaching it to a defect tracking tool.

- Output from a run includes not only output of the benchmark but
also other information that is useful in validating the run.  As
an example, the fio benchmarks in kubuculum store not only fio
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
noisy neighbors and their impact.

## Scope

Testing during development has been limited to Red Hat's
Openshift. Known usage of the tool has also been on Openshift.

## Versions

The initial implementation was in ansible, followed by a python
rewrite. The python version has better capabilities, but not all
benchmarks and features have been ported to it at this time.

## Getting Started

### Prerequisites

kubuculum is run on a system that has kubectl set up to control a
kubernetes cluster. The prerequisites for running the tool are:

- A kubernetes cluster up and running.

- The system running the tool should have kubectl set up to
work against said kubernetes cluster.

- The kubernetes cluster should have a default StorageClass. This
is used by the tool for dynamically provisioning storage.
Alternatively, you can specify a StorageClass to use; see below.

- The system running the tool should have python3 (>= 3.6) and
the following modules installed.
  - pip3 install pyyaml
  - pip3 install jinja2

In addition, the access policy for the kubernetes cluster should
allow the kubectl commands issued by the tool: create a
namespace, list nodes, create statefulsets and pods, to list a
few. In this context, note that:

- kubuculum has an option to collect system stats (*iostat, sar,
top*) during runs. This option is disabled by default; when
enabled, it creates a daemonset of privileged pods on
all/selected nodes.

- kubuculum has an option to drop linux kernel caches at points
during the benchmark runs. This option is disabled by default;
when enabled, it creates a daemonset of privileged pods with root
access, on selected nodes, that execute the *sysctl
vm.drop_caches* command.

### Quick Start

```
git clone https://github.com/manojtpillai/kubuculum.git
cd kubuculum
./perform_runs.py -i sample_input/dummy.yaml
```

Based on settings in the dummy.yaml input file, this will run a dummy
benchmark (just sleeps for a specified suration).  Output goes to a
timestamped directory */tmp/run_\<timestamp\>*.  A quick examination
of this directory should give a sense of how the tool organizes
output.

The tool creates the k8s resources that it needs, e.g. pods, in a
separate namespace, *nm-kubuculum* by default. In case of a failed
run, use the cleanup script:

```
./cleanup.py
```
