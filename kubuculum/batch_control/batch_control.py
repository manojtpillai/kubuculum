
import logging
import copy
from kubuculum import util_functions
from kubuculum.run_control import run_control

logger = logging.getLogger (__name__)

def perform_runs (batch_dir, params_dict):

    module_label = 'batch_control'

    # input file does not have section for batch_control
    if module_label not in params_dict:
        run_control.perform_singlerun (batch_dir, params_dict) 
        return

    # remove my parameters from params_dict
    module_params = params_dict.pop (module_label, {})
    if module_params is None:
        module_params = {}

    # get list of runs to iterate over
    run_list = module_params.get ('run_list', [])
    if run_list is None:
        run_list = []

    iter = 0
    for run_dict in run_list:

        if run_dict is None:
            run_dict = {}

        if 'run_tag' in run_dict:
            run_subdir = run_dict.pop ('run_tag')
        else:
            run_subdir = 'run-' + str(iter)

        # TODO: handle exception
        # set directory for this run
        run_dir = util_functions.create_subdir (batch_dir, run_subdir)

        # generate single dict: params_dict updated with run_dict
        run_params = copy.deepcopy (params_dict)
        util_functions.deep_update (run_params, run_dict)

        logger.info ('starting run: %s', run_subdir)

        # run_params is now in a form that perform_singlerun expects
        run_control.perform_singlerun (run_dir, run_params) 

        iter += 1

    logger.info ('all runs completed')

