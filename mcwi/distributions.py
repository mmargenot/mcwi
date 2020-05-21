import numpy as np
import abc


class DataType(abc.ABCMeta):

    def __init__(self):
        pass

    @abc.abstractmethod
    def step_forward_one(self):
        pass

    @abc.abstractmethod
    def step_forward_n(self, n):
        pass


class BrownianMotion(DataType):
    """A simple Brownian motion. The standard deviation of the normally-distributed
    next sampled step is equal to the time difference.
    """

    def __init__(self, init, mu=0, sigma=1):
        self.init = init
        self.mu = mu
        self.sigma = sigma

    def step_forward_one(self):
        next_step = self.init + np.random.normal(
            mu=self.mu,
            sigma=self.sigma)

        return next_step

    def step_forward_n(self, n):
        next_step = self.init + np.random.normal(
            mu=self.mu,
            sigma=self.sigma*n)

        return next_step
