import time
from urllib.parse import urlparse

import requests

# server is http://localhost:5000/generate-samples

ITER_BYTES_SIZE = 9

class Client:
    """
    This might be useful?
    https://stackoverflow.com/questions/59162868/python-requests-stream-iter-content-chunks-into-a-pandas-read-csv-function
    might be smarter than trying to build our own iterator.
    """

    def __init__(self, url):
        self.server = url

        self._validate_server_address(self.server)

    def _validate_server_address(self, server_address):
        result = urlparse(server_address)

        if result.scheme and result.netloc:
            return True

        raise ValueError("Server URL is not valid")

    def generate_samples(self, N, tick_size='s'):
        response = self._request_data(
            "generate-samples?tick_size={tick_size}&number_of_samples={N}".format(
                tick_size=tick_size,
                N=N,
            ),
        )

        return response.json()

    def _request_data(self, resource):
        url = '/'.join([self.server, resource])

        response = requests.post(url)
        return response
