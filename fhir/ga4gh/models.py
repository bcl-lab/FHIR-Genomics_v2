from flask import current_app
from datetime import datetime, timedelta
from urlparse import urljoin
from urllib import urlencode
import requests
import grequests
from error import GA4GHOauthError
from ..database import db
import json


REPOSITORIES = {
   'google': 'https://www.googleapis.com/genomics/v1beta2',
   'ncbi': 'http://trace.ncbi.nlm.nih.gov/Traces/gg',
   'ebi': 'http://193.62.52.16',
   'ensembl': 'http://grch37.rest.ensembl.org/ga4gh'
}
REPO_ID = 'google'
API_BASE = 'https://www.googleapis.com/genomics/v1beta2'
TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'
CONTENT_TYPE_HEADER = {'Content-Type': 'application/json; charset=UTF-8'}
KEY = 'AIzaSyB01GeX_HiuZbHCkZ-P5hJ7yUHVkwFS07Q'


def assert_good_resp(resp):
    '''
    assert that an HTTP response from Google Genomics is ok
    '''
    if resp.status_code != 200:
        raise GA4GHOauthError(resp.text)


def api_call(call_func):
    '''
    Decorator of method of GA4GHClient that calls GA4GH API.
    Updates token in the case of outdated token.
    '''
    def checked(self, *args, **kwargs):
        #if self.is_expired():
            #self.update(current_app.config['GA4GH_CONFIG'])
        return call_func(self, *args, **kwargs)

    return checked


class GA4GHClient(db.Model):
    '''
    GA4GH API client
    '''
    user_id = db.Column(db.String(200), primary_key=True)
    access_token = db.Column(db.String(150), nullable=True)
    refresh_token = db.Column(db.String(150), nullable=True)
    expire_at = db.Column(db.DateTime, nullable=True)
    # might be a demo account
    api_base = db.Column(db.String(200), nullable=True)
    __tablename__ = 'GA4GHClient'
    
    def __init__(self, code, user_id, ga4gh_config):
        '''
        Initialize a 23andme client given an authorization code
        by exchanging access_token with the code.
        '''
        post_data = {
            'client_id': ga4gh_config['client_id'],
            'client_secret': ga4gh_config['client_secret'],
            'grant_type': 'authorization_code',
            'redirect_uri': ga4gh_config['redirect_uri'],
            'scope': ga4gh_config['scope'],
            'code': code
        }
        resp = requests.post(TOKEN_URI, data=post_data)
        assert_good_resp(resp)
        self._set_tokens(resp.json())
        self.user_id = user_id
        self.api_base = API_BASE


    def _get_header(self):
        '''
        helper functions for getting HTTP Header to make 23andme API call
        '''
        return {'Authorization': 'Bearer '+self.access_token}

    def _set_tokens(self, credentials):
        '''
        set tokens (access and refresh) and calculate expiration time
        '''
        self.access_token = credentials['access_token']
        #self.refresh_token = credentials['refresh_token']
        # just to be safe, set expire time 100 seconds earlier than acutal expire time
        self.expire_at = datetime.now() + timedelta(seconds=int(credentials['expires_in']-100))

    def is_expired(self):
        '''
        check if the client's tokens have expired
        '''
        return datetime.now() > self.expire_at

    # TODO update
    def update(self, ga4gh_config):
        '''
        update tokens
        '''
        post_data = {
            'client_id': ga4gh_config['client_id'],
            'client_secret': ga4gh_config['client_secret'],
            'grant_type': 'refresh_token',
            'redirect_uri': ga4gh_config['redirect_uri'],
            'scope': ga4gh_config['scope'],
            'refresh_token': self.refresh_token
        }
        update_resp = requests.post(TOKEN_URI, data=post_data)
        assert_good_resp(update_resp)
        self._set_tokens(update_resp.json())
        db.session.add(self)
        db.session.commit()

    @api_call
    def get_resource(self, resource_type, resource_id):
        auth_header = self._get_header()
        resp = requests.get('%s/%s/%s?key=%s' % (API_BASE, resource_type, resource_id, KEY), headers=auth_header)
        return resp.json()

    @api_call
    def search_sets(self, resource_type, data):
        #data={'datasetIds': ['10473108253681171589']}
        resp = requests.post('%s/%s/search?key=%s'% (API_BASE, resource_type, KEY),
            data=json.dumps(data),
            headers=CONTENT_TYPE_HEADER)

        if resp.status_code != 200:
            raise Exception('Search on %s failed with arguments: %s -- %s' % (resp.url, data, resp.text))
        else:
            return resp.json()