import datetime
from flask import Response
from adaptor import get_resource, get_resources
from functools import partial
from fhir.models import Access
from ..util import json_to_xml
import error
import json
from urlparse import urljoin
import requests

BS_JSON_MIMETYPE = 'application/json'
json_response = partial(Response, mimetype=BS_JSON_MIMETYPE)
BS_XML_MIMETYPE = 'application/xml'
xml_response = partial(Response, mimetype=BS_XML_MIMETYPE)
API_BASE = 'https://api.basespace.illumina.com/v1pre3/'
CONTENT_TYPE_HEADER = {'Content-Type': 'application/json; charset=UTF-8'}

def verify_access(request, resource_type, access_type):
    '''
    Verify if a request should be accessing a type of resource
    '''
    if request.session is not None:
        # if a request has a session then it's definitely a user
        # and a user has access to all of his or her resources
        request.authorizer = request.session.user
        return True
    elif request.client is not None:
        # not a user but an OAuth consumer
        # check database and verify if the consumer has access
        request.authorizer = request.client.authorizer
        if datetime.datetime.now() > request.client.expire_at:
            return False
        accesses = Access.query.filter_by(
            client_code=request.client.code,
            access_type=access_type,
            resource_type=resource_type)
        return accesses.count() > 0
    else:
        return False




def bs_handle_read(request, resource_type, resource_id):
    resource = get_resource(resource_type, resource_id)
    if resource is None:
        return error.inform_not_found()
    version = 1
    created = False

    if request.format == 'json':
        response = json_response(status='200')
        response.data = resource
    else:
        response = xml_response(status='200')
        response.data = json_to_xml(json.loads(resource))

    loc_header = 'Location' if created else 'Content-Location'
    response.headers[loc_header] = urljoin(API_BASE, '%s/%s/_history/%s' % (
        resource_type,
        resource_id,
        version))
    return response


def bs_handle_search(request, resource_type):
    '''
    handle FHIR search operation
    '''
    # args = request.args
    # data = {}
    # for i in args:
    #     s = args[i]
    #     data[i] = eval(s.encode())

    search_result = get_resources(resource_type)

    search_result = json.dumps(search_result, separators=(',', ':'))
    if search_result is None:
        return error.inform_not_found()

    response = json_response(status='200')
    response.data = search_result

    version = 1
    created = False
    loc_header = 'Location' if created else 'Content-Location'
    response.headers[loc_header] = urljoin(API_BASE, '%s/_history/%s' % (
        resource_type,
        version))

    return response
