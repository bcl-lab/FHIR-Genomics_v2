from flask import current_app
from datetime import datetime, timedelta
from urlparse import urljoin
from urllib import urlencode
import requests
import grequests
from error import BaseSpaceOAuthError
from ..database import db

TOKEN_URI = 'https://api.basespace.illumina.com/v1pre3/oauthv2/token'
API_BASE = 'https://api.basespace.illumina.com/v1pre3/'

def assert_good_resp(resp):
    '''
    assert that an HTTP response from basespace is ok
    '''
    if resp.status_code != 200:
        raise BaseSpaceOAuthError(resp.text)


def api_call(call_func):
    '''
    Decorator of method of BaseSpaceClient that calls BaseSpace API.
    Updates token in the case of outdated token.
    ''' 
    def checked(self, *args, **kwargs):
        if self.is_expired():
            self.update(current_app.config['BS_CONFIG'])
        return call_func(self, *args, **kwargs)

    return checked


# TODO test demo data
class BaseSpaceClient(db.Model):
    '''
    BaseSpace API client
    '''
    user_id = db.Column(db.String(200), db.ForeignKey('User.email'), primary_key=True)
    access_token = db.Column(db.String(150), nullable=True)
    refresh_token = db.Column(db.String(150), nullable=True)
    expire_at = db.Column(db.DateTime, nullable=True)
    # might be a demo account
    api_base = db.Column(db.String(200), nullable=True)
    profiles = db.Column(db.Text, nullable=True)
    __tablename__ = 'BaseSpaceClient'
    
    def __init__(self, code, user_id, bs_config):
        '''
        Initialize a BaseSpace client given an authorization code
        by exchanging access_token with the code.
        '''
        post_data = {
            'client_id': bs_config['client_id'],
            'client_secret': bs_config['client_secret'],
            'grant_type': 'authorization_code',
            'redirect_uri': bs_config['redirect_uri'],
            'scope': bs_config['scope'],
            'code': code
        }
        resp = requests.post(TOKEN_URI, data=post_data)
        assert_good_resp(resp)
        self._set_tokens(resp.json())
        self.api_base = API_BASE
        patients = self.get_patients()
        self.profiles = ' '.join(p['id'] for p in patients)
        self.user_id = user_id

    def _set_tokens(self, credentials):
        '''
        set tokens (access and refresh) and calculate expiration time
        '''
        self.access_token = credentials['access_token']
        self.refresh_token = credentials['refresh_token']
        # just to be safe, set expire time 100 seconds earlier than acutal expire time
        self.expire_at = datetime.now() + timedelta(seconds=int(credentials['expires_in']-100))

    def is_expired(self):
        '''
        check if the client's tokens have expired
        '''
        return datetime.now() > self.expire_at

    def update(self, bs_config):
        '''
        update tokens
        '''
        post_data = {
            'client_id': bs_config['client_id'],
            'client_secret': bs_config['client_secret'],
            'grant_type': 'refresh_token',
            'redirect_uri': bs_config['redirect_uri'],
            'scope': bs_config['scope'],
            'refresh_token': self.refresh_token
        }
        update_resp = requests.post(TOKEN_URI, data=post_data)
        assert_good_resp(update_resp)
        self._set_tokens(update_resp.json())
        db.session.add(self)
        db.session.commit()



    def _get_header(self):
        '''
        helper functions for getting HTTP Header to make 23andme API call
        '''
        return {'Authorization': 'Bearer '+self.access_token} 

    @api_call
    def get_resources(self, para1, para2,data):
        '''
        get all profiles owned by the user who authorized this client
        '''
        auth_header = self._get_header()
        try:
            resp = requests.get('%s/%s/%s' % (self.api_base, para1,para2 ) )
        except:
            resp = requests.post('%s/%s/%s' % (self.api_base, para1,para2 ), postdata = data, header = auth_header)
        assert_good_resp(resp)
        return resp.json()



    @api_call
    def get_resource(self, para1,data):
        '''
        get all profiles owned by the user who authorized this client
        '''
        auth_header = self._get_header()
        try:
            resp = requests.get('%s/%s' % (self.api_base, para1))
        except:
            resp = requests.post('%s/%s' % (self.api_base, para1), postdata = data, header = auth_header)
        assert_good_resp(resp)
        return resp.json()