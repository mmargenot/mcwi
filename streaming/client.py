import time
import sqlite3
from urllib.parse import urlparse

import requests

# server is http://localhost:5000/generate-samples


class Client:
    """A client object for consuming the contents of our simulated data stream
    and providing them for an separate application to use.
    """

    def __init__(self, url, dist_parameters):
        self.server = url
        self.db = 'mcwi.db'
        self.dist_parameters = dist_parameters

        db = sqlite3.connect(self.db)
        c = db.cursor()
        c.execute(
            "INSERT INTO parameters VALUES (?)",
            (dist_parameters['dist'], dist_parameters['params'])
        )
        db.commit()
        db.close()

        self._validate_server_address(self.server)

    def _validate_server_address(self, server_address):
        result = urlparse(server_address)

        if result.scheme and result.netloc:
            return True

        raise ValueError("Server URL is not valid")

    def generate_samples(self, N, tick_size='s'):
        response = self._request_data(
            "generate-samples?"
            "dist={dist}&"
            "tick_size={tick_size}&"
            "number_of_samples={N}".format(
                dist=self.dist_parameters['dist'],
                tick_size=tick_size,
                N=N)
        )

        return response.json()

    def set_distribution(self, dist_parameters):
        """
        Set the statistical parameters of the distribution you are drawing
        samples by updating the parameters database.

        Parameters
        ----------
        dist_parameters : dictionary
            A mapping of
                distribution -> string
                params -> string
            To make the `params` string, we need to turn the tuple of
            parameters into a string and parse it later when we need it.
        """
        # TODO: update parameters table in database.
        self.dist_parameters = dist_parameters

    def _request_data(self, resource):
        url = '/'.join([self.server, resource])

        response = requests.post(url)
        return response
