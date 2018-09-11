from __future__ import (absolute_import, division,
                        print_function, unicode_literals)


from abc import ABCMeta, abstractmethod, abstractproperty
from six import with_metaclass


class AbstractWeatherDataProvider(with_metaclass(ABCMeta)):

    def __init__(self):
        self.raw = None
        self.raw_f = None

    @abstractproperty
    def pressure(self):
        pass

    @abstractmethod
    def update(self, location):
        pass
