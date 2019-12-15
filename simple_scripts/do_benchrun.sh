#! /bin/bash

set -e 
ME=`basename $0`

# parameters section: BEGIN

# output files are collected into a sub-dir here
DEST_DIR="."

# miscellaneous output file for run
RUNOUT="out.run.txt"

# monitoring enabled/disabled
MON_ENABLED="n"
# MON_ENABLED="y"

# namespace for sysstat pods; must exist
# should match the namespace specified in daemonset yaml
NM_SYSSTAT="kube-system"

# namespace for app pods; must exist
NM_STORAPP="nm-storapp"

# yaml file for MON pods
MONYAML_PATH="./daemonset_sysstat.yaml"
MONPOD_LABEL="name=sysstat-collection"
MONOUT="/data"

# yaml file for application, as a k8s job
# expects it in a specific format
JOBYAML_PATH="./fio_job.yaml"
# JOBYAML_PATH="./ycsb_job.yaml"
JOBPOD_LABEL="type=benchmark-pod"
PODOUT="/benchout"

# parameters section: END

function print_usage
{
    echo "Usage: $ME {start|cleanup}"
}

function setup_rundir
{
    ts=`date +"%F_%s"`
    run_dir="${DEST_DIR}/run_${ts}"
    mkdir ${run_dir}
}

function do_cleanup
{
    # cleanup application pods, pvcs and namespaces
    kubectl delete -f ${JOBYAML_PATH} --namespace=${NM_STORAPP}

    # cleanup monitoring pods 
    if [ "$MON_ENABLED" = "y" ]; then
	kubectl delete -f ${MONYAML_PATH}
    fi
}

function force_cleanup
{
    set +e
    do_cleanup
}

## process command-line

if [ "$1" = "cleanup" ]; then
    force_cleanup
    exit 0
elif [ "$1" != "start" ]; then
    print_usage
    exit 1
fi

## set up run directory run_dir

setup_rundir

echo "output for run: " > ${run_dir}/${RUNOUT}
echo >> ${run_dir}/${RUNOUT}

echo "nodes:" >> ${run_dir}/${RUNOUT}
kubectl get nodes >> ${run_dir}/${RUNOUT}
echo >> ${run_dir}/${RUNOUT}

## 

## set up monitoring

if [ "$MON_ENABLED" = "y" ]; then

    # create sysstat pod on each node
    kubectl create -f ${MONYAML_PATH}
    sleep 20 # TODO

    # check pods created
    echo "sysstat pods:" >> ${run_dir}/${RUNOUT}
    kubectl get pods -o wide -l ${MONPOD_LABEL} --namespace=${NM_SYSSTAT} >> ${run_dir}/${RUNOUT}
    echo >> ${run_dir}/${RUNOUT}

fi

##

## create application pods

# create app pod that uses pvc 
kubectl create -f ${JOBYAML_PATH} --namespace=${NM_STORAPP}

## 

## wait for application pods to complete
# check whether pod is in running state
# this means initContainer has completed, and therfore job done
app_pod_list=`kubectl get pods -l ${JOBPOD_LABEL} --namespace=${NM_STORAPP} --no-headers | awk '{print $1}'`
for pod in ${app_pod_list}; do
    kubectl wait --for=condition=Ready  pod/${pod} --namespace=${NM_STORAPP} --timeout=3600s
done
##

## copy application results to run_dir
app_pod_list=`kubectl get pods -l ${JOBPOD_LABEL} --namespace=${NM_STORAPP} --no-headers | awk '{print $1}'`
for pod in ${app_pod_list}; do
    mkdir ${run_dir}/${pod}
    kubectl cp ${NM_STORAPP}/${pod}:${PODOUT} ${run_dir}/${pod}
done

# get node where pod was running
echo "application pod:" >> ${run_dir}/${RUNOUT}
kubectl get pods -o wide -l ${JOBPOD_LABEL} --namespace=${NM_STORAPP} >> ${run_dir}/${RUNOUT}
echo >> ${run_dir}/${RUNOUT}
##

## gather stats

if [ "$MON_ENABLED" = "y" ]; then

    # copy stats files from sysstat pods to run_dir
    pod_list=`kubectl get pods -l ${MONPOD_LABEL} --namespace=${NM_SYSSTAT} --no-headers | awk '{print $1}'`
    for pod in ${pod_list}; do
	mkdir ${run_dir}/${pod}
	kubectl cp ${NM_SYSSTAT}/${pod}:${MONOUT} ${run_dir}/${pod}
    done

fi

##

## clean up
do_cleanup
##

