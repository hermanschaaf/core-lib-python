from core_lib.configurations.endpoint_configuration import EndpointConfiguration
from core_lib.logger.endpoint_logger import EndpointLogger
from core_lib.response_handler import ResponseHandler


class ApiCall:

    @property
    def new_builder(self):
        return ApiCall(self.global_configuration, logger=self.endpoint_logger)

    def __init__(
            self,
            global_configuration,
            endpoint_logger=EndpointLogger()
    ):
        self.global_configuration = global_configuration
        self.request_builder = None
        self.response_handler = ResponseHandler()
        self.endpoint_configuration = EndpointConfiguration()
        self.endpoint_logger = endpoint_logger
        self._endpoint_name_for_logging = None

    def request(self, request_builder):
        self.request_builder = request_builder
        return self

    def response(self, response_handler):
        self.response_handler = response_handler
        return self

    def configuration(self, endpoint_configuration):
        self.endpoint_configuration = endpoint_configuration
        return self

    def endpoint_name_for_logging(self, endpoint_name_for_logging):
        self._endpoint_name_for_logging = endpoint_name_for_logging
        return self

    def execute(self):
        try:
            _http_request = self.request_builder \
                .endpoint_logger(self.endpoint_logger) \
                .endpoint_name_for_logging(self._endpoint_name_for_logging) \
                .build(self.global_configuration)
            _http_client_configuration = self.global_configuration.get_http_client_configuration()
            _http_callback = _http_client_configuration.http_callback

            self.update_http_callback_with_request(_http_callback, _http_client_configuration, _http_request)

            self.endpoint_logger.debug("Raw request for {} is: {}".format(
                self.endpoint_configuration.name, vars(_http_request)))

            _http_response = _http_client_configuration.http_client.execute(
                _http_request, self.endpoint_configuration)

            self.endpoint_logger.debug("Raw response for {} is: {}".format(
                self.endpoint_configuration.name, vars(_http_response)))

            self.update_http_callback_with_response(_http_callback, _http_client_configuration, _http_response)

            return self.response_handler.endpoint_logger(self.endpoint_logger) \
                .endpoint_name_for_logging(self._endpoint_name_for_logging) \
                .handle(_http_response, self.global_configuration.get_global_errors())
        except Exception as e:
            self.logger.error(e)
            raise

    def update_http_callback_with_request(self, _http_callback, _http_client_configuration, _http_request):
        if _http_callback:
            self.endpoint_logger.info("Calling the on_before_request method of http_call_back for {}."
                                      .format(self.endpoint_configuration.name))
            _http_client_configuration.http_callback.on_before_request(_http_request)

    def update_http_callback_with_response(self, _http_callback, _http_client_configuration, _http_response):
        if _http_callback:
            self.endpoint_logger.info("Calling on_after_response method of http_call_back for {}.".format(
                self.endpoint_configuration.name))
            _http_client_configuration.http_callback.on_after_response(_http_response)
