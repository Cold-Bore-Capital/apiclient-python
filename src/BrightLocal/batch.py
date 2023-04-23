from typing import Optional
from brightlocal_api import ApiResponse


class Batch:

    def __init__(self, api, batch_id: Optional[int] = None):
        self.api = api
        self.batch_id = batch_id

    def get_id(self) -> Optional[int]:
        return self.batch_id

    def commit(self) -> bool:
        response = self.api._make_request('/v4/batch', {'batch-id': self.batch_id}, 'PUT')
        if not response.isSuccess():
            raise Exception('An error occurred and we aren\'t able to commit the batch.')
        return True

    def add_job(self, resource: str, params: dict) -> ApiResponse:
        params['batch-id'] = self.batch_id
        response = self.api._make_request(resource, params)
        if not response.isSuccess():
            raise Exception('An error occurred and we weren\'t able to add the job to the batch.')
        return response

    def delete(self) -> bool:
        response = self.api._make_request('/v4/batch', {'batch-id': self.batch_id}, 'DELETE')
        if not response.isSuccess():
            raise Exception('An error occurred and we weren\'t able to delete the batch.')
        return True

    def stop(self) -> bool:
        response = self.api._make_request('/v4/batch/stop', {'batch-id': self.batch_id}, 'PUT')
        if not response.isSuccess():
            raise Exception('An error occurred and we weren\'t able to stop the batch.')
        return True

    def get_results(self) -> ApiResponse:
        response = self.api._make_request('/v4/batch', {'batch-id': self.batch_id})
        if not response.isSuccess():
            raise Exception('An error occurred and we weren\'t able to find the batch.')
        return response
