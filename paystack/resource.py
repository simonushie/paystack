# -*- coding: utf-8 -*-
"""
Paystack API wrapper.

@author Bernard Ojengwa.

Copyright (c) 2015, Bernard Ojengwa
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors
   may be used to endorse or promote products derived from this software
   without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OƒR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
from paystack.client import RequestsClient
from paystack import error
from paystack import util
from paystack import version


class BaseAPIResource(object):

    def __init__(self, api_secret=None, resource_path=None, verify_ssl=True):
        self.protocol = 'https'
        self.api_host = self.protocol + '://api.paystack.co/'

        if not api_secret:
            raise error.ValidationError('You must provide your API SECRET_KEY \
                                        during object initialisation')

        if not resource_path:
            raise error.ValidationError('You must provide the API endpoint for\
                                         for the resource you want to access.')
        self.api_secret = util.utf8(api_secret)
        self.resource_path = resource_path
        self.client = RequestsClient(verify_ssl_certs=verify_ssl)
        self.request_headers = {
            "Authorization": "Bearer {0}".format(self.api_secret),
            "Content-Type": "application/json",
            "user-agent": "PaystackSDK - {0}".format(version.VERSION)
        }

        self._result = {}
        self._status_code = None
        self._response_headers = {}

    def all(self):
        pass

    def one(self, id):
        pass

    def post(self, data):
        pass

    def delete(self, id):
        pass

    def update(self, id, data):
        pass

    @property
    def status(self):
        return self._status_code

    @property
    def response(self):
        return self._result

    @property
    def headers(self):
        self._response_headers


class CustomerResource(BaseAPIResource):
    pass


class TransactionResource(BaseAPIResource):

    def __init__(self, api_secret, reference=None,
                 resource_path='transaction', *args, **kwargs):
        super(TransactionResource, self)\
            .__init__(api_secret, resource_path, *args, **kwargs)
        self.reference = reference
        self.authorization_url = None
        self.access_code = None
        self.email = None
        self.amount = None
        self.authorization_code = None

    def initialize(self, amount, email, ref=None, plan=None):
        endpoint = '/initialize'
        method = 'POST'
        if not ref and not self.reference:
            raise error.ValidationError("A unique object reference was not \
                                        provided during instantiation. You\
                                         must provide a reference for this\
                                         transaction.")
        self.reference = (lambda ref: ref if ref else self.reference)(ref)
        payload = {
            "reference": self.reference,
            "amount": amount,
            "email": email,
            "plan": plan
        }
        url = self.api_host + self.resource_path + endpoint
        response, status, headers = self.client.request(method, url,
                                                        self.request_headers,
                                                        post_data=payload)
        self._response_headers = headers
        self._status_code = status
        self._result = response
        print(response)
        if not response.get('status', False):
            raise error.APIError(response.get('message'))

        self.authorization_url = response.get('authorization_url', None)
        self.access_code = response.get('access_code', None)
        self.email = email
        self.amount = amount
        self.authorization_code = response\
            .get('authorization_code')
        print(self.authorization_code)

        return response

    def verify(self, ref=None):
        method = 'GET'

        if not ref and not self.reference:
            raise error.ValidationError("A unique object reference was not \
                                        provided during instantiation. You\
                                         must provide a reference for this\
                                         transaction.")

        self.reference = (lambda ref: ref if ref else self.reference)(ref)

        endpoint = '/verify/' + self.reference
        url = self.api_host + self.resource_path + endpoint

        response, status, headers = self.client.request(method, url,
                                                        self.request_headers
                                                        )
        self._response_headers = headers
        self._status_code = status
        self._result = response
        if not response.get('status', False):
            raise error.APIError(response.get('message'))

        self.authorization_url = response.get('authorization_url', None)
        self.access_code = response.get('access_code', None)

        return response

    def charge(self, authorization_code=None, amount=None,
               email=None, reference=None):

        endpoint = '/charge_authorization'
        method = 'POST'

        if not authorization_code and not self.authorization_code:
            raise error.ValidationError("This transaction object does not\
                                         have an authorization code.You must\
                                          provide an authorization code for\
                                           this transaction.")
        if not amount and not self.amount:
            raise error.ValidationError("There is no amount specified for this \
                                        transaction. You must provide the \
                                        transaction amount in Kobo.")
        if not email and not self.email:
            raise error.ValidationError("The customer's email address wss not \
                                        specified.")

        authorization_code = (
            lambda ref: authorization_code if authorization_code else self
            .authorization_code)(authorization_code)

        email = (
            lambda ref: email if email else self.email)(email)

        amount = (
            lambda ref: amount if amount else self.amount)(amount)

        payload = {
            "reference": reference,
            "amount": amount,
            "email": email,
            "authorization_code": authorization_code
        }

        url = self.api_host + self.resource_path + endpoint
        response, status, headers = self.client.request(method, url,
                                                        self.request_headers,
                                                        post_data=payload
                                                        )
        self._response_headers = headers
        self._status_code = status
        self._result = response
        if not response.get('status', False):
            raise error.APIError(response.get('message'))

        # self.authorization_url = response.get('authorization_url', None)
        # self.access_code = response.get('access_code', None)

        return response


class PlanResource(BaseAPIResource):
    pass
