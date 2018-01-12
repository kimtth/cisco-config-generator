from abc import ABCMeta, abstractmethod

# python 3
# https://stackoverflow.com/questions/13646245/is-it-possible-to-make-abstract-classes-in-python
class AbstractGen(metaclass=ABCMeta):

    @abstractmethod
    def generate_config(self, post_data):
        pass
