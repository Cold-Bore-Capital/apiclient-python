import requests
import time
import hmac
import hashlib
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

    def __init__(self):
        self.api_key = os.getenv('BRIGHT_LOCAL_API_KEY')
        self.api_secret = os.getenv('BRIGHT_LOCAL_API_SECRET')

    def _get_auth_params(self):
        expires = int(time.time()) + self.MAX_EXPIRY
        sig = hmac.new(self.api_secret.encode('latin-1'), (self.api_key + str(expires)).encode('latin-1'), hashlib.sha1).digest()
        sig = sig.decode('latin-1')
        sig = sig.encode('base64').rstrip('\n')
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
        if not response.isSuccess() or ('batch-id' in response.getResult() and not isinstance(response.getResult()['batch-id'], int)):
            raise BatchCreateException('An error occurred and we weren\'t able to create the batch. ', response.getResult()['errors'])
        return int(response.getResult()['batch-id'])

    def get_batch(self, batch_id):
        url = self.BASE_URL + f'/v4/batch/{batch_id}'
        response = self._make_request(url, method='GET')
        return response.getResult()



if __name__ == '__main__':
    api = BrightLocalAPI()
    batch_id = api.create_batch()
    print(batch_id)



























# import requests


# class Api:
#     """API endpoint URL"""
#     ENDPOINT = 'https://tools.brightlocal.com/seo-tools/api'
#     """expiry can't be more than 30 minutes (1800 seconds)"""
#     MAX_EXPIRY = 1800

#     def __init__(self, api_key: str, api_secret: str, endpoint: str = None):
#         self.endpoint = Api.ENDPOINT if endpoint is None else endpoint
#         self.api_key = api_key
#         self.api_secret = api_secret

#     def get(self, resource: str, params: dict = None) -> 'ApiResponse':
#         return self.call(resource, params, 'GET')

#     def post(self, resource: str, params: dict = None) -> 'ApiResponse':
#         return self.call(resource, params)

#     def put(self, resource: str, params: dict = None) -> 'ApiResponse':
#         return self.call(resource, params, 'PUT')

#     def delete(self, resource: str, params: dict = None) -> 'ApiResponse':
#         return self.call(resource, params, 'DELETE')

#     def create_batch(self, stop_on_job_error: bool = False, callback_url: str = None) -> 'Batch':
#         params = {'stop-on-job-error': int(stop_on_job_error)}
#         if callback_url is not None:
#             params['callback'] = callback_url
#         response = self.post('/v4/batch', params)
#         if not response.is_success() or ('batch-id' in response.get_result() and not isinstance(response.get_result()['batch-id'], int)):
#             raise BatchCreateException('An error occurred and we weren\'t able to create the batch. ', None, None, response.get_result()['errors'])
#         return Batch(self, int(response.get_result()['batch-id']))

#     def get_batch(self, batch_id: int) -> 'Batch':
#         return Batch(self, batch_id)

#     def call(self, resource: str, params: dict = None, http_method: str = 'POST') -> 'ApiResponse':
#         resource = resource.replace('/seo-tools/api', '')
#         # some methods only require api key but there's no harm in also sending
#         # sig and expires to those methods
#         params = {**self.get_auth_params(), **(params or {})}
#         try:
#             result = requests.request(http_method, self.endpoint + '/' + resource.lstrip('/'), **self.get_options(http_method, params))
#         except requests.RequestException as e:
#             result = e.response
#         return ApiResponse(result.status_code, result.json())

#     def get_auth_params(self) -> dict:
#         expires = int(datetime.datetime.utcnow().timestamp()) + Api.MAX_EXPIRY
#         sig = base64.encodebytes(hmac.new(self.api_secret.encode(), (self.api_key + str(expires)).encode(), hashlib.sha1).digest()).decode()
#         return {
#             'api-key': self.api_key,
#             'sig': sig,
#             'expires': expires