'''
Adaptor for 23andMe API

NOTE: we don't store any 23andMe data except OAuth tokens and
profile ids associated with the user who granted the access
'''
from flask import request, g, current_app, redirect, Blueprint
from functools import wraps
from itertools import chain
from models import GA4GHClient
from error import GA4GHOauthError
import requests

REPOSITORIES = {'google': 'https://www.googleapis.com/genomics/v1beta2'}
OKG = '10473108253681171589'
CONTENT_TYPE_HEADER = {'Content-Type': 'application/json; charset=UTF-8'}
MAIL = 'yhmyhm@mail.ustc.edu.cn'

def require_client(adaptor):
    '''
    decorator for functions that makes 23andme API call
    '''
    @wraps(adaptor)
    def checked(*args, **kwargs):
        ga4gh_client = GA4GHClient.query.get(MAIL)
        if not ga4gh_client:
            raise GA4GHOauthError
        return adaptor(*args, **kwargs)
    return checked

@require_client
def get_resource(resource_type, resource_id):
    '''
    resource_type: callsets, variantsets,
    '''
    ga4gh_client = GA4GHClient.query.get(MAIL)
    get_result = ga4gh_client.get_resource(resource_type, resource_id)
    return get_result


@require_client
def search_sets(resource_type, data):
    ga4gh_client = GA4GHClient.query.get(MAIL)
    search_result = ga4gh_client.search_sets(resource_type, data)
    return search_result
