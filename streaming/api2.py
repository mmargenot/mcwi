from flask import g

from streaming import create_app

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

class FlaskApp:

    def __init__(debug=True):
        self.debug = debug
        self.app = create_app()

        self.db_connector = DbConnector()

        self.add_endpoint(
            endpoint='/set-distribution',
            endpoint_name='set-distribution',
            handler=self._set_distribution_handler,
        )

        self.add_endpoint(
            endpoint='/generate-samples',
            endpoint_name='generate-samples',
            handler=self._generate_samples_handler,
        )

    def run(self):
        self.app.run(self.debug)
        self.db = db_connect.get_db_connection()

    def add_endpoint(self, endpoint, endpoint_name, handler):
        self.app.add_url_rule(endpoint, endpoint_name, handler)

    def _set_distribution_handler(self):
        # do the handling of the request here
        pass

    def _generate_samples_handler(self):
        # do the handling of the request here
        pass
