class ConfigBlock:

    POS_INITIAL = ""
    BUFF = ""
    BLOCK = "!\n"

    POS_AAA = ""
    POS_DHCP = ""
    POS_OBJGROUP = ""
    POS_VPDN = ""
    POS_POLMAP = ""
    POS_VLAN = ""
    POS_INT = ""
    POS_NAT = ""
    POS_IPV4ACL = ""
    POS_RADIUS = ""
    POS_LINE = ""
    POS_NTP = ""

    RES_DICT = dict()

    def __init__(self):
        pass

    @staticmethod
    def add_block_suffix(config_str):
        config_str = config_str \
                     + "!\n"
        return config_str




