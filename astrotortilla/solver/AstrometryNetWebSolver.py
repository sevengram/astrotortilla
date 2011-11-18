from ..IPlateSolver import IPlateSolver, Solution
from ..units import Coordinate
import os, os.path, time
import urllib2, sys, os, string, re, random, mimetypes, time, urllib
import binascii
import gettext
t = gettext.translation('astrometrynetwebsolver', 'locale', fallback=True)
_ = t.gettext

# vim: set fileencoding=UTF-8 : ts=4 sts=4 sw=4 et si
# -*- coding: UTF-8 -*-

DEBUG = 0 # 1 to enable some debug prints

PROPERTYLIST = {
"username":(_("Username"), str, _("Web solver username"), "", ""),
"email":(_("E-mail"), str, _("E-mail address"),  "", ""),
"scale_low":(_("Scale minimum"), float, _("Image scale lower bound"), "", 0),
"scale_max":(_("Scale maximum"), float, _("Image scale upper bound"), "", 179),
}


# This feature is under development, inherit from IPlateSolver only when
# developing the feature
baseclass = object
if DEBUG:
	baseclass = IPlateSolver

class AstrometryNetWebSolver(baseclass):
    def __init__(self, workDirectory=None):
        super(AstrometryNetWebSolver, self).__init__()
        self.propertyList = PROPERTYLIST
        self.__found = False
        self.__solution = None
        self.__timeout = 300
        self.__wd = workDirectory
        self.__callback = None
        self.__abort = False
    @property
    def hasSolution(self):
        return self.__found
    @property
    def solution(self):
        return self.__solution
    @property
    def timeout(self):
        return self.__timeout
    @timeout.setter
    def timeout(self, value):
        self.__timeout = int(value)

    def solve(self, imagePath, target=None, targetRadius=3, minFOV=None, maxFOV=None, callback = None):
        """Do plate solving for image, return True on success
        @param imagePath string, path to image to be solved
        @param target Coordinate(), optional guess at image center
        @param targetRadius float, target coordinate guess accuracy
        @param minFOV float, optional minimum field width in degrees
        @param maxFOV float, optional maximum field width in degrees
        @param callback function, optional function called periodically
        @return Solution() or None

        The callback function must be callable with a string argument and with explicit None.
        """
        self.__found = False
        del self.__solution
        self.__solution = None
        uname = self.getProperty("username")
        email = self.getProperty("email")

        if not os.path.exists(imagePath):
            if callback: 
                callback("File not found")
            else:
                raise IOError("File not found")
            return False
        else:
            imagename = os.path.abspath(imagePath)

        # handle submission form

        data = {}
        data['email'] = email
        data['uname'] = uname
        data['xysrc'] = 'img'
	data['UPLOAD_IDENTIFIER'] = ''.join(random.choice(string.hexdigits[:16]) for i in range(32))
        data['MAX_FILE_SIZE'] = '262144000'
        data['justjobid'] = ''
        data['skippreview'] = ''
        data['remember'] = 1
        data['submit'] = 'Submit'
        body, headers = self.__encodeMultipartData(data, {'imgfile': imagename})

        # Send request
        try:
            request = urllib2.Request("http://live.astrometry.net/index.php", body, headers)
            response = urllib2.urlopen(request)
            #print response.read()
        except urllib2.URLError:
            if callback: 
                callback("HTML error!")
            return False

        callback("Uploading...")

        content = response.read()
	print content[:5000]
        response.close()

        if not re.search("alpha-[0-9]+-[0-9]+", content):
            return False
        jobid = re.search("alpha-[0-9]+-[0-9]+", content).group(0)

        if self.__callback: self.__callback("Job ID: " + jobid)

        joburl = "http://live.astrometry.net/status.php?job=" + jobid
        #callback("Job Status Page: " + "http://live.astrometry.net/status.php?job=" + jobid)
        response = urllib2.urlopen(joburl)
        content = response.read()

        if callback: callback("Waiting for solve...")
        while "Running" in content.replace('\n', ''):
            response.close()
            time.sleep(5)
            response = urrlib2.urllopen(joburl)
            content = response.read()

        if "Failed" in content.replace('\n',''):
            if callback: callback("Solving failed!")
            self.__found = False
            del self.__solution
            self.__solution = None
            return False

        else:
            if callback: callback("Solve successful!")

        for line in content.split('\n'):
            if "(RA, Dec) center:" in line:
                [ra,dec] = map(float, re.findall('[0-9]+\.[0-9]+', line))
            if "Orientation:" in line:
                rotation = map(float, re.findall('[0-9]+\.[0-9]+', line))[0]
            if "Parity:" in line:
                if "Normal" in line:
                    parity = 0
                else: #if "Reversed" in line:
                    parity = 1
            if "Field size :" in line:
                fieldOfView = tuple(map(float, re.findall('[0-9]+\.[0-9]+', line)))
                if "arcminutes" in line:
                    fieldOfView = [x/60. for x in fieldOfView]
                elif "arcseconds" in line:
                    fieldOfView = [x/3600. for x in fieldOfView]


        center = Coordinate(ra, dec)
        self.__solution = Solution(center, rotation, parity, 
                fieldOfView[0], fieldOfView[1], wcsInfo=None)

        self.__found = True
        return self.__solution

    def __randomString(self, length):
        return ''.join(random.choice(string.ascii_letters) for ii in range(length+1))

    def __encodeMultipartData(self, data, files):
        boundary = self.__randomString(30)

        def getContentType(filename):
            return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

        def encodeField(fieldName):
            return ('--' + boundary,
                    'Content-Disposition: form-data; name="%s"' % fieldName,
                    '', str(data[fieldName]))

        def encodeFile(fieldName):
            filename = files[fieldName]
            return ('--' + boundary,
                    'Content-Disposition: form-data; name="%s"; filename="%s"' % (fieldName, filename),
                    'Content-Type: %s' % getContentType(filename),
                    '', open(filename, 'rb').read())

        lines = []
        for name in data:
            lines.extend(encodeField(name))
        for name in files:
            lines.extend(encodeFile(name))
        lines.extend(('--%s--' % boundary, ''))
        body = '\r\n'.join(unicode(lines))
        body = binascii.b2a_base64(unicode(body))

        headers = {'Content-Type': 'multipart/form-data; boundary=' + boundary,
                'Content-Length': str(len(body)),
                'Content-Transfer-Encoding': 'base64',
                'User-Agent': 'Opera/9.80 (Windows NT 5.1; U; en) Presto/2.8.131 Version/11.11'}
        return body, headers

