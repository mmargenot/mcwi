import mcwi
import sklearn.linear_model
from multiprocessing import Process


class TimeSeriesPredictor:

    def __init__(self):
        self.model = sklearn.linear_model.LinearRegression(fit_intercept=True)
        self.goodness_of_fit = {
            'r2': None
        }

    def train_model(self, X, y):
        self.model.fit(X, y)
        self.goodness_of_fit['r2'] = self.model.score(X, y)

    def predict_one(self, X):
        self.model.predict(X)


model = TimeSeriesPredictor()

app = mcwi.streaming.api.McwiApp()
server = Process(target=app.run)
server.start()

mcwi_client = mcwi.streaming.client.Client(url='http://localhost:5000')
mcwi_client.set_distribution(
    'brownian',
    {'start': 100, 'sigma': 1}
)

s = mcwi_client.generate_samples(100)
model.train(s[:-1], s[1:])  # AR(1) model
print('Predicted Next Value: ', model.predict(s[-1]))

server.terminate()
server.join()
