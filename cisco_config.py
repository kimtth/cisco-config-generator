from abstract_config import AbstractGen
from bottle import FormsDict
from config_block import ConfigBlock


class CiscoGen(AbstractGen):

    def __init__(self):
        pass

    def generate_config(self, post_data):
        if isinstance(post_data, FormsDict):
            # for debugging
            print(">>> debug data -- start")
            for key, value in post_data.items():
                print(key + ":" + value)
            print(">>> debug data -- end")

            # generate
            self.__decouple_common_block(post_data)
            self.__decouple_common_router_assembler(post_data)
            self.__cisco_basic_router(post_data)

            # mapping the results into response data
            buff = self.__config_block_broker()
            ConfigBlock.RES_DICT["config_str"] = buff

            return ">>> ok"
        else:
            return ">>> error"

    def __config_block_broker(self):
        ConfigBlock.BUFF += ConfigBlock.POS_INITIAL

        ConfigBlock.BUFF += ConfigBlock.POS_AAA
        ConfigBlock.BUFF += ConfigBlock.POS_DHCP
        ConfigBlock.BUFF += ConfigBlock.POS_OBJGROUP
        ConfigBlock.BUFF += ConfigBlock.POS_VPDN
        ConfigBlock.BUFF += ConfigBlock.POS_POLMAP
        ConfigBlock.BUFF += ConfigBlock.POS_VLAN
        ConfigBlock.BUFF += ConfigBlock.POS_INT
        ConfigBlock.BUFF += ConfigBlock.POS_NAT
        ConfigBlock.BUFF += ConfigBlock.POS_IPV4ACL
        ConfigBlock.BUFF += ConfigBlock.POS_RADIUS
        ConfigBlock.BUFF += ConfigBlock.POS_LINE
        ConfigBlock.BUFF += ConfigBlock.POS_NTP

        return ConfigBlock.BUFF

    def __decouple_common_block(self, post_data):
        self.__decouple_aaa_config_block()
        fqdn_value = post_data.get("fqdn_hostname")
        self.__decouple_fqdn_hostname(fqdn_value)
        self.__decouple_admin_user(post_data)
        self.__decouple_line_block()

    # part1. start -- common
    def __decouple_aaa_config_block(self):
        ConfigBlock.POS_AAA += "aaa new-model\n"
        ConfigBlock.POS_AAA += "aaa authentication enable default none\n"
        ConfigBlock.POS_AAA += "aaa authentication ppp default local\n"
        ConfigBlock.POS_AAA += "aaa authorization exec default none\n"
        ConfigBlock.POS_AAA += "aaa authorization commands 0 default none\n"
        ConfigBlock.POS_AAA += "aaa authorization commands 15 default none\n"
        ConfigBlock.POS_AAA += ConfigBlock.BLOCK

    # - input: router1.lan.local
    # - output:
    #    hostname router1
    #    ip domain-name lan.local
    def __decouple_fqdn_hostname(self, value):
        value = value.replace(" ", "")
        cut_str = value.split(".")
        ConfigBlock.POS_INITIAL += "hostname " + cut_str[0] + "\n" \
                                   + "ip domain-name" + ".".join(cut_str[1:]) + "\n"

    def __decouple_admin_user(self, post_data):
        ConfigBlock.POS_INITIAL += "username " + post_data.get(
            "admin_username") + " privilege 15 password " + post_data.get(
            "admin_password") + "\n"

    def __decouple_line_block(self):
        ConfigBlock.POS_LINE += "line con 0\n";
        ConfigBlock.POS_LINE += 'logging synchronous\n'
        ConfigBlock.POS_LINE += '!\n'

    def __decouple_enSSH(self, post_data):
        ConfigBlock.POS_INITIAL += "!          \n" \
                                   + "!    /\\    \n" \
                                   + "!   /  \\   If your device doesn't have an RSA key yet, execute the following command:\n" \
                                   + "!  / !! \\  crypto key generate rsa general-keys modulus 2048 \n" \
                                   + "! /------\\  \n" \
                                   + "ip ssh version 2\n"

        ssh_alt_port = post_data.get("sshaltport")
        if ssh_alt_port != "22" or "0":
            ConfigBlock.POS_INITIAL += "ip ssh port " + ssh_alt_port + " rotary 1 \n"

        private_ssh_only = str(post_data.get("privateSSH")).lower()
        if private_ssh_only == "yes":
            ConfigBlock.POS_IPV4ACL = "ip access-list extended SSH\n" \
                                      + " permit tcp object-group PrivateRanges any eq 22\n" \
                                      + " permit tcp any any eq 8022\n"
            ConfigBlock.POS_IPV4ACL += ConfigBlock.BLOCK

        ConfigBlock.POS_LINE += "line vty 0 15\n"
        ConfigBlock.POS_LINE += " logging synchronous\n"
        ConfigBlock.POS_LINE += " transport input ssh\n"

        if ssh_alt_port != "22" or "0":
            ConfigBlock.POS_LINE += " rotary 1\n"
        if private_ssh_only == "yes":
            ConfigBlock.POS_LINE += " access-class SSH in\n"

        ConfigBlock.POS_LINE += ConfigBlock.BLOCK

    # part1. end --- common

    # part2. start -- common router
    def __decouple_common_router_assembler(self, post_data):
        ConfigBlock.POS_INITIAL += "no ip bootp server"

        if post_data.get("enSSH") == "yes":
            self.__decouple_enSSH(post_data)

        self.___decouple_basic_qos(post_data)

        ConfigBlock.POS_IPV4ACL += "ip access-list extended NAT\n" \
                                   + "deny ip any object-group PrivateRanges\n" \
                                   + "permit ip any any\n"

        ntp_server_ips = post_data.getall("ntp_server_ip")
        if len(ntp_server_ips) > 0:
            for ip in ntp_server_ips:
                if ip != "":
                    ConfigBlock.POS_NTP += "ntp server "
                    ConfigBlock.POS_NTP += ip + "\n"

        ConfigBlock.POS_OBJGROUP += "object-group network PrivateRanges\n" \
                                    + " 192.168.0.0 255.255.0.0\n" \
                                    + " 172.16.0.0 255.240.0.0\n" \
                                    + " 10.0.0.0 255.0.0.0\n" \
                                    + "!\n"

        ConfigBlock.POS_IPV4ACL += "ip access-list extended Internet-IN\n" \
                                   + " deny udp any any eq 53\n" \
                                   + " deny tcp any any eq 53\n" \
                                   + " permit ip any any\n" \

        ConfigBlock.POS_IPV4ACL += "!\n"

        # VLAN config
        self.__decouple_vlan_setting(post_data)

    def __decouple_vlan_setting(self, post_data):
        vlans = post_data.get("vlans")
        vlan_list = self.__parse_to_number(vlans)

        vlan_style = post_data.get("vlan_style")
        ConfigBlock.POS_INT = ""
        for vlan in vlan_list:
            vlan_str = str(vlan)

            if vlan_style == "subinterface":
                lan_interface = post_data.get("lan_interface")
                ConfigBlock.POS_INT += "interface "
                ConfigBlock.POS_INT += lan_interface
                ConfigBlock.POS_INT += "." + vlan_str + "\n"
                ConfigBlock.POS_INT += " encapsulation dot1Q " + vlan_str + "\n"
            else:
                ConfigBlock.POS_VLAN += "vlan " + vlan_str
                ConfigBlock.POS_INT += "interface Vlan " + vlan_str

            ConfigBlock.POS_INT += " no ip proxy-arp\n"
            ConfigBlock.POS_INT += " no ip redirects\n"
            ConfigBlock.POS_INT += " ip nat inside\n"
            ConfigBlock.POS_INT += " no ip unreachables\n"

            # IP address for the VLANs. Format: 192.0.2.1/24. v will be replaced by the VLAN number
            vlan_ip_with_subnet = post_data.get("vlan_ips")
            vlan_ip_with_subnet = str(vlan_ip_with_subnet).replace("v", vlan_str)

            vlan_ips_split = str(vlan_ip_with_subnet).split('/')
            ip_address = vlan_ips_split[0]
            subnet_mask = vlan_ips_split[1]

            ConfigBlock.POS_INT += " ip address " + ip_address + " " + self.__calcDottedNetmask(subnet_mask) + "\n"
            ConfigBlock.POS_INT += " no shutdown" + "\n"

            dhcp_onvlan = post_data.get("dhcp_onvlan")
            if dhcp_onvlan == "all":
                dhcp_onvlan = str(vlan)
            dhcp_onvlan_list = self.__parse_to_number(dhcp_onvlan)
            if dhcp_onvlan == "all" or vlan in dhcp_onvlan_list:
                ConfigBlock.POS_DHCP += "ip dhcp pool " + vlan_ip_with_subnet + "\n"
                ConfigBlock.POS_DHCP += " network " + vlan_ip_with_subnet + "\n"
                ConfigBlock.POS_DHCP += "default-router " + ip_address + "\n"

                fqdn_hostname = post_data.get("fqdn_hostname")
                cut_str = fqdn_hostname.split(".")
                ConfigBlock.POS_DHCP += "domain-name " + ".".join(cut_str[1:]) + "\n"

                dns_server = post_data.get("dnsServer")
                if dns_server == "yes":
                    ConfigBlock.POS_DHCP += "dns-server " + ip_address + "\n"
                else:
                    ConfigBlock.POS_DHCP += "dns-server " + self.__get_dns_ips(post_data) + "\n"

                ConfigBlock.POS_DHCP += "!\n"

            guestvlan = post_data.get("guestvlan")
            if vlan_str == guestvlan:
                ConfigBlock.POS_IPV4ACL += "ip access-list extended Guest-IN" + "\n"
                ConfigBlock.POS_IPV4ACL += " permit ip any host " + "\n"
                ConfigBlock.POS_IPV4ACL += " deny ip any object-group PrivateRanges" + "\n"
                ConfigBlock.POS_IPV4ACL += " permit ip any any" + "\n"
                ConfigBlock.POS_IPV4ACL += "!\n"

                ConfigBlock.POS_INT += "ip access-group Guest-IN in" + "\n"

            ConfigBlock.POS_INT += "!\n"

    def __get_dns_ips(self, post_data):
        dhcp_scope_list = post_data.getall("dhcp_scope")
        temp_buff = " ".join(dhcp_scope_list[0:])
        return temp_buff

    # How to convert the CIDR notation (192.168.0.0/24) of a subnetmask to the dotted decimal form (255.255.255.0).
    def __calcDottedNetmask(self, mask):
        bits = 0
        mask = int(mask)
        for i in range(32 - mask, 32):
            bits |= (1 << i)
        return "%d.%d.%d.%d" % ((bits & 0xff000000) >> 24, (bits & 0xff0000) >> 16, (bits & 0xff00) >> 8, (bits & 0xff))

    def __parse_to_number(self, value):
        result = []
        for part in value.split(','):
            if '-' in part:
                a, b = part.split('-')
                a, b = int(a), int(b)
                result.extend(range(a, b + 1))
            else:
                a = int(part)
                result.append(a)
        return result

    def ___decouple_basic_qos(self, post_data):
        qos_int = int(post_data.get("qos_upload")) * 1000
        ConfigBlock.POS_POLMAP += "class-map match-any VoIP\n" \
                                  + " match protocol sip\n" \
                                  + " match protocol rtp audio\n" \
                                  + "!\n" \
                                  + "policy-map Internet-Output\n" \
                                  + " class VoIP\n" \
                                  + "  priority 512\n" \
                                  + " class class-default\n" \
                                  + "  fair-queue\n" \
                                  + "!\n" \
                                  + "policy-map WAN-Output\n" \
                                  + " class class-default\n" \
                                  + "  shape average " + str(qos_int) + "\n" \
                                  + "   service-policy Internet-Output \n" \
                                  + "!\n"

        # part2. end -- common router

    # part3. start -- cisco basic router
    def __decouple_simple_vpn(self, post_data, wan_interface):
        svpn_radius = post_data.get("svpnRadius")
        svpnradius_name = post_data.get("svpnradius_name")
        svpnradius_ip = post_data.get("svpnradius_ip")
        svpnradius_serverkey = post_data.get("svpnradius_serverkey")

        if svpn_radius == "yes":
            ConfigBlock.POS_AAA += "aaa group server radius PPTPVPNRadius \n"
            ConfigBlock.POS_AAA += "server name " + svpnradius_name + "\n"
            ConfigBlock.POS_AAA += "!\n"
            ConfigBlock.POS_AAA += "aaa authentication ppp PPTPVPN group PPTPVPNRadius" + "\n"
            ConfigBlock.POS_AAA += "aaa authorization network PPTPVPN group PPTPVPNRadius" + "\n"
            ConfigBlock.POS_AAA += "!\n"
            ConfigBlock.POS_RADIUS += "radius server " + svpnradius_name + "\n"
            ConfigBlock.POS_RADIUS += "address ipv4 " + svpnradius_ip + "\n"
            ConfigBlock.POS_RADIUS += "key " + svpnradius_serverkey + "\n"
            ConfigBlock.POS_RADIUS += "!\n"

        ConfigBlock.POS_INITIAL += "ip local pool VPN 10.1.254.100 10.1.254.110" + "\n"

        ConfigBlock.POS_VPDN += "vpdn enable" + "\n"
        ConfigBlock.POS_VPDN += "vpdn logging" + "\n"
        ConfigBlock.POS_VPDN += "vpdn logging local" + "\n"
        ConfigBlock.POS_VPDN += "vpdn logging user" + "\n"
        ConfigBlock.POS_VPDN += "!\n"

        ConfigBlock.POS_VPDN += "vpdn-group 1" + "\n"
        ConfigBlock.POS_VPDN += " accept-dialin" + "\n"
        ConfigBlock.POS_VPDN += "  protocol pptp" + "\n"
        ConfigBlock.POS_VPDN += "  virtual-template 1" + "\n"
        ConfigBlock.POS_VPDN += "!\n"

        ConfigBlock.POS_INT += "interface Virtual-Template1" + "\n"
        ConfigBlock.POS_INT += " ip unnumbered " + wan_interface + "\n"
        if svpn_radius == "yes":
            ConfigBlock.POS_INT += " ppp authentication ms-chap-v2 PPTPVPNRadius" + "\n"
            ConfigBlock.POS_INT += " ppp authorization PPTPVPNRadius" + "\n"
        else:
            ConfigBlock.POS_INT += " ppp authentication ms-chap-v2" + "\n"
        ConfigBlock.POS_INT += " ip nat inside" + "\n"
        ConfigBlock.POS_INT += " ppp encrypt mppe auto" + "\n"
        ConfigBlock.POS_INT += " peer default ip address pool VPN" + "\n"

        ConfigBlock.POS_INT += "!\n"

    def __cisco_basic_router(self, post_data):
        dns_server = post_data.get("dnsServer")
        if dns_server == "yes":
            ConfigBlock.POS_INT += "ip dns server" + "\n"

        vlan_style = post_data.get("vlan_style")
        if vlan_style == "subinterface":
            # Enable the main interface where subinterfaces will be attached to
            ConfigBlock.POS_INT += "interface " + post_data.get("lan_interface") + "\n"
            ConfigBlock.POS_INT += " no ip proxy-arp" + "\n"
            ConfigBlock.POS_INT += " no shutdown" + "\n"
            ConfigBlock.POS_INT += " no ip unreachables" + "\n"
            ConfigBlock.POS_INT += " no ip redirects" + "\n"
            ConfigBlock.POS_INT += " no mop enabled" + "\n"

            ConfigBlock.POS_INT += "!\n"

        svpn = post_data.get("svpn")
        wan_interface = post_data.get("wan_interface")
        if svpn == "yes":
            self.__decouple_simple_vpn(post_data, wan_interface)

        # WAN interface
        ConfigBlock.POS_INT += "interface " + wan_interface + "\n"
        ConfigBlock.POS_INT += " ip address dhcp" + "\n"
        ConfigBlock.POS_INT += " ip nat outside" + "\n"
        ConfigBlock.POS_INT += " ip access-group Internet-IN in" + "\n"
        ConfigBlock.POS_INT += " service-policy output WAN-Output" + "\n"
        ConfigBlock.POS_INT += " no shutdown" + "\n"
        ConfigBlock.POS_INT += " no ip proxy-arp" + "\n"
        ConfigBlock.POS_INT += " no ip redirects" + "\n"
        ConfigBlock.POS_INT += " no ip unreachables" + "\n"
        ConfigBlock.POS_INT += " no cdp enable" + "\n"
        ConfigBlock.POS_INT += " no mop enabled" + "\n"

        ConfigBlock.POS_INT += "!\n"

        # NAT
        ConfigBlock.POS_NAT += "ip nat inside source list NAT interface " + wan_interface + " overload" + "\n"
        ConfigBlock.POS_NAT += "!\n"

    # part3. end -- cisco basic router
