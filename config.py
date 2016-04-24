# settings for Postgres
PGUSERNAME = 'username'
PGPASSWORD = 'password'
DBNAME = 'xyz'

APP_CONFIG = {
    # SQL_connection_url
    # 'SQLALCHEMY_DATABASE_URI': "postgresql+psycopg2://%s:%s@localhost/%s"% (
    #   PG_USERNAME,
    #   PG_PASSWORD,
    #   DB_NAME),
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///fhir.db',

    # drop your own 23andme API credentials here
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
# version of FHIR than the one we are using (FHIR v1.4.0).
FHIR_SPEC_DIR = '/Users/apple/Documents/fhir-spec/site'

# GOOGLE_API_KEY = 'AIzaSyB01GeX_HiuZbHCkZ-P5hJ7yUHVkwFS07Q'
# SECRET_KEY = 'hi'




