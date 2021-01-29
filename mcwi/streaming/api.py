import time
from typing import NamedTuple
from flask import jsonify, request
import sqlite3
import json
import pickle

import toolz.functoolz as tools

from .server import create_app

from mcwi.distributions import BrownianMotion


class DistributionParameters(NamedTuple):
    type: str
    params: dict


class DbConnector:

    def __init__(self, db_type='sqlite'):
        self.db_type = db_type

    def get_db_connection(self):
        """Add a connection to the database to the request global variable set.

        Returns
        -------
        Connection
            Connection to the sqlite3 database for the app.
        """
        if self.db_type == 'sqlite':
            db = self._connect_to_sqlite_db()

        self.cursor = db.cursor()

        return db

    def _connect_to_sqlite_db(self):
        """Connect to MCWI database.

        Returns
        -------
        conn : Connection
        Connection to the sqlite3 database for the app.
        """
        conn = sqlite3.connect('mcwi.db')

        return conn

    def _load_dist_parameters(self):
        dist_params = self.cursor.execute(
            'SELECT params FROM parameters'
        )
        dist_params = dist_params[0]
        dist_params = dist_params.split(',')
        dist_params = [float(p) for p in dist_params]
        return dist_params

    def get_distribution_parameters(self):
        if not hasattr(self, 'cursor'):
            raise ValueError("Need to establish a database connection first")

        db_result = self.cursor.execute("SELECT * FROM parameters").fetchall()

        dist_params = DistributionParameters(
            type=db_result[0][0],
            params=db_result[0][1],
        )
        return dist_params

    def insert_distribution_parameters(self, distribution, params):
        results = self.cursor.execute(
            "INSERT INTO parameters VALUES (?, ?)",
            (distribution, params)
        )
        return results

    def update_distribution_parameters(
            self,
            old_distribution,
            old_params,
            new_distribution,
            new_params
    ):
        results = self.cursor.execute(
            "UPDATE parameters "
            "SET distribution = ?, params = ? "
            "WHERE distribution = ? AND params = ?",
            (new_distribution, new_params, old_distribution, old_params)
        )
        return results


class McwiApp:
    SUPPORTED_TICK_SIZES = ('ms', 's', 'm', 'h', 'd')

    MAX_TICKS_PER_TICK_SIZE = {
        'ms': 0.001,
        's': 1,
        'm': 60,
        'h': 24,
        'd': 365,
    }

    DISTRIBUTIONS = {
        'brownian': BrownianMotion
    }

    CURRENT_TIME = 0
    PREVIOUS_TIME = None
    # TODO: Determine appropriate time dilations factors for real world
    #       timestamp vs. simulated time series ticks. What is a reasonable
    #       value?
    TIME_DILATION_FACTOR = 1

    def __init__(self, debug=True):
        self.debug = debug
        self.app = create_app()

        self._db_connector = DbConnector()

        self.add_endpoint(
            endpoint='/set-distribution',
            endpoint_name='set-distribution',
            handler=self._set_distribution_handler,
            methods=['POST'],
        )

        self.add_endpoint(
            endpoint='/generate-samples',
            endpoint_name='generate-samples',
            handler=self._generate_samples_handler,
            methods=['POST'],
        )

    def run(self, host='0.0.0.0', port=5000):
        self.app.run(debug=self.debug, host=host, port=port)
        self.db = self.db_connector.get_db_connection()

    def add_endpoint(self, endpoint, endpoint_name, handler, methods):
        self.app.add_url_rule(
            endpoint,
            endpoint_name,
            handler,
            methods=methods
        )

    def add_custom_distribution_type(self, name, cls):
        # XXX: Another way to do this is add another endpoint
        # that allows someone to send a name and code
        # that subclasses the MCWI Distribution class
        # and then the server executes that code
        self.DISTIRIBUTIONS[name] = cls

    def _set_distribution_handler(self):
        import pdb; pdb.set_trace();
        payload = request.get_json()
        params = json.loads(payload)

        dist = params.pop('distribution')

        # https://toolz.readthedocs.io/en/latest/api.html#toolz.functoolz.pipe
        params = tools.pipe(params, pickle.dumps, sqlite3.Binary)

        dp = self.db.get_distribution_parameters()
        try:
            if not dp:
                self.db.insert_distribution_parameters(
                    distribution=dist,
                    params=params,
                )
            else:
                self.db.update_distribution_parameters(
                    old_distribution=dp.type,
                    old_params=dp.params,
                    new_distribution=dist,
                    new_params=params,
                )
        except sqlite3.Error as e:
            print('Error Occurred: ', str(e))

        self.db.commit()
        self.db.close()

        return jsonify(
            message='Distribution set to {dist}'.format(dist=dist),
            status_code=200,
        )

    def _generate_samples_handler(self):
        # do the handling of the request here
        """
        Takes:
        - frequency
        - n: number of samples
        """
        tick_size = request.args.get('tick_size')
        number_of_samples = int(request.args.get('number_of_samples'))

        assert tick_size in self.SUPPORTED_TICK_SIZES
        ticks = self.MAX_TICKS_PER_TICK_SIZE[tick_size]

        dp = self.db.get_distribution_parameters()

        if not dp:
            return jsonify(
                message="Distribution must be set before sampling",
                status_code=400
            )

        assert dp.type in self.SUPPORTED_DISTRIBUTIONS

        params = pickle.loads(dp.params)

        self.PREVIOUS_TIME = self.CURRENT_TIME
        self.CURRENT_TIME = time.time()

        time_delta = self.CURRENT_TIME - self.PREVIOUS_TIME

        dist = self.SUPPORTED_DISTRIBUTIONS[dp.type](
            **params
        )

        jump_sample = dist.handle_jump(
            time_delta * ticks
        )

        data = {
            'samples': [jump_sample],
            'tick_size': tick_size,
        }

        for tick in range(1, number_of_samples):
            sample = dist.sample()

            tick = tick % ticks

            data['samples'].append([tick, sample])

            # TODO: Modify parameter table to include most recent start values
            #       (use the params dictionary combined with established table)

        return jsonify(data)
