from flask import Response, jsonify, request

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

    bm = BrownianMotion(
        start=10,
        dt=1,
    )
    data = {
        'samples': [],
        'tick_size': tick_size,
    }

    for tick in range(1, number_of_samples + 1):
        sample = bm.sample()

        tick = tick % tick_mod
 
        data['samples'].append([tick, sample])

    import pdb
    pdb.set_trace()
    return jsonify(data)

# TODO: Add a config endpoint to change which type of distribution
# the server will use to generate samples


if __name__ == '__main__':
    app.run(debug=True)
