import requests
import time
import hmac
import hashlib
import base64
import json
import os 
from dotenv import find_dotenv, load_dotenv
from typing import Optional

load_dotenv(find_dotenv())

class BrightLocalException(Exception):
    pass

class BatchCreateException(BrightLocalException):
    def __init__(self, message, errors):
        super().__init__(message)
        self.errors = errors


class ApiResponse:
    def __init__(self, status_code, response):
        self.status_code = status_code
        self.response = response

    def isSuccess(self):
        return self.status_code == 200

    def getResult(self):
        return self.response


class BrightLocalAPI:
    BASE_URL = 'https://tools.brightlocal.com/seo-tools/api'
    MAX_EXPIRY = 1800

    def __init__(self, api_key: str, api_secret: str) -> None:
        self.api_key = api_key
        self.api_secret = api_secret

    def _get_auth_params(self):
        expires = int(time.time()) + self.MAX_EXPIRY
        sig = hmac.new(self.api_secret.encode('latin-1'), (self.api_key + str(expires)).encode('latin-1'), hashlib.sha1).digest()
        sig = base64.b64encode(sig).decode('latin-1').rstrip('\n')
        return {
            'api-key': self.api_key,
            'sig': sig,
            'expires': expires
        }

    def _make_request(self, url, params=None, method='POST'):
        auth_params = self._get_auth_params()
        request_params = {**auth_params, **(params or {})}
        if request_params.get('batch-id'):
            request_params['batch-id'] = str(request_params['batch-id'])
        response = requests.request(method, url, params=request_params)
        api_response = ApiResponse(response.status_code, json.loads(response.text))
        return api_response

    def create_batch(self, stop_on_job_error=False, callback_url=None):
        url = self.BASE_URL + '/v4/batch'
        params = {'stop-on-job-error': int(stop_on_job_error)}
        if callback_url:
            params['callback'] = callback_url
        response = self._make_request(url, params)
        r = response.getResult()
        if not r['success'] or ('batch-id' in r.keys() and not isinstance(r['batch-id'], int)):
            raise BatchCreateException('An error occurred and we weren\'t able to create the batch. ', response.getResult()['errors'])
        return (r['batch-id'])

    def get_batch(self, batch_id):
        url = self.BASE_URL + f'/v4/batch/{batch_id}'
        response = self._make_request(url, method='GET')
        return response.getResult()
    def get_id(self) -> Optional[int]:
        return self.batch_id

    def commit(self) -> bool:
        response = self._make_request('/v4/batch', {'batch-id': self.batch_id}, 'PUT')
        if not response.isSuccess():
            raise Exception('An error occurred and we aren\'t able to commit the batch.')
        return True

    def add_job(self, resource: str, params: dict) -> ApiResponse:
        params['batch-id'] = self.batch_id
        response = self._make_request(url=resource, params=params)
        if not response.isSuccess():
            raise Exception('An error occurred and we weren\'t able to add the job to the batch.')
        return response

    def delete(self) -> bool:
        response = self._make_request('/v4/batch', {'batch-id': self.batch_id}, 'DELETE')
        if not response.isSuccess():
            raise Exception('An error occurred and we weren\'t able to delete the batch.')
        return True

    def stop(self) -> bool:
        response = self._make_request('/v4/batch/stop', {'batch-id': self.batch_id}, 'PUT')
        if not response.isSuccess():
            raise Exception('An error occurred and we weren\'t able to stop the batch.')
        return True

    def get_results(self) -> ApiResponse:
        response = self._make_request('/v4/batch', {'batch-id': self.batch_id})
        if not response.isSuccess():
            raise Exception('An error occurred and we weren\'t able to find the batch.')
        return response




