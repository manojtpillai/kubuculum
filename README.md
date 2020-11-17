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

- The initial implementation was in ansible. This version is still
accessible via tag v0.1

- The tool has been rewritten in python. It has gained better
capabilities in this rewrite; maybe most significant is the ability to
specify a batch of runs in a single input file. However, not all
benchmarks available in the ansible version have been rewritten yet.

## Getting Started

### Prerequisites

kubuculum is run on a system that has kubectl set up to control a
kubernetes cluster. The prerequisites for running the tool are:

- python3 (>= 3.6) on the system running the tool. It also requires
additional packages. The following should suffice:
  - pip3 install pyyaml
  - pip3 install jinja2

- A kubernetes cluster up and running. The system running the tool
should have kubectl set up to work against said kubernetes cluster.
Since the benchmarks are storage focused, the kubernetes cluster
should either have a default storageclass, or a storageclass should be
specified in the input file (see below).

In addition, the access policy for the kubernetes cluster should allow
the kubectl commands issued by the tool: create a namespace, list
nodes, create statefulsets and pods, to list a few. In this context,
note the following:

- kubuculum has an option to collect system stats (*iostat, sar, top*)
during runs. When enabled, this creates a daemonset of privileged pods
on all/selected nodes.

- kubuculum has an option to drop linux kernel caches at points during
the benchmark runs. When enabled, this creates a daemonset of
privileged pods with root access, on all/selected nodes, that execute
the *sysctl vm.drop_caches* command.

### Quick Start

```
git clone https://github.com/manojtpillai/kubuculum.git
cd kubuculum
./perform_runs.py -i sample_input/dummy.yaml
```

Based on settings in the dummy.yaml input file, this will run a dummy
benchmark (just sleeps for a specified duration).  Output goes to a
timestamped directory */tmp/run_\<timestamp\>*.  A quick examination
of this directory should give a sense of how the tool organizes
output.

The tool creates the k8s resources that it needs, e.g. pods, in a
separate namespace, *nm-kubuculum* by default. In case of a failed
run, use the cleanup script:

```
./cleanup.py
```

### Beyond the Trivial

The examples in the *sample_input* directory highlight the
capabilities of the tool, and the input file syntax to use to exercise
them.

For more details on the individual packages/modules look in the
corresponding directory. Below is the output of the *tree* command for
*kubuculum/benchmarks/fio_random*:

```
.
├── defaults.yaml
├── fio_random.py
└── templates
    ├── fio_random.prep.job.j2
    └── fio_random.run.job.j2
```

The *defaults.yaml* file has the options that are available for this
particular benchmark. The input file only needs to specify those
options that need to be overridden. 

Generally speaking, the data set size parameters in the defaults are
chosen to be unrealistically low. This is to allow new users to try
out runs that complete quickly. For useful runs, it is expected that
users will provide better values. Specifically for the *fio_random*
benchmark, the user would specify more appropriate values for
*filesize_gb*, *ninstances* and *numjobs* options.

## Additional Details

- **Storage backends:** The tool uses k8s features for allocating
storage, so it mostly doesn't need to be aware of specific storage
backends. The *openshift_storage* module, written for Openshift
Container Storage (OCS) is an example of how specific features can be
incorporated into the tool: this module implements *drop_caches*
functionality for OCS.

- **Statistics:** The tool currently has one module, *sysstat*, for
natively collecting stats during runs. But it is designed to allow
other ways of collecting stats. There is also a module,
*stats_splitter*, that allows multiple stats collection modules to be
active concurrently.

