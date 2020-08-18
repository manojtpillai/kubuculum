# Benchmark Role bench_fiorand

The bench_fiorand benchmark role evaluates the performance of a
storage backend on an fio random I/O workload.  It is a
distributed fio test.

## Description

### Prepare Phase

In the prepare phase, it starts *n* fio server pods using the
server_fio role.  The nodes where there fio server pods run can
be specified using a node label.

When the fio server pods are ready, a client fio pod initiates
the creation of a data set using an fio sequential write job. The
random I/O workload in the run phase is run against this data
set.

The size of the persistent volume claim can be specified using an
option (*bench_fiorand_pvcsz_req_gb*); if left unspecified, it is
calculated based on file size (*bench_fiorand_fsz_gb*) and number
of jobs (*bench_fiorand_njobs*). Note that file size and number
of jobs is per fio server.

### Run Phase

In the run phase of the benchmark, a client fio pod first
initiates an fio random read test on the data set created in the
prepare phase. This is followed by an fio random write test.
There are options to skip the random read or the random write
test, if only one of these is desired.

### Dropping Caches

Currently, bench_fiorand does not explicitly drop caches.
kubuculum has an option (*dopcaches_postprepare*) to drop caches
between the prepare and run phases. At present, this is
sufficient for this benchmark.

## Example: Typical Parameters and Output

This section looks at a typical run of the bench_fiorand
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

benchmark_role="bench_fiorand"
bench_fiorand_ninstances=3
bench_fiorand_fsz_gb=32
bench_fiorand_njobs=4
bench_fiorand_bs_kb=8
bench_fiorand_run_sec=240
bench_fiorand_servernodelabel="node-role.kubernetes.io/worker=''"

# ansible-playbook -i simple_inventory perform_benchrun.yml
```

The output directory from this run includes output from the roles
bench_fiorand and server_fio, as well as some files that capture
the nodes where different pods were scheduled:

```
# ls -l run_2020-08-18_1597731688/
total 12
drwxr-xr-x. 4 root root  95 Aug 18 02:57 bench_fiorand
-rw-r--r--. 1 root root 273 Aug 18 02:57 out.bench_fiorand.txt
-rw-r--r--. 1 root root 587 Aug 18 02:57 out.get_envinfo.txt
-rw-r--r--. 1 root root 541 Aug 18 02:57 out.server_fio.txt
drwxr-xr-x. 5 root root 100 Aug 18 02:57 server_fio

# ls -l run_2020-08-18_1597731688/server_fio/
total 4
-rw-r--r--. 1 root root 1052 Aug 18 02:21 fioserver_statefulset.yaml
drwxr-xr-x. 2 root root   55 Aug 18 02:57 server-fio-0
drwxr-xr-x. 2 root root   55 Aug 18 02:57 server-fio-1
drwxr-xr-x. 2 root root   55 Aug 18 02:57 server-fio-2

# ls -l run_2020-08-18_1597731688/server_fio/server-fio-0/
total 16
-rw-r--r--. 1 root root  872 Aug 18 02:57 df_h.txt
-rw-r--r--. 1 root root  404 Aug 18 02:57 ls_l.txt
-rw-r--r--. 1 root root 4153 Aug 18 02:57 mount.txt

# cat run_2020-08-18_1597731688/server_fio/server-fio-0/ls_l.txt 
total 134217808
-rw-------. 1 1000600000 1000600000 34359738368 Aug 18 06:57 10.131.0.34.f.0.0
-rw-------. 1 1000600000 1000600000 34359738368 Aug 18 06:57 10.131.0.34.f.1.0
-rw-------. 1 1000600000 1000600000 34359738368 Aug 18 06:57 10.131.0.34.f.2.0
-rw-------. 1 1000600000 1000600000 34359738368 Aug 18 06:57 10.131.0.34.f.3.0
drwxrws---. 2 root       1000600000       16384 Aug 18 06:21 lost+found

# ls -l run_2020-08-18_1597731688/bench_fiorand/
total 8
-rw-r--r--. 1 root root 1950 Aug 18 02:22 fioprep_job.yaml
-rw-r--r--. 1 root root 2972 Aug 18 02:49 fiorun_job.yaml
drwxr-xr-x. 2 root root  169 Aug 18 02:57 fio-tww9n
drwxr-xr-x. 2 root root  110 Aug 18 02:48 prepare_fio-sw9dn

# cat run_2020-08-18_1597731688/bench_fiorand/fio-tww9n/fio.randread.run.txt | grep -A 1 "All clients"
All clients: (groupid=0, jobs=12): err= 0: pid=0: Tue Aug 18 06:53:30 2020
   read: IOPS=14.8k, BW=116Mi (121M)(27.1GiB/240143msec)

# cat run_2020-08-18_1597731688/bench_fiorand/fio-tww9n/fio.randwrite.run.txt | grep -A 1 "All clients"
All clients: (groupid=0, jobs=12): err= 0: pid=0: Tue Aug 18 06:57:36 2020
  write: IOPS=4512, BW=35.3Mi (36.0M)(8468MiB/240176msec)
```

The storage class used in this run was
*ocs-storagecluster-ceph-rbd*, which uses 3-way replication.
Hence, the write IOPS is expected to be lower compared to read.

