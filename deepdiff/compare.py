# -*- coding: utf-8 -*-
"""

"""
#regular expressions
import re
#https://github.com/seperman/deepdiff
from deepdiff import DeepDiff

def deep_dif_cmp(t1, 
                 t2, 
                 t1_name, 
                 t2_name,
                 dict_update,
                 encode_type):
    """This method compares two objects, t1 and t2, 
    and identifies two types of differences: 1) value changes and 
    2) object type changes. Lastly, the method returns a list with commands
    to make the second object equivalent to the first in attribute value and 
    type; however, the id of each object will remain the same.
    
    This method was created out of a use case where two data stores exist 
    for the same physical item or asset and the two need to be syncronized.
    From the start, it is assumed the first object is "definitive" and the 
    second object is the one requiring an "update". 
    
    If objects are represented in different systems entirely, it is not
    possible to use an equals symbol to programmatically make the second
    object equal to the first.
                              t1 = t2
    
    If t1 is a csv or text file and t2 is an API interface using JSON on a 
    server; one could "submit" all the data for t1 to the API and overwrite
    the representation of t2 on the server; however, as the size of the data
    to represent t1 increases, so does the amount of JSON data that must be
    submitted to the API interface.
    
    So, this module seeks to determine what are just the handful of commands
    that are required to make t2 = t1. 
    
    Args:
        t1 - obj believed to be current, 
        t2 - obj believed to be out-of-date, 
        t1_name - str to use for t1, 
        t2_name - str to use for t2,
        dict_update - and empty dictionary,
        encode_type - specify either 'dict' or 'obj'
         
    Result:
        update_cmds - list of commands to execute manually to make t2 = t1
    """
    
    print('--------DeepDiff Object Comparison---------\n')
    print('--------------- tree view -----------------\n')
    print('t1 = \n{0}\n\nt2 = \n{1}\n'.format(t1, t2))
    ddiff_verbose2_tree = DeepDiff(t1, t2, verbose_level=2, view='tree')
    print('DeepDiff(t1, t2, verbose_level=2,\
                    view=\'tree\') = \n{}\n'.format(
            ddiff_verbose2_tree))
   
    def check_deep_diff(obj, encode_type, obj_name):
        
        if isinstance(obj, DeepDiff):
            if 'values_changed' in obj:
                #set_of_values_changed = obj['values_changed']
                update_cmds = print_deepdiff_changed(
                        obj = list(obj['values_changed']), 
                        type_of_change = 'values_changed',
                        encode_type = encode_type,
                        obj_name = obj_name)
                return update_cmds
            if 'types_changes' in obj:
                #set_of_types_changed = obj['type_changes']
                update_cmds = print_deepdiff_changed(
                        obj = list(obj['values_changed']), 
                        type_of_change = 'types_changed', 
                        encode_type = encode_type)
                return update_cmds

    def print_deepdiff_changed(obj, 
                               type_of_change, 
                               encode_type,
                               obj_name):
        update_cmds = []
        if isinstance(obj, list):
            len_obj = len(obj) - 1
            print('\n..............................................')
            print('type of change = {}'.format(type_of_change))
            print('..............................................\n')
            for idx, val in enumerate(obj):
                print('change {0} of {1} = {2:0.0f} %\n'
                      .format(idx,
                              len_obj,
                              (idx/len_obj*100)))
                print(val)
                print('type(change) = {0}\n\
                      change = {1}\n\
                      change.path = {2}\n'
                      .format(type(obj[idx]),
                              val,
                              obj[idx].path()))
                print('change.t1 = {}\t change.t2 = {}\n'
                      .format(obj[idx].t1, 
                              obj[idx].t2))
                
                update_instructions(dict_update,
                           obj[idx].path(),
                           obj[idx].t1)
                if encode_type == 'obj':
                    update_cmds.append(
                            encode_update_cmd(
                            new_val = obj[idx].t1,
                            change_path = obj[idx].path(),
                            encode_type='obj',
                            obj_name = obj_name)
                            )
                if encode_type == 'dict':
                    update_cmds.append(
                            encode_update_cmd(
                            change_path = obj[idx].path(),
                            new_val = obj[idx].t1,
                            encode_type='dict')
                            )
            print('update dictionary = \n{}\n'.format(dict_update))
            print('update command list = \n')
            [print(cmd) for cmd in update_cmds]
        return update_cmds

    def update_instructions(dict_obj, key, val, obj_name = 'obj2'):
        dict_obj[key] = val
    def get_dict_key_from_change(change_path):
        print('change_path = {}'.format(change_path))
        if change_path:
            #need to remove root word from str
            change = change_path[4:len(change_path)]
            print('change = {}'.format(change))
            return change

    def encode_update_cmd(new_val, 
                          change_path,
                          encode_type,
                          obj_name = t2_name 
                          ):
        if change_path:
            change = get_dict_key_from_change(change_path)
            print('change = {}'.format(change))
            if encode_type == 'dict':
                cmd = obj_name + change + ' = '
                print('.....encoding update for dict.....')
                if isinstance(new_val, str):
                    cmd += new_val
                else:
                    cmd += str(new_val)
                print('dictionary update cmd = {}'.format(cmd))
                return cmd
            if encode_type == 'obj':
                print('.....encoding update for custom object.....')
                regex = r"(\w+)"
                p = re.compile(regex)
                attrs = p.findall(change)
                attr_path = obj_name + '.' + '.'.join(attrs) \
                    + ' = ' + str(new_val)
                print('type(attrs) = {}\nattrs = {}\n\
                      encode update command => \n{}\n'
                  .format(type(attrs), attrs, attr_path))
                return attr_path
        else:
            print('\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            print('change_path is None!')
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n')

    update_cmds = check_deep_diff(obj = ddiff_verbose2_tree, 
                                  encode_type = encode_type, 
                                  obj_name = t2_name)
    return update_cmds


if __name__ == '__main__':
    cnc1 = {'make': 'Siemens', 'drillbits': [
            {'id': 1, 'name': '1/8"', 'dull': True}, 
            {'id': 2, 'name': '1/4"', 'dull': False}, 
            {'id': 3, 'name': '1/2"', 'dull': False}], 'id': 1}
    cnc2 = {'make': 'Acme', 'drillbits': [
            {'id': 1, 'name': '1/8"', 'dull': True}, 
            {'id': 5, 'name': '3/16"', 'dull': True}, 
            {'id': 6, 'name': '5/8"', 'dull': False}], 'id': 2}

    
    print('----- deepdiff tree view for cnc1 & cnc2 -------')
    update_cmds_dict = deep_dif_cmp(cnc1, 
                               cnc2, 
                               t1_name='cnc1', 
                               t2_name='cnc2',
                               dict_update = {},
                               encode_type='dict')
    update_cmds_obj = deep_dif_cmp(cnc1, 
                               cnc2, 
                               t1_name='cnc1', 
                               t2_name='cnc2',
                               dict_update = {},
                               encode_type='obj')

