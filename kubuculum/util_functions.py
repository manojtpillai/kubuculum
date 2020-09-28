
import yaml
import subprocess
import time
from jinja2 import Environment, FileSystemLoader

# deep update of base_dict with new_dict
# base_dict and new_dict are possibly nested
# new_dict is unchanged
def deep_update (base_dict, new_dict):

    for new_key, new_value in new_dict.items ():
        if new_key in base_dict:
            base_value = base_dict.pop (new_key)
            if isinstance (new_value, dict) and isinstance (base_value, dict):
                deep_update (base_value, new_value)
                base_dict[new_key] = base_value
            else:
                base_dict[new_key] = new_value
        else:
            base_dict[new_key] = new_value

# prepare for calling a module
# updates module_params; global_params is unchanged
def prepare_call (module_label, module_params, global_params):

    module_dir = global_params['dir'] + '/' + module_label
    create_dir (module_dir)

    deep_update (module_params, global_params)
    module_params['dir'] = module_dir

# instantiate jinja2 template to produce yaml
# uses entries in dict to render the template 
def instantiate_template (template_dir, template_file, dest_file, dict):

    file_loader = FileSystemLoader (template_dir)
    env = Environment (loader=file_loader, trim_blocks=True)
    template = env.get_template (template_file)

    rendered_yaml = template.render (dict)

    yaml_file = open (dest_file, 'w')
    print (rendered_yaml, file = yaml_file)
    yaml_file.close ()

# given a yaml file containing a dict, return the dict
def dict_from_file (filename):

    with open (filename, 'r') as yaml_input:
        params = yaml.safe_load (yaml_input)

    if params is None:
        params = {}

    return params

# given a dict, write it to a yaml file
def dict_to_file (dict, filename):

    with open (filename, 'w') as outfile:
        yaml.dump (dict, outfile, default_flow_style=False, sort_keys=False)

# create a subdirectory based on a tag and current time
def createdir_ts (path, tag):

    ts = str (time.time ())
    subdir = path + '/' + tag + ts

    subprocess.run (["mkdir", subdir])
    return subdir

# create a directory 
def create_dir (path):
    subprocess.run (["mkdir", path])

# TODO: make it interruptible ala ansible pause
# pause for specified duration
def pause (pause_sec):
    subprocess.run (["sleep", str (pause_sec)])


