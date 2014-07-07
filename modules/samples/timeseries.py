from __future__ import division
import numpy as np

class AnomalyDetector(object):

    def __init__(self, window = 10):
        self._index = 0
        self._window = window
        self._values = np.zeros(window)
        self._valuesSq = np.zeros(window)
        self._mean = 0
        self._variance = 0
        self._count = 0

    def observation(self, value):
        anomaly = False

        threshold = 3 * np.sqrt(self._variance)
        if self._count > self._window:
            if value > self._mean + threshold:
                value = self._mean + threshold
                anomaly = True
            elif value < self._mean - threshold:
                value = self._mean - threshold
                anomaly = True
        else:
            self._count += 1

        prev_value = self._values[self._index]
        self._values[self._index] = value
        self._valuesSq[self._index] = value ** 2
        self._index = (self._index + 1) % self._window

        self._mean = self._mean - prev_value / self._window + value / self._window
        self._variance = sum(self._valuesSq) / self._window - (self._mean ** 2)

        return anomaly, self._mean
