__author__ = 'HemingY'
'''
Load randomly generated example data into the database
'''
from fhir.models import db, Resource, User, commit_buffers
from fhir.indexer import index_resource
from fhir.fhir_parser import parse_resource
import names
import random
from functools import partial
import json
import os
from vcf import VCFReader

BASEDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fhir')
MAX_SEQ_PER_FILE = 110
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
    variant_id = variant_ids[index]
    f = file(BASEDIR + '/examples/loinc-code.txt')
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
        'resourceType': 'observationforgenetics',

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
        valueCodeableConcept = {'text': 'Negative',
                 'coding': [{
                           'system': "http://snomed.info/sct",
                           'code': "260385009"
                            }]
                 }
    else:
        valueCodeableConcept = {'text': 'Positive',
                 'coding': [{
                            'system': "http://snomed.info/sct",
                            'code': "10828004"
                            }]
                 }
    observation['valueCodeableConcept'] = valueCodeableConcept

    extension = []
    # get source randomly
    if random.random() < 0.5:
        source = {'url': PRE_EXTENSION_OBS_URL+'GenomicSourceClass',
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
    # get variant_id
    if variant_id:
        variant = {'url': PRE_EXTENSION_OBS_URL+'DNAVariationId',
                   'valueCodeableConcept': {'coding': [{'system': 'http://www.ncbi.nlm.nih.gov/projects/SNP/snp_ref.cgi',
                                                        'code': variant_id}]
                                            }}
        extension.append(variant)

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
                                             'coding': [{
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
    return save_resource('observationforgenetics', observation)


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
            'referenceSeq': [
                {'chromosome': {'text': record.CHROM,
                                'coding': [{'system': 'http://hl7.org/fhir/ValueSet/chromosome-human',
                                            'code': record.CHROM}]},
                 'genomeBuild': {'text': 'GRCh37'},
                 'referenceSeqId': {'coding': [{'system': 'http://www.ensembl.org',
                                                'code': record.INFO.get('SNPEFF_TRANSCRIPT_ID')}]},
                 'windowStart': record.POS,
                 'windowEnd': int(record.end)+1
                 }],

            'variation': {'start': record.POS,
                          'end': int(record.end)+1,
                          'observedAllele': str(record.ALT[0]),
                          'referenceAllele': record.REF
                          },

            'species': {'text': 'Homo sapiens',
                        'coding': [{
                            'system': 'http://snomed.info/sct',
                            'code': '337915000'}]}
        }

        seq_data = dict(sequence_tmpl)

        variant_id = record.ID
        variant_ids.append(variant_id)
        variant = variant_id if variant_id is not None else 'anonymous variant'

        seq_data['text']['div']  = '<div>Genotype of %s is %s/%s</div>'% (variant, record.REF, str(record.ALT[0]))

        gene_name = record.INFO.get('SNPEFF_GENE_NAME')
        gene_names.append(gene_name)
        sequence = save_resource('Sequence', seq_data)
        print 'Created Sequence at %s:%s-%s'% (record.CHROM, record.POS, record.end)
        count += 1
        sequence_ids.append(sequence.get_reference())
        if MAX_SEQ_PER_FILE is not None and count >= MAX_SEQ_PER_FILE:
            break


def create_diagnosticreport(patient_id):
    condition_id = rand_conditions(patient_id)
    print condition_id
    performer_id = rand_practitioner(patient_id)
    extension = []
    assessed_condition = {'url': PRE_EXTENSION_REPORT_URL + 'AssessedCondition',
                          'valueReference': condition_id}
    extension.append(assessed_condition)

    results = []
    sequence_index = []
    for _ in xrange(random.randint(0,10)):
        index = random.randint(0,len(sequence_ids)-1)
        if random.randint(0,len(sequence_ids)-1) not in sequence_index:
            sequence_index.append(index)
            results.append(rand_observations(patient_id, index).get_reference())

    data = {
        'resourceType': 'reportforgenetics',
        'extension': extension,
        'status': 'final',
        'code': {'text': 'Gene mutation analysis'},
        'subject': patient_id,
        'effectiveDateTime': rand_date(),
        'issued': rand_date(),
        'performer': performer_id,
        'result': results
        }

    return save_resource('reportforgenetics', data)


def rand_practitioner(patient_id):
    '''
    randomly assign a set of conditions to a poor patient
    '''
    practitioner = random.sample(available_practitioner, 1)
    practitioner_id = 0
    for cond_tmpl in practitioner:
        practitioner = dict(cond_tmpl)
        practitioner['subject'] = patient_id
        practitioner = save_resource('Practitioner', practitioner)
        practitioner_id = practitioner.get_reference()
        print 'Created practitioner'
        break
    return practitioner_id


def init_practitioner():
    practitioner_dir = os.path.join(BASEDIR, 'examples/Practitioner')
    global available_practitioner
    load_instance = partial(load_practitioner_from_file, relevant_dir=practitioner_dir)
    list_of_file = os.listdir(practitioner_dir)
    list_of_instance = []
    for i in list_of_file:
        if '.json' in i:
            list_of_instance.append(i)
    available_practitioner = map(load_instance, list_of_instance)


def load_practitioner_from_file(path, relevant_dir):
    abspath = os.path.join(relevant_dir, path)
    with open(abspath) as f:
        return json.loads(f.read())


def rand_conditions(patient_id):
    '''
    randomly assign a set of conditions to a poor patient
    '''
    conditions = random.sample(available_conditions,
                            random.randint(1, len(available_conditions)))
    condition_id = 0
    for cond_tmpl in conditions:
        condition = dict(cond_tmpl)
        condition['patient'] = patient_id
        condition_id = save_resource('Condition', condition).get_reference()
        print 'Created condition %s'% condition['code'].get('text', '')
        break
    return condition_id


def load_condition_from_file(path):
    abspath = os.path.join(BASEDIR, 'examples/conditions', path)
    with open(abspath) as condition_f:
        return json.loads(condition_f.read())


def init_conditions():
    condition_dir = os.path.join(BASEDIR, 'examples/conditions')
    global available_conditions
    available_conditions = map(load_condition_from_file, os.listdir(condition_dir))


def rand_date():
    date = "%d-%d-%dT%d:%d:00+01:00" % (random.randint(2010, 2015),
                                        random.randint(1, 11),
                                        random.randint(1, 27),
                                        random.randint(0, 23),
                                        random.randint(0, 59))
    return date


def load_from_file(path, relevant_dir):
    abspath = os.path.join(relevant_dir, path)
    with open(abspath) as f:
        return json.loads(f.read())


def init(resource):
    dir = os.path.join(BASEDIR, 'examples/' + resource)
    ids = []
    load_instance = partial(load_from_file, relevant_dir=dir)
    list_of_file = os.listdir(dir)
    list_of_instance = []
    for i in list_of_file:
        if '.json' in i:
            list_of_instance.append(i)
    availables = map(load_instance, list_of_instance)
    for i in availables:
        instance = dict(i)
        resource_instance = save_resource(resource, instance)
        print 'Created %s' % resource
        ids.append(resource_instance.get_reference())
    return ids


def init_superuser():
    superuser = User(email='super')
    db.session.add(superuser)
    global test_resource
    test_resource = partial(Resource, owner_id=superuser.email)


if __name__ == '__main__':
    from server import app
    with app.app_context():
        init_superuser()
        init_practitioner()
        init('Organization')
        init_conditions()
        patient_ids = []
        sequence_ids = []
        gene_names = []
        variant_ids = []

        for example_file in os.listdir(os.path.join(BASEDIR, 'examples/vcf')):
            load_vcf_example(os.path.join(BASEDIR, 'examples/vcf', example_file))
        sequence_amount = len(sequence_ids)


        for _ in xrange(10):
            patient = rand_patient()
            create_diagnosticreport(patient.get_reference())

        commit_buffers(BUF)
