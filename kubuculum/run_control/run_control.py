
import logging
import copy
from kubuculum.setup_run import setup_run
from kubuculum.dropcaches import dropcaches
import kubuculum.benchmarks.util_functions
import kubuculum.statistics.util_functions
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
    setup_handle = setup_run.setup_run (run_dir, params_dict, run_globals)
    setup_handle.do_setup ()
    logger.info (f'setup completed')

    # 
    # create handle for stats module
    #
    if 'statistics' in module_params:

        stats_module = module_params['statistics']
        logger.debug (f'statistics: {stats_module} enabled')

        stats_handle = kubuculum.statistics.util_functions.create_object \
            (stats_module, run_dir, params_dict, run_globals)

        stats_handle.start()
        logger.info (f'stats collection started')

    else:
        logger.debug (f'statistics not enabled')
        stats_module = None

    # 
    # create handle for enabled benchmark 
    #
    if 'benchmark' in module_params:

        benchmark_module = module_params['benchmark']
        logger.debug (f'benchmark {benchmark_module} enabled')

        benchmark_handle = kubuculum.benchmarks.util_functions.create_object \
            (benchmark_module, run_dir, params_dict, run_globals)

    else:
        benchmark_module = None
        logger.info (f'no benchmark enabled')


    # 
    # execute benchmark prepare phase
    #
    if benchmark_module is not None:
        logger.info (f'initiating benchmark prepare phase')
        benchmark_handle.prepare()
        logger.info (f'benchmark prepare phase completed')

    # 
    # drop caches before run
    #
    drop_caches = module_params.get ('dropcaches_beforerun', False)
    if drop_caches:
        dc_handle = dropcaches.dropcaches (run_dir, params_dict, run_globals)
        dc_handle.drop_caches ()
        logger.info (f'caches dropped before run phase')

    # 
    # execute benchmark run phase
    #
    if benchmark_module is not None:
        logger.info (f'initiating benchmark run phase')
        benchmark_handle.run ()
        logger.info (f'benchmark run phase completed')

    # 
    # gather statistics
    #
    if stats_module is not None:
        stats_handle.gather ()
        logger.info (f'statistics gathered')

    # 
    # stop statistics
    #
    if stats_module is not None:
        stats_handle.stop ()
        logger.info (f'statistics collection stopped')

    #
    # perform cleanup tasks
    #
    setup_handle.cleanup ()
    logger.info (f'cleanup completed')


