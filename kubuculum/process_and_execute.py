
import logging
import subprocess
import copy
from kubuculum import util_functions
from kubuculum.multirun_control import multirun_control

def perform_runs (run_params):

    # make a copy of params
    params_dict = copy.deepcopy (run_params)

    #
    # handle global parameters
    #
    # remove global parameters from params_dict
    passed_globals = params_dict.pop ('global', {})
    if passed_globals is None:
        passed_globals = {}

    passed_logparams = passed_globals.pop ('log_control', {})
    if passed_logparams is None:
        passed_logparams = {}

    # TODO: read from defaults file
    # global params minus log_control params
    global_params = {
        'base_directory': '/tmp',
        'input_copy': 'kubuculum.input.yaml'
    }

    # update global defaults with passed values
    util_functions.deep_update (global_params, passed_globals) 

    # create a directory for runs, if needed
    if 'dir' not in global_params:
        global_rundir = util_functions.createdir_ts \
            (global_params['base_directory'], 'run_')
    else:
        global_rundir = global_params.pop ('dir')
    global_params.pop ('base_directory') 

    # write a copy of input params as yaml
    input_file_copy = global_params.pop ('input_copy')
    input_file_copy = global_rundir + '/' + input_file_copy
    util_functions.dict_to_file (run_params, input_file_copy)

    # TODO: read from defaults file
    #
    # setup logging
    #
    logging_params = {
        'stderr': { 'enabled': True, 'level': 'INFO' },
        'file': { 'enabled': True, 'filename': 'kubuculum.log', 'level': 'DEBUG' }
    }

    # update logging defaults with passed values
    util_functions.deep_update (logging_params, passed_logparams) 

    logger = logging.getLogger ()
    logger.setLevel (logging.DEBUG)

    stderr_params = logging_params['stderr']
    if stderr_params['enabled']:
        ch = logging.StreamHandler ()
        ch.setLevel (stderr_params['level'])
        logger.addHandler (ch)

    file_params = logging_params['file']
    if file_params['enabled']:
        if 'dirname' in file_params:
            dir = file_params['dirname']
        else:
            dir = global_rundir

        file = dir + '/' + file_params['filename']
        fh = logging.FileHandler (file)
        fmt = logging.Formatter ('%(asctime)s - %(levelname)s - %(message)s')
        fh.setLevel (file_params['level'])
        fh.setFormatter (fmt)
        logger.addHandler (fh)

    logger.info ("output directory: %s" , global_rundir)

    #
    # perform runs
    #
    multirun_control.perform_runs (global_rundir, params_dict)

