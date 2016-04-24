import os
from vcf import VCFReader
import random

def load_vcf_example(vcf_file):
    reader = VCFReader(filename=vcf_file)
    for record in reader:
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
                 'windowEnd': record.end
                 }],

            'variation': {'start': record.POS,
                          'end': record.end,
                          'observedAllele': str(record.ALT[0]),
                          'referenceAllele': record.REF
                          },

            'species': {'text': 'Homo sapiens',
                        'coding': [{
                            'system': 'http://snomed.info/sct',
                            'code': '337915000'}]}
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
            print reads, reads.split(delimiter), record.REF
            seq_data['observedAllele'] = reads.split(delimiter)
            # get name of the variant
            variant_id = record.ID
            variant = variant_id if variant_id is not None else 'anonymous variant'
            seq_data['variantID'] = variant_id
            seq_data['text']['div']  = '<div>Genotype of %s is %s</div>'% (variant, reads)
            print 'Created Sequence at %s:%s-%s'% (record.CHROM, record.POS, record.end)
            break



BASEDIR = 'fhir'
for example_file in os.listdir(os.path.join(BASEDIR, 'examples/vcf')):
    load_vcf_example(os.path.join(BASEDIR, 'examples/vcf', example_file))

