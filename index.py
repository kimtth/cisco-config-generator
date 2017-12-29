import bottle
import os
from bottle import route, run, template
from bottle import static_file

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

@app.post('/config_analyze')
def config_analyze(filename='config_analyze.tpl'):
    return template(filename)

if __name__ == '__main__':
        run(app, server='auto', host='localhost', port=8080, reloader=True)