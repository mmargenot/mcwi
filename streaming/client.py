import time
import requests

# server is http://localhost:5000/generate-samples


class Client:
    """
    This might be useful?
    https://stackoverflow.com/questions/59162868/python-requests-stream-iter-content-chunks-into-a-pandas-read-csv-function
    might be smarter than trying to build our own iterator.
    """

    def __init__(self, address):
        self.server = address

    # TODO: This methodology still results in some weird artifacts when
    # pinging the server for samples. There might be a better way to handle
    # the stream itself rather than just the raw bytes, beyond what we have
    # looked at.
    def generate_samples(self, N):
        url = self.server + 'generate-samples'
        r = requests.post(url, stream=True)

        samples = []

        previous_right = None

        left = None
        right = None

        # is there a smarter way to estimate chunk size based on the number of
        # samples?
        for chunk in r.iter_content(9):
            chunk = str(chunk)
            chunk = chunk.replace("b", '')
            chunk = chunk.replace("'", '')

            # print("CHUNK IS:", chunk)

            data = str(chunk).split(',')

            if len(data) > 1:
                left, right = data

                # print('left is:', left)
                # print('right is:', right)

                if previous_right is not None:
                    left = previous_right + left
                    # print("left is now:", left)
                    samples.append(left)

                previous_right = right
            else:
                previous_right = None

            if len(samples) >= N:
                break

        # not floats yet, still strings
        return samples
