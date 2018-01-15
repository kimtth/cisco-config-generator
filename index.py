import bottle
import os
from datetime import datetime
from bottle import request, run, template
from bottle import static_file
from cisco_config import CiscoGen
from config_block import ConfigBlock

'''
get reference from https://github.com/koddr/bottle-vue-kickstart/blob/master/run.py
'''

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
bottle.TEMPLATE_PATH.insert(0, os.path.join(BASE_DIR, 'templates'))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
IMG_DIR = os.path.join(BASE_DIR, 'images')
app = bottle.default_app()


@app.get('/')
def index(filename='index'):
    return template(filename)


@app.get('/static/<filename:path>')
def get_static_files(filename):
    return static_file(filename, root=STATIC_DIR)


@app.get('/images/<filename:path>')
def img_static_file(filename):
    return static_file(filename, root=IMG_DIR)


@app.error(404)
def error404(error):
    return 'Nothing here, sorry'

@app.get('/config_clear')
def clear():
    ConfigBlock.BUFF = ""
    ConfigBlock.POS_INITIAL = ""
    ConfigBlock.POS_AAA = ""
    ConfigBlock.POS_DHCP = ""
    ConfigBlock.POS_OBJGROUP = ""
    ConfigBlock.POS_VPDN = ""
    ConfigBlock.POS_POLMAP = ""
    ConfigBlock.POS_VLAN = ""
    ConfigBlock.POS_INT = ""
    ConfigBlock.POS_NAT = ""
    ConfigBlock.POS_IPV4ACL = ""
    ConfigBlock.POS_RADIUS = ""
    ConfigBlock.POS_LINE = ""
    ConfigBlock.POS_NTP = ""

@app.post('/config_cisco_basic_route')  # or @app.route('/config_analyze', method='POST')
def config_analyze(filename='cisco_basic_router.tpl'):
    post_data = request.body.read()
    print("debug postdata: " + str(post_data))

    post_data = request.forms
    #intial_value_mapper(post_data)
    cis_gen = CiscoGen()
    ret = cis_gen.generate_config(post_data)
    print(ret)
    local_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    '''
    # sample response
        >>> from bottle import template
        >>> template('Hello {{name}}!', name='World')
        u'Hello World!'

        >>> my_dict={'number': '123', 'street': 'Fake St.', 'city': 'Fakeville'}
        >>> template('I live at {{number}} {{street}}, {{city}}', **my_dict)
        u'I live at 123 Fake St., Fakeville'
    '''

    response_dict = ConfigBlock.RES_DICT
    return template(filename, developer="Kim", local_time=local_time, **response_dict)

# For debugging
def intial_value_mapper(post_data):
    for key, value in post_data.iteritems():
        if value == "":
            if key == "fqdn_hostname":
                post_data[key] = "router1.lan.local"
            elif key == "dhcp_onvlan":
                post_data[key] = "all"
            elif key == "dhcp_scope":
                post_data[key] = "195.130.131.139"
            elif key == "sshaltport":
                post_data[key] = "8022"
            elif key == "wan_interface":
                post_data[key] = "GigabitEthernet0/1"
            elif key == "enSSH":
                post_data[key] = "yes"
            elif key == "vlan_ips":
                post_data[key] = "10.1.v.1/24"
            elif key == "admin_password":
                post_data[key] = "admin"
            elif key == "svpnradius_serverkey":
                post_data[key] = "xxxxxxx"
            elif key == "ntp_server_ip":
                post_data[key] = "192.104.37.238"
            elif key == "vlan_style":
                post_data[key] = "subinterface"
            elif key == "vlans":
                post_data[key] = "1,2"
            elif key == "svpn":
                post_data[key] = "yes"
            elif key == "privateSSH":
                post_data[key] = "yes"
            elif key == "dnsServer":
                post_data[key] = "no"
            elif key == "guestvlan":
                post_data[key] = "0"
            elif key == "qos_upload":
                post_data[key] = "8000"
            elif key == "svpnradius_ip":
                post_data[key] = "192.168.1.1"
            elif key == "admin_username":
                post_data[key] = "admin"
            elif key == "lan_interface":
                post_data[key] = "GigabitEthernet0/0"
            elif key == "svpnRadius":
                post_data[key] = "no"
            elif key == "svpnradius_name":
                post_data[key] = "rrad1"

if __name__ == '__main__':
    run(app, server='auto', host='localhost', port=8080, reloader=True)
