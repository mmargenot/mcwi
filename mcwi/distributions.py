import numpy as np
import abc


class DataType(abc.ABCMeta):

    def __init__(self):
        pass

    @abc.abstractmethod
    def sample_one(self):
        pass

    @abc.abstractmethod
    def sample_n(self, n):
        pass


class RandomWalk(DataType):

    def __init__(self, params):
        pass
