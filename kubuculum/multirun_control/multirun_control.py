
import logging
import copy
from kubuculum import util_functions
from kubuculum.run_control import run_control

logger = logging.getLogger (__name__)

def perform_runs (params_dict, global_params):

    module_label = 'multirun_control'

    # remove my parameters from params_dict
    module_params = params_dict.pop (module_label, {})
    if module_params is None:
        module_params = {}

    # get list of tests to iterate over
    test_list = module_params.get ('test_list', [])
    if test_list is None:
        test_list = []

    run_dir = global_params['dir']
    iter = 0
    for test_dict in test_list:

        if test_dict is None:
            test_dict = {}

        if 'test_tag' in test_dict:
            test_subdir = test_dict.pop ('test_tag')
        else:
            test_subdir = 'test-' + str(iter)

        # set directory for this test
        test_dir = run_dir + '/' + test_subdir
        util_functions.create_dir (test_dir)

        passed_globals = copy.deepcopy (global_params)
        passed_globals['dir'] = test_dir


        # generate single dict: params_dict updated with test_dict
        run_params = copy.deepcopy (params_dict)
        util_functions.deep_update (run_params, test_dict)

        logger.info ('starting test: %s', test_subdir)

        # run_params is now in a form that perform_singlerun expects
        run_control.perform_singlerun (run_params, passed_globals) 

        iter += 1

    logger.info ('all tests completed')

