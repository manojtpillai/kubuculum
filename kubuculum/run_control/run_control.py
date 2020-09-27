
from kubuculum.setup import setup
import kubuculum.benchmarks.util_functions
import kubuculum.util_functions

def perform_singlerun (params_dict, global_params):

    module_label = 'run_control'

    # create updated params for self
    module_params = params_dict.get (module_label, {})
    if module_params is None:
        module_params = {}

    #
    # perform setup tasks
    #
    callee_label = 'setup'
    callee_params = params_dict.get (callee_label, {})
    if callee_params is None:
        callee_params = {}

    callee_params.update (global_params)
    setup_handle = setup.environs (callee_params)
    setup_handle.do_setup ()

    # 
    # create handle for enabled benchmark 
    #
    benchmark_module = module_params['benchmark']
    if benchmark_module is not None:
        benchmarks_dict = params_dict.get ('benchmarks', {})
        if benchmarks_dict is None:
            benchmarks_dict = {}

        passed_params = benchmarks_dict.get (benchmark_module, {})
        if passed_params is None:
            passed_params = {}

        callee_params = kubuculum.util_functions.prepare_call \
            (benchmark_module, passed_params, global_params)

        benchmark_handle = kubuculum.benchmarks.util_functions.create_object (benchmark_module, callee_params)


    # 
    # execute benchmark prepare phase
    #
    if benchmark_module is not None:
        benchmark_handle.prepare()

    # 
    # execute benchmark run phase
    #
    if benchmark_module is not None:
        benchmark_handle.run ()

    #
    # perform cleanup tasks
    #
    setup_handle.cleanup ()


