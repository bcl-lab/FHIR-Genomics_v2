'''
Adaptor for 23andMe API

NOTE: we don't store any 23andMe data except OAuth tokens and
profile ids associated with the user who granted the access
'''
from flask import request, g
from functools import wraps
from itertools import chain
from models import BaseSpaceClient
from error import BaseSpaceOAuthError
from ..models import Resource
from ..query_builder import COORD_RE, InvalidQuery
from util import slice_, get_snps, get_coord

# we use this to distinguish any 23andMe resource from internal resources
# PREFIX = 'bs_'
# PREFIX_LEN = len(PREFIX)


def acquire_client():
    '''
    Get the client from database
    '''
    bs_client = BaseSpaceClient.query.get(request.authorizer.email)
    return bs_client


def require_client(adaptor):
    '''
    decorator for functions that makes 23andme API call
    '''
    @wraps(adaptor)
    def checked(*args, **kwargs):
        bs_client = acquire_client()
        if bs_client is None:
            raise BaseSpaceOAuthError
        return adaptor(*args, **kwargs)
    return checked


@require_client
def get_resources(resource_type, resource_id, data=None):

    bs_client = BaseSpaceClient.query.get(request.authorizer.email)
    get_result = bs_client.get_resource(resource_type, resource_id,data)
    return get_result


@require_client
def get_resource(resource_type, data):

    bs_client = BaseSpaceClient.query.get(request.authorizer.email)
    get_result = bs_client.get_resources(resource_type, data)
    return get_result

