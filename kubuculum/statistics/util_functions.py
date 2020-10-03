

from kubuculum.statistics.sysstat.sysstat import sysstat
from kubuculum.stats_splitter.stats_splitter import stats_splitter

def create_object (class_name, run_dir, params_dict, globals):

    if class_name == 'sysstat':
        object_handle = sysstat (run_dir, params_dict, globals)
    elif class_name == 'stats_splitter':
        object_handle = stats_splitter (run_dir, params_dict, globals)

    # TODO: else handle error
    return object_handle

