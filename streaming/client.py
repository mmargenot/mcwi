from urllib.parse import urlparse

import requests

# server is http://localhost:5000/generate-samples


class Client:
    """A client object for consuming the contents of our simulated data stream
    and providing them for an separate application to use.
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
            "generate-samples?"
            "tick_size={tick_size}&"
            "number_of_samples={N}".format(
                tick_size=tick_size,
                N=N)
        )

        return response.json()

    def set_distribution(self, dist, params):
        """
        Set the statistical parameters of the distribution you are drawing
        samples by updating the parameters database.

        Parameters
        ----------
        dist : str
            Name of the distribution to use.
        params : dictionary
            Parameters of the given distribution.
        """
        response = self._request_data(
            "set-distribution?"
            "dist={dist}&"
            "params={params}".format(
                dist=dist,
                params=params
            )
        )
        # TODO: Pass params as json body instead of as query param

        return response.json()

    def _request_data(self, resource, json=None):
        url = '/'.join([self.server, resource])

        response = requests.post(url, json=json)
        return response
