from flask import jsonify, request
from streaming import create_app

from mcwi.distributions import BrownianMotion

class DbConnector:

    def __init__(db_type='sqlite'):
        self.db_type = db_type

    def get_db_connection(self):
        """Add a connection to the database to the request global variable set.

        Returns
        -------
        Connection
            Connection to the sqlite3 database for the app.
        """
        if self.db_type == 'sqlite':
            db = _connect_to_sqlite_db()

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

class McwiApp:
    SUPPORTED_TICK_SIZES = ('s', 'm', 'h', 'd')

    MAX_TICKS_PER_TICK_SIZE = {
        's': 60,
        'm': 60,
        'h': 24,
        'd': 365,
    }

    DISTRIBUTIONS = {
        'brownian': BrownianMotion
    }

    def __init__(debug=True):
        self.debug = debug
        self.app = create_app()

        self.db_connector = DbConnector()

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

    def run(self):
        self.app.run(self.debug)
        self.db = self.db_connector.get_db_connection()

    def add_endpoint(self, endpoint, endpoint_name, handler, methods):
        self.app.add_url_rule(endpoint, endpoint_name, handler, methods=methods)

    def add_custom_distribution_type(self, name, cls):
        # XXX: Another way to do this is add another endpoint
        # that allows someone to send a name and code
        # that subclasses the MCWI Distribution class
        # and then the server executes that code
        self.DISTIRIBUTIONS[name] = cls

    def _set_distribution_handler(self):
        # do the handling of the request here
        """
        Takes:
        - frequency
        - n: number of samples
        """
        tick_size = request.args.get('tick_size')
        number_of_samples = int(request.args.get('number_of_samples'))

        assert tick_size in SUPPORTED_TICK_SIZES
        tick_mod = MAX_TICKS_PER_TICK_SIZE[tick_size]

        c = self.db.cursor()
        # TODO: Move this select to the db connector
        db_result = c.execute("SELECT * FROM parameters").fetchall()

        if not db_result:
            return jsonify(
                message="Distribution must be set before sampling",
                status_code=400
            )

        dist_type = db_result[0][0]
        assert dist_type in SUPPORTED_DISTRIBUTIONS
        
        params = pickle.loads(db_result[0][1])
        dist = SUPPORTED_DISTRIBUTIONS[dist_type](
            **params
        )

        data = {
            'samples': [],
            'tick_size': tick_size,
        }
        
        for tick in range(1, number_of_samples + 1):
            sample = dist.sample()
            
            tick = tick % tick_mod
            
            data['samples'].append([tick, sample])

            # TODO: Modify parameter table to include most recent start values
            #       (use the params dictionary combined with established table)

        return jsonify(data)

    def _generate_samples_handler(self):
        # do the handling of the request here
        pass
    
    def _load_dist_parameters(self):
        c = self.db.cursor()
        dist_params = c.execute(
            'SELECT params FROM parameters'
        )
        dist_params = dist_params[0]
        dist_params = dist_params.split(',')
        dist_params = [float(p) for p in dist_params]
        return dist_params
