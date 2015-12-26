__author__ = 'HemingY'
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
PRE_EXTENSION_OBS_URL = 'http://hl7.org/fhir/StructureDefinition/observation-genetics'
PRE_EXTENSION_REPORT_URL = 'http://hl7.org/fhir/StructureDefinition/diagnosticreport-genetics'

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


def rand_observations(patientId, index):
    gene_name = gene_names[index]
    f = file (BASEDIR + '/examples/loinc-code.txt')
    code, text = None, None
    for line in f.readlines():
        line = line.split('\t')
        if gene_name and gene_name + ' gene mutation analysis' in line[1]:
            code = line[0]
            text = line[1]
            break
    if not code:
        code = '55233-1'
        text = 'Genetic analysis master panel'

    observation = {
        'resourceType': 'Observation',

        'category': {'text': 'Laboratory',
                     'coding': [{
                                'system': "http://hl7.org/fhir/ValueSet/observation-category",
                                'code': "laboratory"
                                }]
                     },
        'code': {'text': text,
                 'coding': [{
                            'system': "http://loinc.org",
                            'code': code
                            }]
                 },

        'subject': patientId,

        'status': 'final'

    }
    
    if random.random() < 0.2:
        value = {'text': 'Negative',
                 'coding': [{
                           'system': "http://snomed.info/sct",
                           'code': "260385009"
                            }]
                 }
    else:
        value = {'text': 'Positive',
                 'coding': [{
                            'system': "http://snomed.info/sct",
                            'code': "10828004"
                            }]
                 }
    observation['value'] = value

    extension = []
    # get source randomly
    if random.random() < 0.5:
        source = {'url': PRE_EXTENSION_OBS_URL+'Source',
                  'valueCodeableConcept': {'text': 'Somatic',
                                           'coding': [{
                                                      'system': "http://hl7.org/fhir/LOINC-48002-0-answerlist",
                                                      'code': "LA6684-0"
                                                      }]}}

    else:
        source = {'url': PRE_EXTENSION_OBS_URL+'Source',
                  'valueCodeableConcept': {'text': 'Germline',
                                           'coding': [{
                                                      'system': "http://hl7.org/fhir/LOINC-48002-0-answerlist",
                                                      'code': "LA6683-2"
                                                      }]}}
    extension.append(source)

    # get gene name
    if gene_name:
        gene_id = None
        f = file(os.path.join(BASEDIR, 'examples/genename/genenames-HGNC.txt'))
        for line in f.readlines():
            lis_line = line[0:-1].split('\t')
            if lis_line[1] == gene_name:
                gene_id = lis_line[0].split(':')[1]
                break
        if gene_id:
            gene = {'url': PRE_EXTENSION_OBS_URL+'Gene',
                    'valueCodeableConcept': {'text': gene_name,
                                             'coding':[{
                                                        'system': 'http://www.genenames.org/',
                                                        'code': gene_id
                                                        }]}}
        else:
            gene = {'url': PRE_EXTENSION_OBS_URL+'Gene',
                    'valueCodeableConcept': {'text': gene_name}}
        extension.append(gene)

    # get sequence reference
    sequence = {'url': PRE_EXTENSION_OBS_URL + 'Sequence',
                'valueReference': sequence_ids[index]}
    extension.append(sequence)

    observation['extension'] = extension
    print 'Created Observation-genetics instance'
    return save_resource('Observation', observation)


def load_vcf_example(vcf_file):
    reader = VCFReader(filename=vcf_file)
    count = 0
    serial = 0
    for record in reader:
        serial += 1
        if serial % 1000 != 0:
            continue
        sequence_tmpl = {
            'text': {'status': 'generated'},
            'resourceType': 'Sequence',
            'type': 'DNA',
            'coordinate': [
                {
                'chromosome': {'text': record.CHROM},
                'start': record.POS,
                'end': record.end,
                'genomeBuild': {'text': 'GRCh37'}
            }],

            'species': {'text': 'Homo sapiens',
                        'coding': [{
                            'system': 'http://snomed.info/sct',
                            'code': '337915000'}]},
            'referenceAllele': record.REF
        }

        seq_data = dict(sequence_tmpl)

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

            seq_data['variationID'] = [{
                                       'coding': [{
                                                   'system': 'http://www.ncbi.nlm.nih.gov/projects/SNP/snp_ref.cgi',
                                                   'code': variant_id
                                                   }]}]

            seq_data['text']['div']  = '<div>Genotype of %s is %s</div>'% (variant, reads)

            gene_name = record.INFO.get('SNPEFF_GENE_NAME')

            sequence = save_resource('Sequence', seq_data)
            print 'Created Sequence at %s:%s-%s'% (record.CHROM, record.POS, record.end)
            count += 1
            sequence_ids.append(sequence.get_reference())
            gene_names.append(gene_name)
        if MAX_SEQ_PER_FILE is not None and count >= MAX_SEQ_PER_FILE:
            break


def create_diagnosticreport(patientId):
    conditionId = rand_conditions(patientId)
    print conditionId
    performerId = rand_practitioner(patientId)
    extension = []
    assessed_condition = {'url': PRE_EXTENSION_REPORT_URL + 'AssessedCondition',
                          'valueReference': conditionId}
    extension.append(assessed_condition)

    results = []
    sequence_index = []
    for _ in xrange(random.randint(0,10)):
        index = random.randint(0,len(sequence_ids)-1)
        if random.randint(0,len(sequence_ids)-1) not in sequence_index:
            sequence_index.append(index)
            results.append(rand_observations(patientId, index).get_reference())

    data = {
        'extension': extension,
        'resourceType': 'DiagnosticReport',
        'status': 'final',
        'code': {'text': 'Gene mutation analysis'},
        'subject': patientId,
        'effectiveDateTime': rand_date(),
        'issued': rand_date(),
        'performer': performerId,
        'result': results
        }

    return save_resource('DiagnosticReport', data)


def rand_practitioner(patientId):
    '''
    randomly assign a set of conditions to a poor patient
    '''
    practitioner = random.sample(available_practitioner, 1)
    practitionerId = 0
    for cond_tmpl in practitioner:
        practitioner = dict(cond_tmpl)
        practitioner['subject'] = patientId
        practitioner = save_resource('Practitioner', practitioner)
        practitionerId = practitioner.get_reference()
        print 'Created practitioner'
        break
    return practitionerId


def init_practitioner():
    practitioner_dir = os.path.join(BASEDIR, 'examples/practitioner')
    global available_practitioner
    available_practitioner = map(load_practitioner_from_file, os.listdir(practitioner_dir))


def load_practitioner_from_file(path):
    path = 'practitioner-example.json'
    print path
    abspath = os.path.join(BASEDIR, 'examples/practitioner', path)
    with open(abspath) as practitioner_f:
        return json.loads(practitioner_f.read())


def rand_conditions(patientid):
    '''
    randomly assign a set of conditions to a poor patient
    '''
    conditions = random.sample(available_conditions,
                            random.randint(1, len(available_conditions)))
    conditionid = 0
    for cond_tmpl in conditions:
        condition = dict(cond_tmpl)
        condition['patient'] = patientid
        conditionid = save_resource('Condition', condition).get_reference()
        print 'Created condition %s'% condition['code'].get('text', '')
        break
    return conditionid


def load_condition_from_file(path):
    print path
    abspath = os.path.join(BASEDIR, 'examples/conditions', path)
    with open(abspath) as condition_f:
        return json.loads(condition_f.read())


def init_conditions():
    condition_dir = os.path.join(BASEDIR, 'examples/conditions')
    global available_conditions
    available_conditions = map(load_condition_from_file, os.listdir(condition_dir))


def load_specimen_from_file(path):
    print path
    abspath = os.path.join(BASEDIR, 'examples/specimen', path)
    with open(abspath) as specimen_f:
        return json.loads(specimen_f.read())


def rand_date():
    date = "%d-%d-%dT%d:%d:00+01:00" % (random.randint(2010, 2015),
                                        random.randint(1, 11),
                                        random.randint(1, 27),
                                        random.randint(0, 23),
                                        random.randint(0, 59))
    return date


def init_superuser():
    superuser = User(email='super')
    db.session.add(superuser)
    global test_resource
    test_resource = partial(Resource, owner_id=superuser.email)


if __name__ == '__main__':
    from server import app
    with app.app_context():
        init_superuser()
        init_conditions()
        init_practitioner()
        patient_ids = []
        sequence_ids = []
        gene_names = []

        for example_file in os.listdir(os.path.join(BASEDIR, 'examples/vcf')):
            load_vcf_example(os.path.join(BASEDIR, 'examples/vcf', example_file))
        sequence_amount = len(sequence_ids)
        '''
        for _ in xrange(50):
            patient = rand_patient()
            create_diagnosticreport(patient.get_reference())
        '''
        commit_buffers(BUF)
