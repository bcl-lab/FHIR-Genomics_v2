import re
import os
import sys
import json
from fhir.sequence import sequence_resource, sequence_reference_types

# RE used to search resource profiles in FHIR's specs. directory
PROFILE_F_RE = re.compile(r'^type-(?P<datatype>\w+).profile.json$|^(?P<resource>\w+).profile.json$')
WARNING = 'WARNING: this is auto generated. Change it at your risk.'

def load_and_process_profile(profile_loc):
    '''
    load a profile file and prepare it as internal structure for specs. code generation
    '''
    with open(profile_loc) as profile_f:
        return process_profile(json.load(profile_f))


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
        element = {}
        path = ori_element['path']
        element['path'] = path
        definition = {}
        definition['min'] = ori_element['min']
        definition['max'] = ori_element['max']
        if ori_element.get('type'):
            definition['type'] = ori_element['type']
            element['definition'] = definition
            names = path.split('.')[1:]
            name = '-'.join(names)
            if name:
                code = ori_element['type'][0]['code']
                if code in ['integer', 'decimal']:
                    type_for_praram = 'number'
                elif code in ['date', 'dateTime', 'instant', 'Period', 'Timing']:
                    type_for_praram = 'date'
                elif code in ['code', 'CodeableConcept', 'Coding', 'Identifier', 'ContactPoint', 'boolean']:
                    type_for_praram = 'token'
                elif 'reference' in code:
                    type_for_praram = 'reference'
                elif 'Quantity' in code:
                    type_for_praram = 'quantity'
                else:
                    type_for_praram = 'string'

                search_param = {'name': name, 'type': type_for_praram}
                element['searchParam'] = search_param

                types = []
                for element_type in ori_element['type']:
                    if element_type['code'] == 'Reference':
                        if element.get('profile'):
                            for reference in element_type['profile']:
                                reference_type = reference.split('/')[-1]
                                types.append(reference_type)
                            reference_types[search_param['name']] = types or None

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
    resources = []
    reference_types = {}
    for f in os.listdir(spec_dir):
        matched = PROFILE_F_RE.match(f)
        if matched is not None:
            profile_loc = os.path.join(spec_dir, f)
            elements, resource_search_params, resource_reference_types = load_and_process_profile(
                profile_loc)
            name = elements[0]['path']
            # manually add assessed-condition into list of serach params
            if name == 'Observation':
                resource_search_params['assessed-condition'] = 'reference'
                resource_reference_types['assessed-condition'] = ['Condition']

            specs[name] = {
                'elements': elements,
                'searchParams': resource_search_params
            }

            if matched.group('resource') is not None:
                resources.append(name)
                reference_types[name] = resource_reference_types

            print 'Loaded %s\'s profile' % name
            resources.append('name')


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
