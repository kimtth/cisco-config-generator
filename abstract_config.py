from abc import ABCMeta,abstractmethod

class AbstractGen (metaclass=ABCMeta):

    @abstractmethod
    def parse_form_data(self):
        pass

    @abstractmethod
    def load_config_template(self):
        pass

    @abstractmethod
    def generate_config_str(self):
        pass

    @abstractmethod
    def special_config_for_vendor(self):
        pass

