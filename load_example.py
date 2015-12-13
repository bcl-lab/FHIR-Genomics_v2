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
MAX_SEQ_PER_FILE = 10

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


def load_vcf_example(vcf_file):
    reader = VCFReader(filename=vcf_file)
    count = 0
    serial = 0
    for record in reader:
        serial += 1
        if serial % 100 != 0:
            continue
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
            seq_data['variantID'] = {'coding': [{
                                                'system': 'http://www.ncbi.nlm.nih.gov/projects/SNP/snp_ref.cgi',
                                                'code': variant_id
                                                }]}

            seq_data['text']['div']  = '<div>Genotype of %s is %s</div>'% (variant, reads)

            # get name of the gene
            if record.INFO.get('SNPEFF_GENE_NAME'):
                gene_name = record.INFO.get('SNPEFF_GENE_NAME')
                gene_id = None
                for genename_file in os.listdir(os.path.join(BASEDIR, 'examples/genename')):
                    f = file(os.path.join(BASEDIR, 'examples/genename/genenames-HGNC.txt'))
                    for line in f.readlines():
                        lis_line = line[0:-1].split('\t')
                        if lis_line[1] == gene_name:
                            gene_id = lis_line[0].split(':')[1]
                            break
                if gene_id:
                    seq_data['gene'] = {'text': gene_name,
                                        'coding':[{
                                            'system': 'http://www.genenames.org/',
                                            'code': gene_id
                                        }]}
                else:
                    seq_data['gene'] = {'text': gene_name}

            # get source
            if random.random() < 0.5:
                seq_data['source'] = {'text': 'Somatic',
                                      'coding': [{
                                          'system': "http://hl7.org/fhir/LOINC-48002-0-answerlist",
                                          'code': "LA6684-0"
                                      }]}
            else:
                seq_data['source'] = {'text': 'Germline',
                                      'coding': [{
                                          'system': "http://hl7.org/fhir/LOINC-48002-0-answerlist",
                                          'code': "LA6683-2"
                                      }]}
            sequence = save_resource('Sequence', seq_data)
            print 'Created Sequence at %s:%s-%s'% (record.CHROM, record.POS, record.end)
            count += 1
            sequence_ids.append(sequence.get_reference())
                    
        if MAX_SEQ_PER_FILE is not None and count >= MAX_SEQ_PER_FILE:
            break


def rand_date():
    date = "%d-%d-%dT%d:%d:00+01:00" % (random.randint(2010, 2015),
                                        random.randint(1, 12),
                                        random.randint(1, 28),
                                        random.randint(0, 23),
                                        random.randint(0, 60))
    return date


def make_observation():
    observation = {
        'resourceType': 'Observation',

        'category': {'text': 'Laboratory',
                     'coding': [{
                                'system': "http://hl7.org/fhir/ValueSet/observation-category",
                                'code': "laboratory"
                                }]
                     },
        'code': {'text': 'DNA Analysis Discrete Sequence Variant Panel',
                 'coding': [{
                            'system': "http://loinc.org",
                            'code': "laboratory"
                            }]
                 },

        'subject': patient_ids[random.randint(0, len(patient_ids)-1)],

        'status': 'final',

        'valueReference': sequence_ids[random.randint(0, len(sequence_ids)-1)],

        'speciment': 
    }

    print 'Created Observation (Genetic Observation)'
    return save_resource('Observation', observation)


def init_superuser():
    superuser = User(email='super')
    db.session.add(superuser)
    global test_resource
    test_resource = partial(Resource, owner_id=superuser.email)  


def load_condition_from_file(path):
    print path
    abspath = os.path.join(BASEDIR, 'examples/conditions', path)
    with open(abspath) as condition_f:
        return json.loads(condition_f.read())


def load_specimen_from_file(path):
    print path
    abspath = os.path.join(BASEDIR, 'examples/specimen', path)
    with open(abspath) as specimen_f:
        return json.loads(specimen_f.read())


def init_conditions():
    condition_dir = os.path.join(BASEDIR, 'examples/conditions')
    global available_conditions
    available_conditions = map(load_condition_from_file, os.listdir(condition_dir))


def init_specimen():
    specimen_dir = os.path.join(BASEDIR, 'examples/specimen')
    global available_specimens
    available_specimens = map(load_specimen_from_file, os.listdir(specimen_dir))


def init_practitioner():
    condition_dir = os.path.join(BASEDIR, 'examples/practitioner')
    global available_practitioner
    available_conditions = map(load_condition_from_file, os.listdir(condition_dir))

if __name__ == '__main__':
    from server import app
    with app.app_context():
        init_superuser()
        patient_ids = []
        sequence_ids = []

        for _ in xrange(8):
            patient = rand_patient()
            patient_ids.append(patient.get_reference())

        for example_file in os.listdir(os.path.join(BASEDIR, 'examples/vcf')):
            load_vcf_example(os.path.join(BASEDIR, 'examples/vcf', example_file))
        sequence_amount = len(sequence_ids)

        # randomize the sequence
        for i in range (0, int(sequence_amount/10)):
            x = random.randint(0, sequence_amount-1)
            y = random.randint(0, sequence_amount-1)
            sequence_ids[x], sequence_ids[y] = sequence_ids[y], sequence_ids[x]

        # create Observation resource
        for _ in xrange(8):
            make_observation()

        commit_buffers(BUF) 
