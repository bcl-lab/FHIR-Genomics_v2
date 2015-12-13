from flask import Blueprint, current_app, redirect, request, Response
from urllib import urlencode
from models import BaseSpaceClient, BaseSpaceOAuthError
from ..ui import require_login, get_session
from ..database import db

basespace = Blueprint('basespace', __name__)

basespace.before_request(get_session)

NOT_ALLOWED = Response(status='405')

@basespace.route('/')
def acquire_client():
    '''
    Get the client from database
    '''
    try:
        bs_client = BaseSpaceClient.query.get(request.session.user.email)
    except:
        bs_client = None

    if not bs_client:
        return redirect('/basespace/import')
    return

@basespace.route('/import')
@require_login
def import_from_bs():
    '''
    redirect user to basespace and prompt authorization to access his or her data
    '''
    bs_client = BaseSpaceClient.query.get(request.session.user.email)
    if bs_client is not None:
        return NOT_ALLOWED
    bs_config = current_app.config['BS_CONFIG']
    redirect_params = urlencode({
        'client_id': bs_config["client_id"],
        'redirect_uri': bs_config["redirect_uri"],
        'response_type': 'code',
        'scope': bs_config["scope"]
    })
    return redirect('%s?%s'% (bs_config['auth_uri'], redirect_params))


@basespace.route('/recv_redirect')
@require_login
def recv_bs_auth_code():
    '''
    handle redirect from BaseSpace's OAuth dance and initiate our BaseSpace client
    '''
    code = request.args.get('code')
    if code is None:
        return BaseSpaceOAuthError
    bs_config = current_app.config['BS_CONFIG']
    bs_client = BaseSpaceClient(code, request.session.user.email, bs_config)
    db.session.add(bs_client)
    db.session.commit()
    return bs_client


@basespace.route('/clear')
@require_login
def clear_bs_data():
    '''
    removed the BaseSpace client associated with user in session
    '''
    bs_client = BaseSpaceClient.query.get(request.session.user.email)
    if bs_client is None:
        return NOT_ALLOWED
    db.session.delete(bs_client)
    db.session.commit()
    return redirect('/') 
