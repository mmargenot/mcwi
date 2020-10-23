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
            The latest sample from the Brownian motion.
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
    dt : float
        The time increment that passes with each tick.
    delta : float, optional
        The speed of the Brownian motion.

    See Also
    --------
    Distribution
    """

    def __init__(
            self,
            start,
            dt,
            delta=1):

        self.last = start
        self.dt = dt
        self.delta = delta

    def sample(self):
        s = self.last + np.random.normal(
            0,
            self.delta*np.sqrt(self.dt))

        self.last = s

        return s
