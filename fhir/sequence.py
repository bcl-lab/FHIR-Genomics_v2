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
<<<<<<< HEAD
=======
            'path': 'Sequence.variationID',
            'definition': {
                'min': 0,
                'max': '1',
                'type': [{'code': 'CodeableConcpet'}]
            },
            'searchParam': {
                'name': 'variationID',
                'type': 'token'
             }
        }, {
            'path': 'Sequence.interpretation',
            'definition': {
                'min': 1,
                'max': '1',
                'type': [{'code': 'code'}]
            },
            'searchParam': {
                'name': 'interpretation',
                'type': 'token'
             }
        }, {
            'path': 'Sequence.patient',
            'definition': {
                'min': 1,
                'max': '1',
                'type': [{'code': 'Resource'}]
            },
            'searchParam': {
                'name': 'patient',
                'type': 'reference'
             }
        }, {
            'path': 'Sequence.timeDetermined',
            'definition': {
                'min': 0,
                'max': '1',
                'type': [{'code': 'dateTime'}]
            },
            'searchParam': {
                'name': 'time-determined',
                'type': 'date'
             }
        }, {
            'path': 'Sequence.variation',
            'definition': {
                'min': 0,
                'max': '*',
            }
        }, {
>>>>>>> origin/master
            'path': 'Sequence.variation.type',
            'definition': {
                'min': 1,
                'max': '1',
                'type': [{'code': 'code'}]
            },
            'searchParam': {
                'name': 'variation-type',
                'type': 'token'
<<<<<<< HEAD
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
=======
             }
        }, {
            'path': 'Sequence.variation.variationHGVS',
            'definition': {
                'min': 0,
                'max': '1',
                'type': [{'code': 'CodeableConcpet'}]
            },
            'searchParam': {
                'name': 'variation-variationHGVS',
                'type': 'token'
             }
        }, {
            'path': 'Sequence.variation.variationType',
            'definition': {
                'min': 0,
                'max': '1',
                'type': [{'code': 'CodeableConcpet'}]
            },
            'searchParam': {
                'name': 'variation-variationType',
                'type': 'token'
             }
        }, {
>>>>>>> origin/master
            'path': 'Sequence.variation.referenceSeq',
            'definition': {
                'min': 0,
                'max': '1',
<<<<<<< HEAD
                'type': [{'code': 'CodeableConcept'}]
            }
        }, {
            'path': 'Sequence.variation.quantity',
            'definition': {
                'min': 0,
                'max': '1',
                'type': [{'code': 'Quantity'}]
=======
                'type': [{'code': 'CodeableConcpet'}]
            },
            'searchParam': {
                'name': 'variation-referenceSeq',
                'type': 'token'
             }
        }, {
            'path': 'Sequence.allelicState',
            'definition': {
                'min': 0,
                'max': '1',
                'type': [{'code': 'CodeableConcpet'}]
>>>>>>> origin/master
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
<<<<<<< HEAD
                'type': [{'code': 'CodeableConcept'}]
=======
                'type': [{'code': 'CodeableConcpet'}]
>>>>>>> origin/master
            },
            'searchParam': {
                'name': 'coordinate-chromosome',
                'type': 'token'
<<<<<<< HEAD
            }
=======
             }
>>>>>>> origin/master
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
<<<<<<< HEAD
            }
=======
             }
>>>>>>> origin/master
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
<<<<<<< HEAD
            }
=======
             }
>>>>>>> origin/master
        }, {
            'path': 'Sequence.coordinate.genomeBuild',
            'definition': {
                'min': 0,
                'max': '1',
<<<<<<< HEAD
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
=======
                'type': [{'code': 'CodeableConcpet'}]
            }
        }, {
            'path': 'Sequence.gene',
            'definition': {
                'min': 0,
                'max': '1',
                'type': [{'code': 'CodeableConcpet'}]
            },
            'searchParam': {
                'name': 'gene',
                'type': 'token'
             }
        },  {
            'path': 'Sequence.region',
            'definition': {
                'min': 0,
                'max': '1',
                'type': [{'code': 'CodeableConcpet'}]
            }
        },  {
            'path': 'Sequence.species',
            'definition': {
                'min': 0,
                'max': '1',
                'type': [{'code': 'CodeableConcpet'}]
            },
            'searchParam': {
                'name': 'species',
                'type': 'token'
             }
        },  {
            'path': 'Sequence.source',
            'definition': {
                'min': 1,
                'max': '1',
                'type': [{'code': 'CodeableConcpet'}]
            },
            'searchParam': {
                'name': 'source',
                'type': 'token'
             }
        }, {
            'path': 'Sequence.request',
            'definition': {
                'min': 0,
                'max': '1',
                'type': [{'code': 'Resource'}]
            },
            'searchParam': {
                'name': 'request',
                'type': 'reference'
             }
        }, {
            'path': 'Sequence.analysis',
            'definition': {
                'min': 0,
                'max': '*',
            }
        }, {
            'path': 'Sequence.analysis.target',
            'definition': {
                'min': 1,
                'max': '1',
                'type': [{'code': 'CodeableConcpet'}]
            },
            'searchParam': {
                'name': 'analysis-target',
                'type': 'token'
             }
        }, {
            'path': 'Sequence.analysis.type',
            'definition': {
                'min': 1,
                'max': '1',
                'type': [{'code': 'CodeableConcpet'}]
            },
            'searchParam': {
                'name': 'analysis-type',
                'type': 'token'
             }
        }, {
            'path': 'Sequence.analysis.interpretation',
            'definition': {
                'min': 0,
                'max': '1',
                'type': [{'code': 'CodeableConcpet'}]
            }
        }, {
            'path': 'Sequence.analysis.confidence',
            'definition': {
                'min': 1,
                'max': '1',
                'type': [{'code': 'code'}]
            }
        }, {
            'path': 'Sequence.gaRepository',
>>>>>>> origin/master
            'definition': {
                'min': 0,
                'max': '1',
                'type': [{'code': 'uri'}]
            }
<<<<<<< HEAD
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
=======
        }, {
            'path': 'Sequence.gaVariantSet',
            'definition': {
                'min': 0,
                'max': '*',
                'type': [{'code': 'string'}]
            }
        }, {
            'path': 'Sequence.gaCallSet',
>>>>>>> origin/master
            'definition': {
                'min': 0,
                'max': '1',
                'type': [{'code': 'string'}]
            }
        }, {
<<<<<<< HEAD
            'path': 'Sequence.repository.readGroupSetId',
=======
            'path': 'Sequence.ReadGroup',
>>>>>>> origin/master
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
