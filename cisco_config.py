from abstract_config import AbstractGen

class CiscoGen(AbstractGen):

    def __init__(self, obj):
        self.obj = obj

    def parse_form_data(self):
        pass

    def load_config_template(self):
        pass

    def generate_config_str(self):
        pass

    def special_config_for_vendor(self):
        pass



