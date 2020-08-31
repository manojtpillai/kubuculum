
from kubuculum.setup import setup
from kubuculum.benchmarks import util_functions

def perform_singlerun (params_dict):

    module_label = "run_control"

    # create updated params for self
    module_params = params_dict.get (module_label, {})
    if module_params is None:
        module_params = {}

    #
    # perform setup tasks
    #
    callee = 'setup'
    callee_params = params_dict.get (callee, {})
    if callee_params is None:
        callee_params = {}

    setup_handle = setup.environment (callee_params)
    setup_handle.do_setup ()

    # 
    # execute benchmark prepare phase
    #
    callee = module_params['benchmark']
    if callee is not None:
        benchmarks_dict = params_dict.get ('benchmarks', {})
        if benchmarks_dict is None:
            benchmarks_dict = {}

        callee_params = benchmarks_dict.get (callee, {})
        if callee_params is None:
            callee_params = {}

        benchmark_handle = util_functions.create_object (callee, callee_params)

        benchmark_handle.prepare()

    # 
    # execute benchmark run phase
    #
    benchmark_handle.run ()

    #
    # perform cleanup tasks
    #
    setup_handle.cleanup ()



