"""
Get info on a FileMaker DDR.

Expects a transfer_file text file that contains a return-delimited list of a
path to a DDR file and one or more directives ( see 'lines' variable ).

Returns a JSON with specified directives into the transfer file.
"""
import os
import xml.etree.ElementTree as ET
import json


def main():
    transfer_file_path = os.path.expanduser(
        '~/Library/Caches/org.nyhtc.auto/transfer_file.txt')
    lines = read_transfer_file(transfer_file_path)

    file_path = lines.pop(0)
    # remaining lines make up a list of directives to extract

    tree = ET.parse(file_path)
    root = tree.getroot()

    d = {}
    if 'accounts' in lines:
        d['account'] = get_accounts(root)
    if 'layouts' in lines:
        d['layout'] = get_layouts(root)
    if 'privSets' in lines:
        d['privSet'] = get_priv_sets(root)
    if 'scripts' in lines:
        d['script'] = get_scripts(root)
    if 'table_occurences' in lines:
        d['table_occurence'] = get_table_occurences(root)
    if 'tables' in lines:
        d['table'] = get_tables(root)
    if not d:
        d = 'ERROR - unknown directive'

    return write_transfer_file(transfer_file_path, d)


def read_transfer_file(transfer_file_path):
    with open(transfer_file_path, 'r') as f:
        lines = f.read().splitlines()
    return lines


def write_transfer_file(transfer_file_path, item_list):
    with open(transfer_file_path, 'w') as f:
        json.dump(item_list, f)
    return True


def get_accounts(root):
    item_list = []
    catalog = root.find('.//AccountCatalog')
    for one_item in catalog:
        d = {'id': one_item.get('id'),
             'account': one_item.get('name'),
             'privSet': one_item.get('privilegeSet'),
             'status': one_item.get('status'),
             'emptyPassword': one_item.get('emptyPassword')
             }
        item_list.append(d)
    return item_list


def get_scripts(root):
    item_list = []
    catalog = root.findall('.//ScriptCatalog//Script[@includeInMenu]')
    for script in catalog:
        item_list.append(script.attrib)
    return item_list


def get_layouts(root):
    item_list = []
    catalog = root.findall('.//LayoutCatalog//Layout[@includeInMenu]')
    for one_item in catalog:
        d = {'layout_id': one_item.get('id'),
             'layout_name': one_item.get('name'),
             'table_id': one_item[0].get('id'),
             'table_name': one_item[0].get('name')
             }
        item_list.append(d)
    return item_list


def get_priv_sets(root):
    item_list = []
    catalog = root.find('.//PrivilegesCatalog')
    for one_item in catalog:
        d = {'id': one_item.get('id'),
             'name': one_item.get('name'),
             'comment': one_item.get('comment'),
             'record': one_item[0].get('value'),
             'layout': one_item[1].get('value'),
             'value_list': one_item[2].get('value'),
             'script': one_item[3].get('value')
             }
        item_list.append(d)
    return item_list


def get_table_occurences(root):
    item_list = []
    catalog = root.find('.//RelationshipGraph/TableList')
    for one_item in catalog:
        file = one_item[0].attrib.get('name') if len(list(one_item)) else ''
        d = one_item.attrib
        d['baseFile'] = file
        d['TO_id'] = d.pop('id')
        d['TO_name'] = d.pop('name')
        del d['color']
        item_list.append(d)
    return item_list


def get_tables(root):
    item_list = []
    catalog = root.find('.//BaseTableCatalog')
    for one_item in catalog:
        d = {'id': one_item.get('id'),
             'name': one_item.get('name'),
             'records': one_item.get('records'),
             'fields': get_fields_for_table(one_item)
             }
        item_list.append(d)
    return item_list


def get_fields_for_table(table_node):
    fields = []
    for one_item in table_node[0]:
        d = {'id': one_item.get('id'),
             'name': one_item.get('name'),
             'dataType': one_item.get('dataType'),
             'fieldType': one_item.get('fieldType'),
             'comment': one_item.findtext('Comment', default='')
             }
        storage_element = one_item.find('Storage')
        if storage_element is not None:
            d['index'] = storage_element.get('index')
            d['global'] = storage_element.get('global')
            d['reps'] = storage_element.get('maxRepetition')
            d['storage'] = storage_element.get('storeCalculationResults')
        fields.append(d)
    return fields


if __name__ == '__main__':
    main()
