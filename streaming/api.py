from flask import Response, stream_with_context

import numpy as np

from streaming import create_app

app = create_app()

@app.route('/generate-samples', methods=['POST'])
def generate_samples():
    data = np.random.randint(low=0, high=10000, size=1000)
 
    def generate():
        for num in data:
            yield ','.join([str(num)])

    return Response(stream_with_context(generate()), mimetype='text/csv')

if __name__ == '__main__':
    app.run(debug=True)
