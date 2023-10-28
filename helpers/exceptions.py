class ApiException(Exception):
    def __init__(self, message: str | None = None, status_code: int = 400):
        super(ApiException, self).__init__(message)
        self._message = message
        self._status_code = status_code

    @property
    def error_message(self):
        return "An error occurred" if self._message is None else self._message

    @property
    def status_code(self):
        return 500 if self._status_code is None else self._status_code


class OperationalException(Exception):
    def __init__(self, message: str | None = None):
        super(OperationalException, self).__init__(message)


class NoDataProvidedApiException(ApiException):
    def __init__(self):
        super(NoDataProvidedApiException, self).__init__(
            message="No data provided", status_code=400
        )


class ClientException(Exception):
    def __init__(self, message: str | None = None):
        super(ClientException, self).__init__(message)
