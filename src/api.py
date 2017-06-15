import urllib3
import json


class LevelMoneyApiClient(object):
    API_PREFIX = 'https://2016.api.levelmoney.com/api/v2/core/'

    def __init__(self, **kwargs):
        self.interview_token = kwargs['interview_token']
        self.uid = kwargs['uid']
        self.api_token = kwargs['api_token']

    @staticmethod
    def _construct_headers():
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        return headers

    def _construct_payload(self, optional_args):
        payload = dict()
        payload['args'] = {
            'uid': self.uid,
            'token': self.interview_token,
            'api-token': self.api_token,
            'json-strict-mode': False,
            'json-verbose-response': False
        }

        # push optional arguments
        for optional_arg_key, optional_arg_value  in optional_args.iteritems():
            payload[optional_arg_key] = optional_arg_value

        return json.dumps(payload)

    @staticmethod
    def validate_response(response):
        response_error = response.get('error')
        if response_error == 'no-error':
            return

        raise Exception(response_error)

    def make_request(self, method_name, method_args=None):
        if method_name is None:
            error_message = 'method_name is required'
            raise Exception(error_message)

        # TODO:
        # - implement retryable w/ backoff
        api_method_url = self.API_PREFIX + method_name
        api_headers = self._construct_headers()
        api_payload = self._construct_payload(method_args or dict())

        http = urllib3.PoolManager()
        response = http.request('POST',
                                api_method_url,
                                headers=api_headers,
                                body=api_payload)

        if response.status != 200:
            raise RuntimeError()

        serialized_response = json.loads(response.data.decode('utf-8'))

        self.validate_response(serialized_response)
        return serialized_response

    def get_all_transactions(self):
        all_transactions = self.make_request(method_name='get-all-transactions')
        return all_transactions['transactions']

    def get_projected_transactions(self, year, month):
        method_arguments = dict()
        method_arguments['year'] = year
        method_arguments['month'] = month

        projected_transactions = self.make_request(method_name='projected-transactions-for-month', method_args=method_arguments)
        return projected_transactions['transactions']
