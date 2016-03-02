class GA4GHOauthError(Exception):
    '''
    Exception used to capture error resulting from
    attempt to get GA4GH resources.

    '''
    pass

inform_not_found = lambda: new_error('404')
inform_gone = lambda: new_error('410')
inform_not_allowed = lambda: new_error('405')
inform_bad_request = lambda: new_error('400')
inform_no_content = lambda: new_error('204')
inform_forbidden = lambda: new_error('403')
