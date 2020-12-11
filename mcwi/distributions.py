import numpy as np
import abc


class Distribution(metaclass=abc.ABCMeta):
    """
    Parameters
    ----------
    params : **kwargs
        Parameters of a probability distribution for streaming. The
        streaming server will know the correct paramters at instantiation
        so.
    """

    def __init__(self, **params):
        pass

    @abc.abstractmethod
    def sample(self):
        """Draw a sample from the defined distribution.

        Returns
        -------
        s : float
            The latest sample from the distribution.
        """

        raise NotImplementedError(
            "This is the base class, it has no probability of being useful.")

    @abc.abstractmethod
    def handle_jump(self, time_delta):
        """Handle a jump in time from the previous call of sampling. This will
        vary by individual distribution.

        Parameters
        ----------
        time_delta : float
            Difference in time between current and previous distribution
            invocation. This is inflated/deflated to match the relative time
            determined by tick size and time dilation factor.

        Returns
        -------
        s : float
            The latest sample from the distribution.
        """

        raise NotImplementedError(
            "This is the base class, it has no probability of being useful.")


class BrownianMotion(Distribution):
    """A simple Brownian motion (or Weiner Process). The standard deviation of
    the normally-distributed next sampled step is equal to the time difference.

    Parameters
    ----------
    start ; float,
        Value from which we start walking.
    sigma : float
        Volatility of each individual tick.

    See Also
    --------
    Distribution
    """

    def __init__(
            self,
            start,
            sigma=1):

        self.last = start
        self.sigma = sigma

    def sample(self):
        s = self.last + np.random.normal(
            0,
            self.sigma)

        self.last = s

        return s

    def handle_jump(self, time_delta):
        s = self.last + np.random.normal(
            0,
            self.sigma*time_delta)

        self.last = s

        return s
