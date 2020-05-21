import numpy as np
import abc


class DataType(abc.ABCMeta):

    def __init__(self):
        pass

    @abc.abstractmethod
    def step_forward_one(self):
        """Move forward a single step in a random walk according to the
        parameters of the distribution.

        Returns
        -------
        next_step : float
            The next step in the random walk, to be served to the consumer.
        """
        pass

    @abc.abstractmethod
    def step_forward_n(self, n):
        """Move forward n steps in a random walk according to the parameters
        of the distribution.

        Parameters
        ----------
        n : int
            Number of steps to move forward.

        Returns
        -------
        next_step : float
            The next step in the random walk, to be served to the consumer.
        """
        pass


class BrownianMotion(DataType):
    """A simple Brownian motion. The standard deviation of the normally-distributed
    next sampled step is equal to the time difference.

    See Also
    --------
    DataType
    """

    def __init__(self, init, mu=0, sigma=1):
        self.current_value = init
        self.mu = mu
        self.sigma = sigma

    def step_forward_one(self):
        next_step = self.current_value + np.random.normal(
            mu=self.mu,
            sigma=self.sigma)

        self.current_value = next_step

        return next_step

    def step_forward_n(self, n):
        next_step = self.current_value + np.random.normal(
            mu=self.mu,
            sigma=self.sigma*n)

        self.current_value = next_step

        return next_step
