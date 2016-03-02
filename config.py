# settings for Postgres
PGUSERNAME = 'lix'
PGPASSWORD = 'password'
DBNAME = 'fhir'

APP_CONFIG = {
		# SQL connection url
        #'SQLALCHEMY_DATABASE_URI': "postgresql+psycopg2://%s:%s@localhost/%s"% (
        #    PGUSERNAME,
        #    PGPASSWORD,
        #    DBNAME),
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///fhir.db',
		# drop your own 23andme API credentials here
		# WARNING: don't touch 'scope'
        'TTAM_CONFIG': {
            'redirect_uri': 'http://localhost:5000/ttam/recv_redirect',
            'client_id': '7d12b72cdc040f0b31a1a5606e4902f5',
            'client_secret': 'd68b746d63e53dff0cd65d3260940f9b',
            'scope': 'basic names genomes',
            'auth_uri': 'http://api.23andme.com/authorize'
        },

        'GA4GH_CONFIG': {
            'redirect_uri': 'http://localhost:5000/ga4gh/recv_redirect',
            'client_id': '849738343457-1d891ektv7o9vjeff1dk1p9shrid5bp9.apps.googleusercontent.com',
            'client_secret': 'F11jjtuEA66KqOYn4RcBBhPk',
            'scope': 'basic names genomes',
            'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
            'scope': 'https://www.googleapis.com/auth/genomics.readonly'
        }
}

# Put Your host name here
HOST = 'localhost:2048'

# replace this with directory where you put your FHIR specification,
# which, should be roughly in this a format like this the `/site` directory 
# in this zipped directory http://www.hl7.org/fhir/fhir-spec.zip.
# NOTE: You SHOULDN'T be concerned about this if you don't wish to load different
# version of FHIR than the one we are using (FHIR v0.0.82).
FHIR_SPEC_DIR = '/Users/apple/Documents/fhir-spec/site'
# the example resource parser right now is still pretty slow
# also, due to the fact that SQLAlchemy is not very good at bulk insert,
# if the vcf file is too large, the example loader is gonna run for decades
MAX_SEQ_PER_FILE = 3000
# ratio between Conditions and Sequences, the example loader uses this to
# randomly create GeneticObservation, which associates the two resources.
CONDITION_TO_SEQ_RATIO = 0.1

#GOOGLE_API_KEY = 'AIzaSyB01GeX_HiuZbHCkZ-P5hJ7yUHVkwFS07Q'
#SECRET_KEY = 'hi'




