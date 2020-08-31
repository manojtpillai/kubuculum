

# base_dict and new_dict are possibly nested
# return deep update of base_dict with new_dict
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

