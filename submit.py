__author__ = 'HemingY'

from fhir.models import db, Resource, User, Client, commit_buffers
from fhir.indexer import index_resource
from fhir.fhir_parser import parse_resource
import names
import random
from functools import partial
import os


BASEDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fhir')


class MockG(object):
    def __init__(self):
        self._nodep_buffers = {}

BUF = MockG()


def save_resource(resource_type, resource_data):
    '''
    save a resource to database and index its elements by search params
    '''
    valid, search_elements = parse_resource(resource_type, resource_data)
    assert valid
    resource = test_resource(resource_type, resource_data)
    index_resource(resource, search_elements, g=BUF)
    return resource


def rand_patient():
    '''
    generate random resource and index its elements by search params
    '''
    gender = 'female' if random.random() < 0.5 else 'male'
    first_name = names.get_first_name(gender=gender)
    last_name = names.get_last_name()
    full_name = '%s %s'% (first_name, last_name)
    data = {
        'resourceType': 'Patient',
        'text': {
            'status': 'generated',
            'div': "<div><p>%s</p></div>"% full_name
        },
        'name': [{'text': full_name}],
        'gender': gender
        }

    print 'Created Patient called %s'% full_name
    return save_resource('Patient', data)


def submit_web(resouce_type, data, user):
    global test_resource
    test_resource = partial(Resource, owner_id=user.email)
    save_resource(resouce_type, data)
    commit_buffers(BUF)


def load_from_file(path, relevant_dir):
    abspath = os.path.join(relevant_dir, path)
    print abspath
    with open(abspath) as f:
        return json.loads(f.read())


def init(resource):
    dir = os.path.join(BASEDIR, 'examples/' + resource)
    load_instance = partial(load_from_file, relevant_dir=dir)
    list_of_file = os.listdir(dir)
    list_of_instance = []
    for i in list_of_file:
        if '.json' in i:
            list_of_instance.append(i)
    availables = map(load_instance, list_of_instance)
    for i in availables:
        instance = dict(i)
        save_resource(resource, instance)
        print 'Created %s' % resource
        break

if __name__ == '__main__':
    from server import app
    with app.app_context():
        init('Practitioner')
        init('Organization')
        test_resource = partial(Resource, owner_id='name@mail.com')

        for _ in xrange(8):
            patient = rand_patient()

        commit_buffers(BUF)

