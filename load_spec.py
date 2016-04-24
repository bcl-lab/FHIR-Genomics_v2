import re
import os
import sys
import json
import io
import copy
# RE used to search resource profiles in FHIR's specs. directory
#TODO support multiple types for one element

PROFILE_F_RE = re.compile(r'^type-(?P<datatype>\w+).profile.json$|^(?P<resource>\w+).profile.json$')
WARNING = 'WARNING: this is auto generated. Change it at your risk.'


#TODO: Need improvement
def get_type_for_param(code):
    '''
    Get the praram type from the element type
    '''
    if code in ['integer', 'decimal']:
        type_for_param = 'number'
    elif code in ['date', 'dateTime', 'instant', 'Period', 'Timing']:
        type_for_param = 'date'
    elif code in ['code', 'CodeableConcept', 'Coding', 'Identifier', 'ContactPoint']:
        type_for_param = 'token'
    elif 'reference' in code or 'Reference' in code:
        type_for_param = 'reference'
    elif 'Quantity' in code:
        type_for_param = 'quantity'
    elif 'string' in code:
        type_for_param = 'string'
    else:
        type_for_param = code

    return type_for_param


#TODO: need support complex element as extensions
def find_extension_attri(filename):
    filepath = os.path.join(spec_dir, 'extension-' + filename + '.json')
    with io.open(filepath, encoding='utf-8') as handle:
        parsed = json.load(handle)
        ori_elements = parsed['differential']['element']
        for ori_element in ori_elements:
            if ori_element['path'] == 'Extension.value[x]':
                if ori_element.get('type') is not None:
                    return ori_element['type'], parsed['url']
        return None, parsed['url']


def find_complex_extension_attri(filename, base_name):
    filepath = os.path.join(spec_dir, 'extension-' + filename + '.json')
    names = []
    search_names = []
    types = []
    with io.open(filepath, encoding='utf-8') as handle:
        parsed = json.load(handle)
        ori_elements = parsed['snapshot']['element']
        for i in range(0, len(ori_elements)):
            ori_element = ori_elements[i]
            if ori_element['path'] == 'Extension.extension.url':
                name = ori_element['fixedUri']
                type = copy.copy(ori_elements[i+1]['type'])
                names.append(name)
                search_names.append(base_name+'-'+name)
                types.append(type)
        #print types
        return names, search_names, types


def process_profile(profile):
    '''
    Process a resource profile (in FHIR's JSON format)
    as our internal structure for specs. code generation
    '''
    ori_elements = profile['snapshot']['element']

    # `reference_types` maintains the mapping
    # between a search parameter of type ResourceReference and possible resource types
    reference_types = {}
    elements = []
    extensions = []
    complex_extensions = {}
    sub_extensions = {}
    for ori_element in ori_elements:
        if '.extension' in ori_element['path'] and ori_element.get('name') is not None:
            assert ori_element['type'][0]['code'] == 'Extension'
            assert ori_element['type'][0]['profile'] is not None
            extension_full_name = ori_element['type'][0]['profile'][0].split('/')[-1]
            extension_name = ori_element['name']
            extension_type, extension_url = find_extension_attri(extension_full_name)
            print "add extension: " + extension_name
            if extension_type:
                extension_type_code = extension_type[0].get('code')
                if extension_type_code == 'Reference':
                    references = []
                    for i in extension_type:
                        reference_type = i['profile'][0].split('/')[-1]
                        references.append(reference_type)
                    reference_types[extension_name] = references
                extensions.append({'name': extension_name,
                                   'type': extension_type_code,
                                   'url': extension_url})
            else:
                complex_extensions[extension_url] = {}
                complex_extension_names, complex_search_names, complex_extension_types = find_complex_extension_attri(extension_full_name, ori_element.get('name'))
                complex_extension_type_codes = []
                for extension_type in complex_extension_types:
                    extension_type_code = extension_type[0].get('code')
                    complex_extension_type_codes.append(extension_type_code)
                    if extension_type_code == 'Reference':
                        references = []
                        for i in extension_type:
                            reference_type = i['profile'][0].split('/')[-1]
                            references.append(reference_type)

                for i in range(0, len(complex_extension_names)):
                    complex_extensions[extension_url][complex_extension_names[i]] = [complex_search_names[i], complex_extension_type_codes[i]]
                    sub_extensions[complex_search_names[i]] = get_type_for_param(complex_extension_type_codes[i])
                print "add a complex extension: %s" % extension_url

        elif ori_element.get('type') is not None:
            element_type = ori_element['type']
            references = []
            for each_type in element_type:
                path = ori_element['path']
                type_code = each_type['code']
                if '[x]' in path:
                    path = path[:-3] + type_code[0].upper() + type_code[1:]

                if type_code == 'Reference' and each_type.get('profile') is not None:
                    reference = each_type['profile'][0]
                    reference_type = reference.split('/')[-1]
                    references.append(reference_type)
                    reference_path = path
                    reference_definition = {'min': ori_element['min'],
                                            'max': ori_element['max'],
                                            'type': type_code}
                    continue

                element = {'path': path}
                definition = {'min': 0,
                              'max': ori_element['max'],
                              'type': type_code}
                element['definition'] = definition
                names = path.split('.')[1:]
                name = '-'.join(names)
                type_for_param = get_type_for_param(type_code)
                search_param = {'name': name, 'type': type_for_param}
                element['searchParam'] = search_param

                for element_type in ori_element['type']:
                    if element_type['code'] == 'Reference':
                        reference_types['name'] = None
                elements.append(element)

            if len(references) > 0:
                names = reference_path.split('.')[1:]
                name = '-'.join(names)
                element = {'path': reference_path,
                           'definition': reference_definition,
                           'searchParam': {'name': name, 'type': 'reference'}
                           }
                reference_types[name] = references
                elements.append(element)

    search_params = {}
    extensions_map = {}
    for element in elements:
        if element.get('searchParam'):
            param_name = element['searchParam']['name']
            param_type = element['searchParam']['type']
            search_params[param_name] = param_type
    for extension in extensions:
        extension_type = extension['type']
        if extension_type != 'CodeableConcept':
            extension_type = extension_type[0].lower() + extension_type[1:]
        search_params[extension['name']] = get_type_for_param(extension_type)
        extensions_map[extension['url']] = {'name': extension['name'],
                                            'type': extension['type']}
    for extension_search_name in sub_extensions:
        search_params[extension_search_name] = sub_extensions[extension_search_name]

    return elements, search_params, reference_types, extensions_map, complex_extensions


def load_spec(spec_dir):
    '''
    Load FHIR specs. given directory of all the profiles
    (FHIR uses Profile resource to document specs.)
    '''
    specs = {}
    resources_block = []
    resource_names = []
    reference_types = {}

    for filename in ['profiles-resources.json']: #, 'profiles-others.json']:
        filepath = os.path.join(spec_dir, filename)
        with io.open(filepath, encoding='utf-8') as handle:
            parsed = json.load(handle)
            assert parsed is not None
            assert 'resourceType' in parsed
            assert 'Bundle' == parsed['resourceType']
            assert 'entry' in parsed

            # find resources in entries
            for entry in parsed['entry']:
                resource_block = entry.get('resource')
                if resource_block is not None:
                    assert 'resourceType' in resource_block
                    if 'StructureDefinition' == resource_block['resourceType']:
                        resources_block.append(resource_block)
                else:
                    logging.warning('There is no resource in this entry: {}'
                        .format(entry))

    # load profiles
    for filename in ['observationforgenetics.profile.json', 'consensus-sequence-block.profile.json',
                     'reportforgenetics.profile.json', 'orderforgenetics.profile.json',
                     'hlaresult.profile.json', 'familymemberhistory-genetic.profile.json']:
        filepath = os.path.join(spec_dir, filename)
        with io.open(filepath, encoding='utf-8') as handle:
            parsed = json.load(handle)
            assert parsed is not None
            assert 'resourceType' in parsed
            assert 'StructureDefinition' == parsed['resourceType']
            resource_block = dict(parsed)
            resources_block.append(resource_block)

    for resource_block in resources_block:
        elements, resource_search_params, resource_reference_types, extensions_map, complex_extensions = process_profile(resource_block)
        assert 'id' in resource_block
        name = resource_block['id']
        assert name is not None
        specs[name] = {
            'elements': elements,
            'searchParams': resource_search_params,
            'extensionsMap': extensions_map,
            'complexExtensions': complex_extensions
            }
        resource_names.append(name)
        reference_types[name] = resource_reference_types
        if len(resource_reference_types) > 1:
            for item in resource_reference_types:
                if item == 'name':
                    continue
                #print resource_reference_types, item
                if 'Observation' in resource_reference_types[item]:
                    resource_reference_types[item] += ['observationforgenetics', 'consensus-sequence-block']
                if 'DiagnosticReport' in resource_reference_types[item]:
                    resource_reference_types[item] += ['reportforgenetics', 'hlaresult']
                if 'DiagnosticOrder' in resource_reference_types[item]:
                    resource_reference_types[item] += ['orderforgenetics']
                if 'FamilyMemberHistory' in resource_reference_types[item]:
                    resource_reference_types[item] += ['familymemberhistory-genetic']

        print 'Loaded %s\'s profile' % name

    with open('fhir/fhir_spec.py', 'w') as spec_target:
        spec_target.write("'''\n%s\n'''" % WARNING)
        spec_target.write('\n')
        spec_target.write('SPECS=' + str(specs))
        spec_target.write('\n')
        spec_target.write('RESOURCES=set(%s)'% str(resource_names))
        spec_target.write('\n')
        spec_target.write('REFERENCE_TYPES=' + str(reference_types))


if __name__ == '__main__':
    # find out where the specs. directory is.
    # Should be supplied via either command line or config file
    if len(sys.argv) == 2: 
        spec_dir = sys.argv[1]
    else:
        try:
            from config import FHIR_SPEC_DIR
            spec_dir = FHIR_SPEC_DIR
        except ImportError:
            print 'Unable to find FHIR spec directory..'
            print 'specify with `FHIR_SPEC_DIR` in `config.py`'
            print 'or do'
            print '$ python load_spec.py [spec dir]'
            sys.exit(1) 
    load_spec(spec_dir)
    print 'finished.!'
