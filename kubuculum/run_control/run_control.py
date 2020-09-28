
import logging
import copy
from kubuculum.setup_run import setup_run
import kubuculum.benchmarks.util_functions
import kubuculum.util_functions

logger = logging.getLogger (__name__)

def perform_singlerun (params_dict, global_params):

    module_label = 'run_control'

    # get params for self
    module_params = params_dict.pop (module_label, {})
    if module_params is None:
        module_params = {}

    #
    # perform setup tasks
    #
    setup_handle = setup_run.environs (global_params)
    setup_handle.do_setup ()
    logger.info ("setup completed")

    # 
    # create handle for enabled benchmark 
    #
    if 'benchmark' in module_params:

        benchmark_module = module_params['benchmark']
        logger.debug ("benchmark %s enabled", benchmark_module)

        benchmarks_dict = params_dict.get ('benchmarks', {})
        if benchmarks_dict is None:
            benchmarks_dict = {}

        bench_params = benchmarks_dict.get (benchmark_module, {})
        if bench_params is None:
            bench_params = {}

        callee_params = copy.deepcopy (bench_params)
        kubuculum.util_functions.prepare_call \
            (benchmark_module, callee_params, global_params)

        if 'storageclass' in module_params:
            callee_params['storageclass'] = module_params['storageclass']

        benchmark_handle = kubuculum.benchmarks.util_functions.create_object (benchmark_module, callee_params)

    else:
        benchmark_module = None
        logger.info ("no benchmark enabled")


    # 
    # execute benchmark prepare phase
    #
    if benchmark_module is not None:
        logger.info ("initiating benchmark prepare phase")
        benchmark_handle.prepare()
        logger.info ("benchmark prepare phase completed")

    # 
    # execute benchmark run phase
    #
    if benchmark_module is not None:
        logger.info ("initiating benchmark run phase")
        benchmark_handle.run ()
        logger.info ("benchmark run phase completed")

    #
    # perform cleanup tasks
    #
    setup_handle.cleanup ()
    logger.info ("cleanup completed")


