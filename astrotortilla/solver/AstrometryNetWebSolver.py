import logging
import time
import gettext
from PIL import Image

import pyfits

from win32com.client import Dispatch
from ..IPlateSolver import IPlateSolver, Solution
from ..units import Coordinate
from astrotortilla.solver import http

logger = logging.getLogger("astrotortilla.AstrometryNetWebSolver")

t = gettext.translation('astrotortilla', 'locale', fallback=True)
_ = t.gettext

PROPERTYLIST = {
    "apikey": (_("API Key"), str, _("API Key"), "", ""),
    "year_epoch": (_("JNow or J2000"), str, _("JNOW or J2000"), "", "J2000")
}


def image_size(filepath):
    if filepath.endswith('fit') or filepath.endswith('fits'):
        v, h = pyfits.open(filepath)[0].data.shape
    else:
        h, v = Image.open(filepath).size
    return h, v


class AstrometryNetWebSolver(IPlateSolver):
    def __init__(self, workDirectory=None):
        super(AstrometryNetWebSolver, self).__init__()
        self.propertyList = PROPERTYLIST
        self.__found = False
        self.__solution = None
        self.__timeout = 300
        self.__wd = workDirectory
        self.__callback = None
        self.__abort = False
        self.__session = None
        try:
            self.__transform = Dispatch("ASCOM.Astrometry.Transform.Transform")
        except:
            logger.error("Failed to initialize ASCOM astrometric transformer, no epoch conversion available")
            self.__transform = None

    @classmethod
    def getName(cls):
        return _("Web astrometry.net")

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

    def solve(self, imagePath, target=None, targetRadius=None, minFOV=None, maxFOV=None, callback=None):
        """
        Do plate solving for image, return True on success
        @param imagePath string, path to image to be solved
        @param target Coordinate(), optional guess at image center
        @param targetRadius float, target coordinate guess accuracy
        @param minFOV float, optional minimum field width in degrees
        @param maxFOV float, optional maximum field width in degrees
        @param callback function, optional function called periodically
        @return Solution() or None

        The callback function must be callable with a string argument and with explicit None.
        """
        logging.info('Try to solve: %s' % imagePath)
        self.__callback = callback
        self.__found = False
        self.__abort = False
        self.__solution = None
        self.__apikey = self.getProperty("apikey")

        subid = None
        for i in range(3):
            subid = self._upload_file(imagePath)
            if subid or self.__abort:
                break
            self._notify('Retry upload')
            time.sleep(1)
        if not subid or self.__abort:
            return None

        result = None
        for i in range(30):
            code, result = self._solve_result(subid)
            if code == 0 or code == 2 or self.__abort:
                break
            time.sleep(10)
        if not result or self.__abort:
            return None

        h, v = image_size(imagePath)
        hFOV = float(h) * result['pixscale'] / 3600.
        vFOV = float(v) * result['pixscale'] / 3600.
        center = Coordinate(result['ra'], result['dec'])
        if self.__transform and self.getProperty("year_epoch").lower() == "jnow":
            self.__transform.SetJ2000(center.RAhour, center.dec)
            center = Coordinate(self.__transform.RAApparent / 24. * 360, self.__transform.DECApparent, epoch="JNOW")
        self.__solution = Solution(center, result['orientation'], result['parity'], hFOV, vFOV)

        self._notify('Solved!')
        self.__found = True
        self.__abort = False
        return self.__solution

    def _notify(self, msg):
        if self.__callback:
            self.__callback(msg)

    def _login(self):
        resp_data = http.post_data('login', {'apikey': self.__apikey})
        if resp_data and resp_data.get('status') == 'success':
            self.__session = resp_data.get('session')
        if not self.__session:
            logger.error('login failed')
            self._notify('Login Failed')
        else:
            logger.info('login succeed')
            self._notify('Login succeed')

    def _upload_url(self, url):
        if not self.__session:
            self._login()
        req_data = {'session': self.__session,
                    'url': url,
                    'allow_commercial_use': 'd',
                    'allow_modifications': 'd',
                    'publicly_visible': 'n'}
        resp_data = http.post_data('url_upload', req_data)
        logger.info('upload result: %s' % resp_data)
        if resp_data and resp_data.get('status') == 'success':
            subid = resp_data.get('subid')
            self._notify('Submission ID: %s' % subid)
            return subid
        else:
            self.__session = None
            self._notify('Submission failed')
            return None

    def _upload_file(self, filepath):
        if not self.__session:
            self._login()
        req_data = {'session': self.__session,
                    'allow_commercial_use': 'd',
                    'allow_modifications': 'd',
                    'publicly_visible': 'n'}
        self._notify("Uploading...")
        resp_data = http.post_file('upload', filepath, req_data)
        logger.info('upload result: %s' % resp_data)
        if resp_data and resp_data.get('status') == 'success':
            subid = resp_data.get('subid')
            self._notify('Submission ID: %s' % subid)
            return subid
        else:
            self.__session = None
            self._notify('Submission failed')
            return None

    def _solve_result(self, subid):
        resp_data = http.get('submissions/%s' % subid)
        logger.info('submission %s status: %s' % (subid, resp_data))
        jobs = resp_data.get('jobs', [])
        if jobs and jobs[0]:
            jobid = jobs[0]
            self._notify('Job ID: %s' % jobid)
            resp_data = http.get('jobs/%s/info' % jobid)
            logger.info('job %s result: %s' % (jobid, resp_data))
            if resp_data and resp_data.get('status') == 'success':
                return 0, resp_data.get('calibration')
            elif resp_data and resp_data.get('status') == 'failure':
                return 2, None
            else:
                return 1, None
        else:
            self._notify('Waiting for the job')
            return 1, None

    def reset(self):
        """Reset solver state"""
        self.__found = False
        self.__solution = None
        self.__abort = False

    def abort(self):
        """Abort current solver"""
        self.__abort = True
