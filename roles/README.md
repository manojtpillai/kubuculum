# Roles in kubuculum

## Benchmark Roles

Benchmark roles in kubuculum are written to have a *prepare*
phase and a *run* phase. This maps directly to the way many
storage benchmarks, like ycsb, sysbench, pgbench etc., operate:
they have an *init/load* step, where a data set is created; this
is followed by a run phase where a representative workload is
applied against the previously created data set.

Benchmark roles are written to support the following actions:
1. prepare: corresponds to the load phase of many benchmarks.
1. run: corresponds to the run phase of many benchmarks.
1. gather: collect benchmark results and any related output.
1. cleanup: delete any resources created by the role.

It is upto the individual benchmark role to decide what tasks are
performed for each action. 

## CALM Roles

CALM stands for Controlled Ambient Load Mixing, a benchmarking
technique meant for environments where applications coexist with
noisy-neighbors. These roles aim to setup a steady background
load, so that a benchmark role can then be run with that load in
the background to gauge the impact of such noise. Currently, a
single CALM role, *calm_fioiops*, exists which creates multiple
fio instances, each generating steady IOPS using *--rate_iops*
option of fio.

## Stats Roles

Stats roles are written to collect CPU, memory, disk and other
statistics during the run.  Currently, a single stats role,
*stats_sysstat*, exists but that will likely change in future.

Stats collection is currently started at the start of a run; in
the future, that might be enhanced to give a choice of when to
start. For example, it might make sense to start stats collection
at the beginning of the run phase of the benchmark.


