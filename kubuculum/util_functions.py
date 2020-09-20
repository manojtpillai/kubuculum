
import yaml
import subprocess
from jinja2 import Environment, FileSystemLoader

# return deep update of base_dict with new_dict
# base_dict and new_dict are possibly nested
def deep_update (base_dict, new_dict):

    updated_dict = base_dict
    
    for new_key, new_value in new_dict.items ():
        if new_key in base_dict:
            base_value = base_dict[new_key]
            if isinstance (new_value, dict) and isinstance (base_value, dict):
                updated_value = deep_update (base_value, new_value)
                updated_dict[new_key] = updated_value
            else:
                updated_dict[new_key] = new_value
        else:
            updated_dict[new_key] = new_value

    return updated_dict

# prepare for calling a module
def prepare_call (module_label, module_params, setup_params):

    updated_dict = setup_params
    module_dict = module_params

    module_dir = updated_dict['dir'] + '/' + module_label
    module_dict['dir'] = module_dir
    create_dir (module_dir)

    updated_dict.update (module_dict)
    return updated_dict

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

    yaml_input = open (filename)
    params = yaml.safe_load (yaml_input)
    yaml_input.close ()

    if params is None:
        params = {}

    return params


# create a directory 
def create_dir (path):
    subprocess.run (["mkdir", path])

# pause for specified duration
def pause (pause_sec):
    subprocess.run (["sleep", str (pause_sec)])


