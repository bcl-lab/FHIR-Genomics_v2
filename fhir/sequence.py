'''
Specification for Sequence resource
'''
# "schema" for Sequence resource
sequence_resource = {
    'elements': [
        {
            'path': 'Sequence',
            'definition': {
                'min': 1,
                'max': '1',
                'type': [{'code': 'Resource'}]
            }
        }, {
            'path': 'Sequence.variation.type',
            'definition': {
                'min': 1,
                'max': '1',
                'type': [{'code': 'code'}]
            },
            'searchParam': {
                'name': 'variation-type',
                'type': 'token'
            }
        }, {
            'path': 'Sequence.variationID',
            'definition': {
                'min': 0,
                'max': '1',
                'type': [{'code': 'CodeableConcept'}]
            },
            'searchParam': {
                'name': 'variationID',
                'type': 'token'
            }
        },  {
            'path': 'Sequence.variation.referenceSeq',
            'definition': {
                'min': 0,
                'max': '1',
                'type': [{'code': 'CodeableConcept'}]
            }
        }, {
            'path': 'Sequence.variation.quantity',
            'definition': {
                'min': 0,
                'max': '1',
                'type': [{'code': 'Quantity'}]
            }
        }, {
            'path': 'Sequence.coordinate',
            'definition': {
                'min': 0,
                'max': '1',
            }
        }, {
            'path': 'Sequence.coordinate.chromosome',
            'definition': {
                'min': 0,
                'max': '1',
                'type': [{'code': 'CodeableConcept'}]
            },
            'searchParam': {
                'name': 'coordinate-chromosome',
                'type': 'token'
            }
        }, {
            'path': 'Sequence.coordinate.start',
            'definition': {
                'min': 0,
                'max': '1',
                'type': [{'code': 'integer'}]
            },
            'searchParam': {
                'name': 'coordinate-start',
                'type': 'number'
            }
        }, {
            'path': 'Sequence.coordinate.end',
            'definition': {
                'min': 0,
                'max': '1',
                'type': [{'code': 'integer'}]
            },
            'searchParam': {
                'name': 'coordinate-end',
                'type': 'number'
            }
        }, {
            'path': 'Sequence.coordinate.genomeBuild',
            'definition': {
                'min': 0,
                'max': '1',
                'type': [{'code': 'CodeableConcept'}]
            }
        }, {
            'path': 'Sequence.species',
            'definition': {
                'min': 0,
                'max': '1',
                'type': [{'code': 'CodeableConcept'}]
            },
            'searchParam': {
                'name': 'species',
                'type': 'token'
            }
        }, {
            'path': 'Sequence.observedAllele',
            'definition': {
                'min': 0,
                'max': '1',
                'type': [{'code': 'string'}]
            }
        },  {
            'path': 'Sequence.referenceAllele',
            'definition': {
                'min': 0,
                'max': '1',
                'type': [{'code': 'string'}]
            }
        },   {
            'path': 'Sequence.quality',
            'definition': {
                'min': 0,
                'max': '1',
            }
        },  {
            'path': 'Sequence.quality.start',
            'definition': {
                'min': 0,
                'max': '1',
                'type': [{'code': 'integer'}]
            }
        },  {
            'path': 'Sequence.quality.end',
            'definition': {
                'min': 0,
                'max': '1',
                'type': [{'code': 'integer'}]
            }
        },  {
            'path': 'Sequence.quality.score',
            'definition': {
                'min': 0,
                'max': '1',
                'type': [{'code': 'Quantity'}]
            }
        }, {
            'path': 'Sequence.quality.platform',
            'definition': {
                'min': 0,
                'max': '1',
                'type': [{'code': 'CodeableConcept'}]
            }
        },  {
            'path': 'Sequence.allelicState',
            'definition': {
                'min': 0,
                'max': '1',
                'type': [{'code': 'CodeableConcept'}]
            }
        },  {
            'path': 'Sequence.allelicFrequency',
            'definition': {
                'min': 0,
                'max': '1',
                'type': [{'code': 'decimal'}]
            }
        },  {
            'path': 'Sequence.copyNumberEvent',
            'definition': {
                'min': 0,
                'max': '1',
                'type': [{'code': 'CodeableConcept'}]
            }
        },  {
            'path': 'Sequence.readCoverage',
            'definition': {
                'min': 0,
                'max': '1',
                'type': [{'code': 'integer'}]
            }
        },  {
            'path': 'Sequence.repository',
            'definition': {
                'min': 0,
                'max': '1',
            }
        },  {
            'path': 'Sequence.repository.uri',
            'definition': {
                'min': 0,
                'max': '1',
                'type': [{'code': 'uri'}]
            }
        },  {
            'path': 'Sequence.repository.name',
            'definition': {
                'min': 0,
                'max': '1',
                'type': [{'code': 'string'}]
            }
        },  {
            'path': 'Sequence.repository.structure',
            'definition': {
                'min': 0,
                'max': '1',
                'type': [{'code': 'uri'}]
            }
        }, {
            'path': 'Sequence.repository.variantId',
            'definition': {
                'min': 0,
                'max': '1',
                'type': [{'code': 'string'}]
            }
        }, {
            'path': 'Sequence.repository.readGroupSetId',
            'definition': {
                'min': 0,
                'max': '1',
                'type': [{'code': 'string'}]
            }
        }
    ],
    'searchParams': {}
}

# collect search parameters of Sequence resource
for element in sequence_resource['elements']:
    if 'searchParam' not in element:
        continue
    param_name = element['searchParam']['name']
    param_type = element['searchParam']['type']
    sequence_resource['searchParams'][param_name] = param_type 

# this is used to inform the spec loader
# the exact types of reference search parameters
# E.g. patient is a search parameter of type Patient.
# Some parameter can be references to multiple types of resources
# so it's a list
sequence_reference_types = {
    'patient': ['Patient'],
    'lab': ['Procedure']
}
