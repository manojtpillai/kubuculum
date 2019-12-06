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

# namespace for app pods; created by script
NM_STORAPP="nm-storapp"

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

## set up run directory run_dir

setup_rundir

echo "output for run: " > ${run_dir}/${RUNOUT}
echo >> ${run_dir}/${RUNOUT}

kubectl get nodes >> ${run_dir}/${RUNOUT}
echo >> ${run_dir}/${RUNOUT}

## 

## set up monitoring

if [ "$MON_ENABLED" = "y" ]; then

    # create sysstat pod on each node
    kubectl create -f daemonset_sysstat.yaml
    sleep 20

    # check pods created
    kubectl get pods -o wide --namespace=${NM_SYSSTAT} >> ${run_dir}/${RUNOUT}
    echo >> ${run_dir}/${RUNOUT}

fi

##

## create application pods

# setup namespace for application
kubectl create namespace ${NM_STORAPP}

# create pvc
kubectl create -f storapp_pvc.yaml --namespace=${NM_STORAPP}

# create app pod that uses pvc 
kubectl create -f fio_job.yaml --namespace=${NM_STORAPP}

## 

## wait for application pods to complete
# use: kubectl wait command
sleep 120
##

## copy application results to run_dir
pod=`kubectl get pods --namespace=${NM_STORAPP} --no-headers | awk '{print $1}'`
mkdir ${run_dir}/${pod}
kubectl cp ${NM_STORAPP}/${pod}:/data ${run_dir}/${pod}
##

## collect stats

if [ "$MON_ENABLED" = "y" ]; then

    # copy stats files from sysstat pods to run_dir
    pod_list=`kubectl get pods --namespace=${NM_SYSSTAT} -l name=sysstat-collection --no-headers | awk '{print $1}'`
    for pod in ${pod_list}; do
	mkdir ${run_dir}/${pod}
	kubectl cp ${NM_SYSSTAT}/${pod}:/data ${run_dir}/${pod}
    done

fi

##

## clean up

# cleanup application pods, pvcs and namespaces
kubectl delete -f fio_job.yaml --namespace=${NM_STORAPP}
kubectl delete -f storapp_pvc.yaml --namespace=${NM_STORAPP}
kubectl delete namespace ${NM_STORAPP}

# cleanup monitoring pods 
if [ "$MON_ENABLED" = "y" ]; then

    kubectl delete -f daemonset_sysstat.yaml

fi

##

