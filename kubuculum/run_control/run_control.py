
import logging
import copy
from kubuculum.setup_run import setup_run
import kubuculum.benchmarks.util_functions
import kubuculum.util_functions

logger = logging.getLogger (__name__)

def perform_singlerun (run_dir, params_dict):

    module_label = 'run_control'

    # get params for self
    module_params = params_dict.pop (module_label, {})
    if module_params is None:
        module_params = {}

    # TODO: read from defaults file
    run_globals = { 'namespace': 'nm-kubuculum' }
    if 'storageclass' in module_params:
        run_globals['storageclass'] = module_params['storageclass']
    if 'namespace' in module_params:
        run_globals['namespace'] = module_params['namespace']

    #
    # perform setup tasks
    #
    setup_handle = setup_run.environs (run_dir, params_dict, run_globals)
    setup_handle.do_setup ()
    logger.info ("setup completed")

    # 
    # create handle for enabled benchmark 
    #
    if 'benchmark' in module_params:

        benchmark_module = module_params['benchmark']
        logger.debug ("benchmark %s enabled", benchmark_module)

        benchmark_handle = kubuculum.benchmarks.util_functions.create_object \
            (benchmark_module, run_dir, params_dict, run_globals)

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


