

from kubuculum.statistics.sysstat.sysstat import sysstat

def create_object (class_name, run_dir, params_dict, globals):

    if class_name == 'sysstat':
        object_handle = sysstat (run_dir, params_dict, globals)

    # TODO: else handle error
    return object_handle

