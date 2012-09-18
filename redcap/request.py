#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2011, Scott Burns
All rights reserved.
"""

import requests
import json


class RCAPIError(Exception):
    """ Errors corresponding to a misuse of the REDCap API """
    pass


class RCRequest(object):
    """Private class wrapping the REDCap API

    see https://redcap.vanderbilt.edu/api/help/

    Decodes response from redcap and returns it.

    Users shouldn't really need to use this, the Project class will use this.
    """

    def __init__(self, url, payload, qtype):
        """Constructor

        Parameters
        ----------
        url: str
            REDCap API URL
        payload: dict
            key,values corresponding to the REDCap API
        qtype: 'imp_record' | 'exp_record' | 'metadata'
            Used to validate payload contents against API
        """
        self.url = url
        self.payload = payload
        self.type = qtype
        if qtype:
            self.validate_pl()
        self.fmt = payload['format']

    def validate_pl(self):
        """Check that at least required params exist

        """
        if self.type == 'exp_record':
            req = set(('token', 'content', 'format', 'type'))
            req_content = 'record'
            err_msg = 'Exporting record but content is not record'
        if self.type == 'imp_record':
            req = set(('token', 'content', 'format', 'type',
                        'overwriteBehavior', 'data'))
            req_content = 'record'
            err_msg = 'Importing record but content is not record'
        if self.type == 'metadata':
            req = set(('token', 'content', 'format'))
            req_content = 'metadata'
            err_msg = 'Requesting metadata but content != metadata'
        if self.type == 'exp_file':
            req = set(('token', 'content', 'action', 'record', 'field'))
            req_content = 'file'
            err_msg = 'Exporting file but content is not file'
        if self.type == 'imp_file':
            req = set(('token', 'content', 'action', 'record', 'field',
                'file'))
            req_content = 'file'
            err_msg = 'Importing file but content is not file'
        if self.type == 'exp_event':
            req = set(('token', 'content', 'format'))
            req_content = 'event'
            err_msg = 'Exporting events but content is not event'
        if self.type == 'exp_arm':
            req = set(('token', 'content', 'format'))
            req_content = 'arm'
            err_msg = 'Exporting arms but content is not arm'
        if self.type == 'exp_fem':
            req = set(('token', 'content', 'format'))
            req_content = 'formEventMapping'
            err_msg = 'Exporting form-event mappings but content is not ' + \
                    'formEventMapping'
        if self.type == 'exp_user':
            req = set(('token', 'content', 'format'))
            req_content = 'user'
            err_msg = 'Exporting users but content is not user'
        pl_keys = set(self.payload.keys())
        # if req is not subset of payload keys, this call is wrong
        if not req <= pl_keys:
            #what is not in pl_keys?
            not_pre = req - pl_keys
            raise RCAPIError("Required keys: %s" % ', '.join(not_pre))
        # Check content, raise with err_msg if not good
        try:
            if self.payload['content'] != req_content:
                raise RCAPIError(err_msg)
        except KeyError:
            raise RCAPIError('content not in payload')

    def execute(self):
        """Execute the API request and return data

        Returns
        -------
        Return data object from JSON decoding process if format=='json',
        else return raw string (ie format=='csv'|'xml')
        """
        header = {'Content-Type': 'application/x-www-form-urlencoded'}
        r = requests.post(self.url, data=self.payload, headers=header)
        if self.payload['format'] == 'json':
            return json.loads(r.content.encode(errors='replace'))
        else:
            return r.content.encode(errors='replace')
