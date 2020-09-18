from flask import Response, stream_with_context

import numpy as np

from streaming import create_app
from mcwi.distributions import BrownianMotion

app = create_app()

@app.route('/generate-samples', methods=['POST'])
def generate_samples():
    """
    Takes:
    - frequency
    - n: number of samples
    """
    bm = BrownianMotion(
        start=10,
        dt=1,
    )

    # load initial data points into buffer
    data_buffer = np.zeros(shape=256)
    for i in range(data_buffer.size):
        sample = bm.sample()
        data_buffer[i] = sample

    def generate(num_samples):
        while True:
            # give the number of data points that the client asks for
            char_data = np.char.mod('%f', data_buffer)[-num_samples:]

            sample_str = ','.join(char_data) + ','
 
            yield bytes(sample_str[-num_samples * 8:], 'utf-8')

            # get rid of the last `num_samples` data points in the buffer
            # shift the remaining data and rewrite the first `num_samples` data point
            data_buffer[:-num_samples] = data_buffer[num_samples:]
            data_buffer[-num_samples:] = np.array([
                bm.sample() for x in range(num_samples)
            ])

    return Response(
        stream_with_context(generate(num_samples=10)),
        #mimetype='text/csv',
    )

if __name__ == '__main__':
    app.run(debug=True)
