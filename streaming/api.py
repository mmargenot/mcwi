from flask import (
    Response,
    jsonify,
    request,
    g
)
import sqlite3
import pickle
import time

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

CURRENT_TIME = 0
PREVIOUS_TIME = None


# TODO: Keep track of ticks that have passed since the last samples request.
#       Should this information be stored in a table? `g` in Flask seems to be
#       local to a given request, not truly global within the app.
# TODO: Determine appropriate time dilations factors for real world timestamp
#       vs. simulated time series ticks


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
        g.db = connect_to_db()

    return g.db


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

    assert tick_size in SUPPORTED_TICK_SIZES
    tick_mod = MAX_TICKS_PER_TICK_SIZE[tick_size]

    db = get_db()
    c = db.cursor()
    db_result = c.execute("SELECT * FROM parameters").fetchall()

    if not db_result:
        return jsonify(
            message="Distribution must be set before sampling",
            status_code=400
        )

    dist_type = db_result[0][0]
    assert dist_type in SUPPORTED_DISTRIBUTIONS

    params = pickle.loads(db_result[0][1])

    # TODO: Keep track of last query time to do time diffs and vol scaling for
    #       later samples.

    global CURRENT_TIME
    global PREVIOUS_TIME

    PREVIOUS_TIME = CURRENT_TIME
    CURRENT_TIME = time.time()  # UNIX Time in seconds.nanoseconds

    # Need a jump_dist and a subsequent_dist. How can we abstract these to
    # allow for a variety in distributions when scaling the jump?
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

    # Update start value for next iteration
    new_params = params
    new_params['start'] = data['samples'][1]
    c.execute(
        "UPDATE parameters "
        "SET params = ? "
        "WHERE params = ?",
        (new_params, params)
    )

    return jsonify(data)


def _pickle_params(params):
    return pickle.dumps(params)


# TODO: Add docstrings.
@app.route(
    '/set-distribution',
    methods=['POST'],
)
def set_distribution():
    """
    """
    payload = request.get_json()
    # payload = json.loads(payload)
    dist = payload['distribution']
    params = payload['params']

    params = _pickle_params(params)
    params = sqlite3.Binary(params)

    db = get_db()
    c = db.cursor()

    db_result = c.execute("SELECT * FROM parameters").fetchall()
    try:
        if not db_result:
            c.execute(
                "INSERT INTO parameters VALUES (?, ?)",
                (dist, params)
            )
        else:
            c.execute(
                "UPDATE parameters "
                "SET distribution = ?, params = ? "
                "WHERE distribution = ? AND params = ?",
                (dist, params, db_result[0][0], db_result[0][1])
            )
    except sqlite3.Error as e:
        print('Error Occurred: ', str(e))

    db.commit()
    db.close()

    return jsonify(message=f'Distribution set to {dist}', status_code=200)


if __name__ == '__main__':
    app.run(debug=True)
