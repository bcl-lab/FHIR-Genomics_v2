'''
Load randomly generated example data into the database
'''
from flask import g
from fhir.models import db, Resource, User, Client, commit_buffers
from fhir.indexer import index_resource
from fhir.fhir_parser import parse_resource
from fhir.fhir_spec import RESOURCES
import names
from argparse import ArgumentParser
import random
from functools import partial
import json
import os
import fhir.ga4gh
from vcf import VCFReader

BASEDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fhir')

class MockG(object):
    def __init__(self):
        self._nodep_buffers = {}

BUF = MockG()

RELIABILITIES = ['questionable', 'ongoing', 'ok', 'calibrating', 'early']
INTERPRETATIONS = [
    {
        'code': 'L',
        'display': 'Below low normal',
        'system': 'http://hl7.org/fhir/vs/observation-interpretation'
    }, { 
        'code': 'IND',
        'display': 'Intermediate',
        'system': 'http://hl7.org/fhir/vs/observation-interpretation'
    }, { 
        'code': 'H',
        'display': 'Above high normal',
        'system': 'http://hl7.org/fhir/vs/observation-interpretation'
    }, { 
        'code': 'NEG',
        'display': 'Negative',
        'system': 'http://hl7.org/fhir/vs/observation-interpretation'
    }, { 
        'code': 'POS',
        'display': 'Positive',
        'system': 'http://hl7.org/fhir/vs/observation-interpretation'
    }
]


def save_resource(resource_type, resource_data):
    '''
    save a resource to database and index its elements by search params
    '''
    valid, search_elements = parse_resource(resource_type, resource_data)
    #assert valid
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


def load_patients_by_samples(samples):
    return {sample: rand_patient() for sample in samples}


def load_labs_by_patients(patients):
    # patients is a key-value pair of sample and patient
    return {sample: rand_lab(patients[sample])
        for sample in patients.keys()}

#'source': 'germline' if random.random() < 0.5 else 'somatic',

def load_vcf_example(vcf_file):
    reader = VCFReader(filename=vcf_file)
    for record in reader:
        sequence_tmpl = {
            'text': {'status': 'generated'},
            'resourceType': 'Sequence',
            'coordinate': {
                'chromosome': {'text': record.CHROM},
                'start': record.POS,
                'end': record.end,
                'genomeBuild': {'text': 'GRCh37'}
            },

            'species': {'text': 'Homo sapiens',
                        'coding': [{
                            'system': 'http://snomed.info/sct',
                            'code': '337915000'}]},
            'referenceAllele': record.REF
        }
        for sample in record.samples:
            sample_id = sample.sample
            reads = sample.gt_bases
            if '/' in reads:
                delimiter = '/'
            elif '|' in reads:
                delimiter = '|'
            else:
                delimiter = '.'
            seq_data = dict(sequence_tmpl)
            seq_data['observedAllele'] = reads.split(delimiter)[1]
            # get name of the variant
            variant_id = record.ID
            variant = variant_id if variant_id is not None else 'anonymous variant'
            seq_data['variantID'] = {'text': variant_id}
            seq_data['text']['div']  = '<div>Genotype of %s is %s</div>'% (variant, reads)
            sequence = save_resource('Sequence', seq_data)
            print 'Created Sequence at %s:%s-%s'% (record.CHROM, record.POS, record.end)



def init_superuser():
    superuser = User(email='super')
    db.session.add(superuser)
    global test_resource
    test_resource = partial(Resource, owner_id=superuser.email)  



if __name__ == '__main__':
    from server import app
    with app.app_context():
        init_superuser()
        patient_ids = []
        sequence_ids = []
        for _ in xrange(8):
            patient = rand_patient()
            patient_ids.append(patient.get_reference())
        commit_buffers(BUF) 
