import numpy as np

class PingProviderStatisics:
    def __init__(self, time: list[float]):
        self.time = time
        self._nptime = np.array(time, dtype=np.float64)
        self._min = self._nptime.min()
        self._max = self._nptime.max()
        self._mean = self._nptime.mean()
        self._median = np.median(self._nptime)
        self._std = self._nptime.std()
        self._var = self._nptime.var()
    
    @property
    def min(self) -> float:
        return self._min

    @property
    def max(self) -> float:
        return self._max

    @property
    def mean(self) -> float:
        return self._mean

    @property
    def median(self) -> float:
        return self._median

    @property
    def std(self) -> float:
        return self._std

    @property
    def var(self) -> float:
        return self._var
    
    @property
    def cv(self) -> float:
        return self._std / self._mean