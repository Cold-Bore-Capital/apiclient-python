import requests
import time
import hmac
import hashlib
import base64
import json
import os 
from dotenv import find_dotenv, load_dotenv

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
        return int(r['batch-id'])

    def get_batch(self, batch_id):
        url = self.BASE_URL + f'/v4/batch/{batch_id}'
        response = self._make_request(url, method='GET')
        return response.getResult()

class BrightLocalBatch:
    BASE_URL = 'https://tools.brightlocal.com/seo-tools/api'
    API_VERSION = 'v4'
    HEADERS = {'Content-Type': 'application/json'}

    def __init__(self, api_key, api_secret, batch_id):
        self.api_key = api_key
        self.api_secret = api_secret
        self.batch_id = None

    def create_batch(self):
        url = f"{self.BASE_URL}/{self.API_VERSION}/batch/create"
        data = {'api-key': self.api_key, 'api-secret': self.api_secret}
        response = requests.post(url, headers=self.HEADERS, data=json.dumps(data))
        response.raise_for_status()
        self.batch_id = response.json()['batch-id']
        return self.batch_id

    def add_job(self, endpoint, params):
        url = f"{self.BASE_URL}/{self.API_VERSION}{endpoint}"
        params.update({'batch-id': self.batch_id, 'api-key': self.api_key, 'api-secret': self.api_secret})
        response = requests.post(url, headers=self.HEADERS, data=json.dumps(params))
        response.raise_for_status()
        return response

    def commit(self):
        url = f"{self.BASE_URL}/{self.API_VERSION}/batch/commit"
        data = {'batch-id': self.batch_id, 'api-key': self.api_key, 'api-secret': self.api_secret}
        response = requests.post(url, headers=self.HEADERS, data=json.dumps(data))
        response.raise_for_status()
        return response

    def get_results(self):
        url = f"{self.BASE_URL}/{self.API_VERSION}/batch/get-results"
        params = {'batch-id': self.batch_id, 'api-key': self.api_key, 'api-secret': self.api_secret}
        response = requests.get(url, headers=self.HEADERS, params=params)
        response.raise_for_status()
        return response

if __name__ == '__main__':
    api = BrightLocalAPI('api_key', 'api_secret')
    batch_id = api.create_batch()
    print(batch_id)



