
from kubuculum import util_functions
from kubuculum.run_control import run_control

def perform_runs (params_dict):

    module_label = "multirun_control"

    # remove my parameters from params_dict
    module_params = params_dict.pop (module_label, {})
    if module_params is None:
        module_params = {}

    # get list of tests to iterate over
    test_list = module_params.get ('test_list', [])
    if test_list is None:
        test_list = []

    for test_dict in test_list:
        if test_dict is None:
            test_dict = {}

        # generate single dict: params_dict updated with test_dict
        run_params = util_functions.deep_update (params_dict, test_dict)

        # run_params is now in a form that perform_singlerun expects
        run_control.perform_singlerun (run_params) 

