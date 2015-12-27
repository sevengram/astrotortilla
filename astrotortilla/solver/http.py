import json
import os
import logging
import urllib
import urllib2


def build_url(service):
    return 'http://nova.astrometry.net/api/' + service


def post_data(service, data=None, headers=None):
    try:
        req_data = {'request-json': json.dumps(data or {})}
        req = urllib2.Request(url=build_url(service), data=urllib.urlencode(req_data), headers=headers or {})
        resp = urllib2.urlopen(req)
        return json.loads(resp.read()) if resp.code == 200 else None
    except (ValueError, IOError):
        return None


def post_file(service, filepath, data=None, headers=None):
    req_data = {'request-json': json.dumps(data or {})}
    content_type, body = encode_multipart_formdata(req_data, filepath)
    headers = headers or {}
    headers['Content-Type'] = content_type
    req = urllib2.Request(url=build_url(service), data=body, headers=headers)
    resp = urllib2.urlopen(req)
    return json.loads(resp.read()) if resp.code == 200 else None


def get(service, headers=None):
    try:
        req = urllib2.Request(url=build_url(service), headers=headers or {})
        resp = urllib2.urlopen(req)
        return json.loads(resp.read()) if resp.code == 200 else None
    except (ValueError, IOError):
        return None


def encode_multipart_formdata(fields, filepath):
    boundary = '----------ThIs_Is_tHe_bouNdaRY_$'
    crlf = '\r\n'
    l = []
    filepath = filepath.encode('utf8')
    for key, value in fields.iteritems():
        l.append('--' + boundary)
        l.append('Content-Disposition: form-data; name="%s"' % key)
        l.append('')
        l.append(value)
    fd = open(filepath, 'rb')
    l.append('--' + boundary)
    l.append('Content-Disposition: form-data; name="file"; filename="%s"' % os.path.basename(filepath))
    l.append('Content-Type: application/octet-stream')
    l.append('')
    l.append(fd.read())
    l.append('--' + boundary + '--')
    l.append('')
    body = crlf.join(l)
    content_type = 'multipart/form-data; boundary=%s' % boundary
    return content_type, body
