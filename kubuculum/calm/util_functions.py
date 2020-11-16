
from kubuculum.calm.fio_iops.fio_iops import fio_iops

def create_object (class_name, run_dir, params_dict, globals):

    if class_name == 'fio_iops':
        object_handle = fio_iops (run_dir, params_dict, globals)

    # TODO: else handle error
    return object_handle

