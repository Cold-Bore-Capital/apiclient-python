class ApiResponse:
    def __init__(self, statusCode: int, result: dict):
        self.statusCode = statusCode
        self.result = result

    def getResult(self) -> dict:
        return self.result

    def getStatusCode(self) -> int:
        return self.statusCode

    def isSuccess(self) -> bool:
        if 'success' in self.result:
            return self.result['success']
        return self.statusCode in [200, 201]