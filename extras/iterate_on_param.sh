#! /bin/bash

set -e 

# parameters section: BEGIN

# output files are collected into sub-directories here
BASE_DIR="/tmp/runs"

NUM_SAMPLES=3
DIR_PRFX="bs_kb_"
PARAM_NAME="bench_fiorand_bs_kb"
PARAM_VALUES="8 16 32"

# parameters section: END

for param in ${PARAM_VALUES}; do
    run_dir="${BASE_DIR}/${DIR_PRFX}${param}"
    mkdir -p ${run_dir}
    for sample in `seq ${NUM_SAMPLES}`; do
	ansible-playbook -i inventory kubuculum/perform_benchrun.yml \
	-e run_basedir=${run_dir} \
	-e ${PARAM_NAME}=${param} 
    done
done

