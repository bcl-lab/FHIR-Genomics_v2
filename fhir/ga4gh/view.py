from flask import Blueprint, current_app, redirect, request, Response, g
from urllib import urlencode
from models import GA4GHClient, GA4GHOauthError
from ..ui import require_login, get_session
from ..database import db

ga4gh = Blueprint('ga4gh', __name__)

ga4gh.before_request(get_session)

NOT_ALLOWED = Response(status='405')

MAIL = 'yhmyhm@mail.ustc.edu.cn'

@ga4gh.route('/')
def acquire_client():
    '''
    Get the client from database
    '''
    try:
        ga4gh_client = GA4GHClient.query.get(MAIL)
    except:
        ga4gh_client = None

    if not ga4gh_client:
        return redirect('/ga4gh/import')
    return



@ga4gh.route('/import')
@require_login
def import_from_ga4gh():
    '''
    redirect user to 23andme and prompt authorization to access his or her data
    '''
    ga4gh_client = GA4GHClient.query.get(request.session.user.email)
    if ga4gh_client is not None:
        return NOT_ALLOWED
    ga4gh_config = current_app.config['GA4GH_CONFIG']
    redirect_params = urlencode({
        'redirect_uri': ga4gh_config['redirect_uri'],
        'response_type': 'code',
        'client_id': ga4gh_config['client_id'],
        'scope': ga4gh_config['scope']})
    return redirect('%s?%s'% (ga4gh_config['auth_uri'], redirect_params))


@ga4gh.route('/recv_redirect')
@require_login
def recv_ga4gh_auth_code():
    '''
    handle redirect from 23andme's OAuth dance and initiate our 23andme client
    '''
    code = request.args.get('code')
    if code is None:
        return GA4GHOauthError
    ga4gh_config = current_app.config['GA4GH_CONFIG']
    ga4gh_client = GA4GHClient(code, MAIL, ga4gh_config)
    #g.ga4gh_client = ga4gh_client
    db.session.add(ga4gh_client)
    db.session.commit()
    return ga4gh_client

@ga4gh.route('/clear')
@require_login
def clear_ga4gh_data():
    '''
    removed the 23andme client associated with user in session
    '''
    ga4gh_client = GA4GHClient.query.get(request.session.user.email)
    if ga4gh_client is None:
        return NOT_ALLOWED
    db.session.delete(ga4gh_client)
    db.session.commit()
    return redirect('/') 
