from flask import Response, jsonify, request, g
import sqlite3

import numpy as np

from streaming import create_app
from mcwi.distributions import BrownianMotion

app = create_app()

SUPPORTED_TICK_SIZES = ['s', 'm', 'h', 'd']
MAX_TICKS_PER_TICK_SIZE = {
    's': 60,
    'm': 60,
    'h': 24,
    'd': 365,
}
SUPPORTED_DISTRIBUTIONS = {
    'brownian': BrownianMotion
}
# TODO: Instantiate server with distribution type and its parameters. Only
# allow supported distributions.
# TODO: Allow reconfiguration of server with different distributions and/or
# parameters, so that users don't need to boot and reboot.

# TODO: Have object held by the server that dictates the above ^ parameters
# TODO: Write function to update that object.

# TODO: Keep track of ticks that have passed since the last samples request.
#       Should this information be stored in a table? `g` in Flask seems to be
#       local to a given request, not truly global within the app.


# Database connection pattern per:
# https://flask.palletsprojects.com/en/1.1.x/appcontext/
def get_db():
    """Add a connection to the database to the request global variable set.

    Returns
    -------
    Connection
        Connection to the sqlite3 database for the app.
    """
    if 'db' not in g:
        g['db'] = connect_to_db()

    return g['db']


def connect_to_db():
    """Connect to MCWI database.

    Returns
    -------
    conn : Connection
        Connection to the sqlite3 database for the app.
    """
    conn = sqlite3.connect('mcwi.db')

    return conn


@app.teardown_appcontext
def teardown_db(exception):
    """Close DB connection when killing app.
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()


def load_dist_parameters(db):
    c = db.cursor()
    dist_params = c.execute(
        'SELECT params FROM parameters'
    )
    dist_params = dist_params[0]
    dist_params = dist_params.split(',')
    dist_params = [float(p) for p in dist_params]
    return dist_params


@app.route(
    '/generate-samples',
    methods=['POST'],
)
def generate_samples():
    """
    Takes:
    - frequency
    - n: number of samples
    """
    tick_size = request.args.get('tick_size')
    number_of_samples = int(request.args.get('number_of_samples'))
    dist_type = request.args.get('dist')

    assert tick_size in SUPPORTED_TICK_SIZES
    tick_mod = MAX_TICKS_PER_TICK_SIZE[tick_size]

    assert dist_type in SUPPORTED_DISTRIBUTIONS
    db = get_db()
    params = load_dist_parameters(db)
    dist = SUPPORTED_DISTRIBUTIONS[dist_type](
        *params
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

    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
