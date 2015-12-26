import re
import os
import sys
import json
import io
# RE used to search resource profiles in FHIR's specs. directory
#TODO support multiple types for one element

PROFILE_F_RE = re.compile(r'^type-(?P<datatype>\w+).profile.json$|^(?P<resource>\w+).profile.json$')
WARNING = 'WARNING: this is auto generated. Change it at your risk.'
'''
Manual changes made to fhir_spec.py:
    2. change effective[x] to effectiveDateTime
    3. change value[x] to value, type to CodeableConcept
'''

#TODO: Need improvement
def get_type_for_param(code):
    '''
    Get the praram type from the element type
    '''
    if code in ['integer', 'decimal']:
        type_for_param = 'number'
    elif code in ['date', 'dateTime', 'instant', 'Period', 'Timing']:
        type_for_param = 'date'
    elif code in ['code', 'CodeableConcept', 'Coding', 'Identifier', 'ContactPoint', 'boolean']:
        type_for_param = 'token'
    elif 'reference' in code or 'Reference' in code:
        type_for_param = 'reference'
    elif 'Quantity' in code:
        type_for_param = 'quantity'
    else:
        type_for_param = 'string'
    return type_for_param


def process_profile(profile):
    '''
    Process a resource profile (in FHIR's JSON format)
    as our internal structure for specs. code generation
    '''
    ori_elements = profile['snapshot']['element']

    # `refeence_types` maintains the mapping
    # between a search parameter of type ResourceReference and possible resource types
    reference_types = {}
    elements = []
    for ori_element in ori_elements:
        if ori_element.get('type') is not None:
            element_type = ori_element['type']
            references = []
            for each_type in element_type:
                path = ori_element['path']
                type_code = each_type['code']
                if '[x]' in path:
                    path = path[:-3] + type_code[0].upper() + type_code[1:]
                    print path

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
    for element in elements:
        if element.get('searchParam'):
            param_name = element['searchParam']['name']
            param_type = element['searchParam']['type']
            search_params[param_name] = param_type
    return elements, search_params, reference_types


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

            for resource_block in resources_block:
                elements, resource_search_params, resource_reference_types = process_profile(resource_block)
                assert 'path' in elements[0]
                name = elements[0]['path']
                assert name is not None
                specs[name] = {
                    'elements': elements,
                    'searchParams': resource_search_params
                    }
                resource_names.append(name)
                reference_types[name] = resource_reference_types

                print 'Loaded %s\'s profile' % name

    '''
    for f in os.listdir(spec_dir):
        matched = PROFILE_F_RE.match(f)
        if matched is not None:
            profile_loc = os.path.join(spec_dir, f)
            elements, resource_search_params, resource_reference_types = load_and_process_profile(
                profile_loc)
            name = elements[0]['path']
            # manually add assessed-condition into list of serach params
            if name == 'Observation':
                resource_search_params['Sequence'] = 'reference'
                resource_reference_types['Sequence'] = ['Sequence']
                resource_search_params['Source'] = 'token'
                resource_search_params['VariationHGVS'] = 'token'
                resource_search_params['VariationType'] = 'token'
                resource_search_params['AminoAcidVariation'] = 'token'
                resource_search_params['Region'] = 'token'
                resource_search_params['Gene'] = 'token'
            if name == 'DiagnosticReport':
                resource_search_params['AssessedCondition'] = 'reference'
                resource_reference_types['AssessedCondition'] = ['Condition']

            specs[name] = {
                'elements': elements,
                'searchParams': resource_search_params
            }

            if matched.group('resource') is not None:
                resources.append(name)
                reference_types[name] = resource_reference_types

            print 'Loaded %s\'s profile' % name
            resources.append('name')
    '''
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
