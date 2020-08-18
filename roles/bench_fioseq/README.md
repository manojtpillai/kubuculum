# Benchmark Role bench_fioseq

The bench_fioseq benchmark role evaluates the performance of a
storage backend on an fio sequential I/O workload.  It is a
distributed fio test.

## Description

### Prepare Phase

In the prepare phase, it starts *n* fio server pods using the
server_fio role.  The nodes where these fio server pods run can
be specified using a node label.

The size of the persistent volume claim can be specified using an
option (*bench_fioseq_pvcsz_req_gb*); if left unspecified, it is
calculated based on file size (*bench_fioseq_fsz_gb*) and number
of jobs (*bench_fioseq_njobs*). Note that number of jobs is per
fio server.

This benchmark does not run any workload as part of the prepare
phase.

### Run Phase

In the run phase of the benchmark, a client fio pod is created
that performs an fio sequential write test to the fio server pods
started in the prepare phase.  This is followed by an fio
sequential read test, which reads the data written in the write
test.

The benchmark drops caches in between the write and read test.
The caches that are dropped depends on settings in the
*util_dropcaches*.

## Example: Typical Parameters and Output

This section looks at a typical run of the bench_fioseq
benchmark. The options below serve to specify the
benchmark parameters. For simplicity, stats collection and
dropping caches are not enabled for this run.

```
# cat simple_inventory

[hosts]
localhost

[all:vars]

run_basedir="/root/mpillai/runs"
run_storageclass="ocs-storagecluster-ceph-rbd"
run_namespace="nm-kubuculum"

benchmark_role="bench_fioseq"
bench_fioseq_ninstances=3
bench_fioseq_fsz_gb=2
bench_fioseq_njobs=16
bench_fioseq_servernodelabel="node-role.kubernetes.io/worker=''"
```

The output directory from this run includes output from the roles
bench_fioseq and server_fio, as well as some files that capture
the nodes where different pods were scheduled:

```
# ls -l run_2020-08-18_1597754051/
total 12
drwxr-xr-x. 4 root root 104 Aug 18 08:45 bench_fioseq
-rw-r--r--. 1 root root 601 Aug 18 08:45 out.get_envinfo.txt
-rw-r--r--. 1 root root 541 Aug 18 08:45 out.server_fio.txt
-rw-r--r--. 1 root root 546 Aug 18 08:45 podlocations.bench_fioseq.txt
drwxr-xr-x. 5 root root 100 Aug 18 08:45 server_fio

# ls -l run_2020-08-18_1597754051/server_fio/
total 4
-rw-r--r--. 1 root root 1051 Aug 18 08:34 fioserver_statefulset.yaml
drwxr-xr-x. 2 root root   55 Aug 18 08:45 server-fio-0
drwxr-xr-x. 2 root root   55 Aug 18 08:45 server-fio-1
drwxr-xr-x. 2 root root   55 Aug 18 08:45 server-fio-2

# ls -l run_2020-08-18_1597754051/server_fio/server-fio-0/
total 16
-rw-r--r--. 1 root root  872 Aug 18 08:45 df_h.txt
-rw-r--r--. 1 root root 1340 Aug 18 08:45 ls_l.txt
-rw-r--r--. 1 root root 4153 Aug 18 08:45 mount.txt

# ls -l run_2020-08-18_1597754051/bench_fioseq/
total 8
-rw-r--r--. 1 root root 1875 Aug 18 08:42 fio_seqrd_job.yaml
-rw-r--r--. 1 root root 1929 Aug 18 08:35 fio_seqwr_job.yaml
drwxr-xr-x. 2 root root  105 Aug 18 08:45 seqrd_fio-bbc7t
drwxr-xr-x. 2 root root  105 Aug 18 08:42 seqwr_fio-gmx9r

# cat run_2020-08-18_1597754051/bench_fioseq/seqrd_fio-bbc7t/fio.seqrd.run.txt | grep -A 1 "All clients"
All clients: (groupid=0, jobs=48): err= 0: pid=0: Tue Aug 18 12:45:25 2020
   read: IOPS=4969, BW=621Mi (651M)(96.0GiB/158260msec)

# cat run_2020-08-18_1597754051/bench_fioseq/seqwr_fio-gmx9r/fio.seqwr.run.txt | grep -A 1 "All clients"
All clients: (groupid=0, jobs=48): err= 0: pid=0: Tue Aug 18 12:42:35 2020
  write: IOPS=1999, BW=250Mi (262M)(96.0GiB/393242msec)
```

The key metric for this benchmark is bandwidth/throughput. The
read tests is reporting 621 MB/s and the write test is reporting
250MB/s.  The storage class used in this run was
*ocs-storagecluster-ceph-rbd*, which uses 3-way replication.
This is an Openshift Container Storage (OCS) deployment, with 3
OCS nodes, each backed by 2Ti gp2 volumes, so the throughput per
node is capped at 250 MB/s. This is reflected in the sequential
write result. Reads can theoretically scale to the cumulative
throughput of the 3 nodes, hence the throughput there is higher.

