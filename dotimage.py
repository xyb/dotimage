#!/usr/bin/env python

import os
import subprocess
import unittest
import uuid
from StringIO import StringIO

from flask import Flask, make_response, request, Response
from werkzeug import secure_filename

DEBUG = os.environ.get('DEBUG', '')
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/tmp/dotimage')

DOT = 'gprof2dot -f {profformat} {profpath} | dot -T{imgformat} -o {imgpath}'
APP_DIR = os.path.dirname(os.path.realpath(__file__))

INDEX_HTML = '''<!doctype html>
<title>Upload Profiling File</title>
<h1>Upload Profiling File</h1>
<form action="" method=post enctype=multipart/form-data>
    <p><input type=file name=dot>
        <select name=format>
            <option value="pstats">pstats (Python profile, cProfile)</option>
            <option value="hprof">hprof (Java Profiler)</option>
            <option value="prof">prof</option>
            <option value="gprof">gprof (GNU gprof)</option>
            <option value="perf">perf (Linux)</option>
            <option value="oprofile">oprofile</option>
            <option value="callgrind">Valgrind's callgrind tool</option>
            <option value="sysprof">sysprof</option>
            <option value="xperf">xperf</option>
            <option value="axe">VTune Amplifier XE</option>
        </select>
        <select name=imageformat>
            <option value="png">PNG</option>
        </select>
        <input type=submit value=Upload>
</form>
'''

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/', methods=['GET'])
def index():
    return make_response(INDEX_HTML)


def save(id, file, dir):
    filename = '%s-%s' % (id, secure_filename(file.filename))
    path = os.path.join(dir, filename)
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    file.save(path)
    return path


def draw_graph(id, prof, profformat, imageformat, imagedir):
    filename = '%s-%s' % (id, secure_filename('output.png'))
    image_path = os.path.join(imagedir, filename)
    args = DOT.format(profformat=profformat, profpath=prof,
                      imgformat=imageformat, imgpath=image_path)
    proc = subprocess.Popen(args=args, shell=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            cwd=APP_DIR)
    stdout, stderr = proc.communicate(None)
    error = ''
    if 'Traceback' in stderr:
        error = 'Error: please upload profiling file with correct type'
    if not os.path.exists(image_path):
        error = '404: File Not Found, please upload profiling file', 404
    return error, image_path


@app.route('/', methods=['POST'])
def profiling():
    id = uuid.uuid4()
    prof = save(id, request.files.get('dot'), app.config['UPLOAD_FOLDER'])

    format = request.form['format']
    imageformat = request.form.get('imageformat', 'png')

    error, ipath = draw_graph(id, prof, format, imageformat,
                              app.config['UPLOAD_FOLDER'])
    if error:
        return error
    image = open(ipath).read()
    return Response(image, content_type='image/png')


TEST_PSTATS_CONTENT = '''
eygDAAAAcwQAAABhLnB5aQEAAAB0CAAAADxtb2R1bGU+KAUAAABpAQAAAGkBAAAAZwBY0lEOZgM/
ZwBY0lEOZgM/eygDAAAAdAcAAABwcm9maWxlaQAAAABjAAAAAAAAAAABAAAAQAAAAHMJAAAAZAAA
R0hkAQBTKAIAAAB0BQAAAGhlbGxvTigAAAAAKAAAAAAoAAAAACgAAAAAcwQAAABhLnB5UgAAAAAB
AAAAcwAAAABpAQAAADAoAwAAAHQAAAAAaQAAAABzCgAAAHNldHByb2ZpbGUoBQAAAGkBAAAAaQEA
AABnAOXrMvynOz9nAOXrMvynOz97KAMAAABSAQAAAGkAAAAAYwAAAAAAAAAAAQAAAEAAAABzCQAA
AGQAAEdIZAEAUygCAAAAUgIAAABOKAAAAAAoAAAAACgAAAAAKAAAAABzBAAAAGEucHlSAAAAAAEA
AABzAAAAAGkBAAAAMCgDAAAAUgEAAABpAAAAAHQIAAAAcHJvZmlsZXIoBQAAAGkAAAAAaQAAAABp
AAAAAGkAAAAAezAoAwAAAFIBAAAAaQAAAABjAAAAAAAAAAABAAAAQAAAAHMJAAAAZAAAR0hkAQBT
KAIAAABSAgAAAE4oAAAAACgAAAAAKAAAAAAoAAAAAHMEAAAAYS5weVIAAAAAAQAAAHMAAAAAKAUA
AABpAQAAAGkBAAAAZwAo+nyUEQc/Z4C6YkZ4e0A/eygDAAAAUgEAAABpAAAAAFIEAAAAaQEAAAAw
MA=='''.decode('base64')


class DotImageTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_index(self):
        r = self.app.get('/')
        assert 'Upload' in r.data

    def test_profile_file(self):
        r = self.app.post('/',
                          data=dict(dot=(StringIO(TEST_PSTATS_CONTENT),
                                         'output.pstats'),
                                    format='pstats',
                                    imageformat='png'),
                          follow_redirects=True)
        assert r.status_code, 200
        assert r.content_type, 'image/png'
        assert r.data

    def test_empty_profile_file(self):
        r = self.app.post('/',
                          data=dict(dot=(StringIO(''), 'output.pstats'),
                                    format='pstats',
                                    imageformat='png'),
                          follow_redirects=True)
        assert r.status_code, 404


def test():
    unittest.main()


if __name__ == '__main__':
    import sys
    if sys.argv[1:] == ['test']:
        del sys.argv[1]
        test()
    else:
        if DEBUG:
            app.debug = True
        app.run(host="0.0.0.0")
