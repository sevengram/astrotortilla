# -*- coding: UTF-8 -*-
"""
IPlateSolver - Plate Solver interface
"""

from units import Coordinate
from Configurations import Configurable


class Solution(object):
    """Plate solver solution class"""

    def __init__(self, center, rotation, parity, hFOV, vFOV, wcsInfo=None):
        """Create a Solution.
        @param center Coordinate(RA,dec) pointing to center of solution
        @param rotation float, image rotation in degrees
        @param parity 0 or 1, parity of image coordinates to real RA/dec coordinates
        @param hFOV float, horizontal field-of-view in degrees
        @param vFOV float, vertical field-of-view in degrees
        @param wcsInfo dict, optional WCS information dictionary of key:value pairs
        """
        if not isinstance(center, Coordinate):
            raise TypeError("Invalid arguments, expected Coordinate")
        self.__center = center
        self.__rotation = float(rotation)
        self.__parity = parity
        self.__vFOV = float(vFOV)
        self.__hFOV = float(hFOV)
        if wcsInfo:
            self.__wcsInfo = wcsInfo
        else:
            self.__wcsInfo = {}

    def __repr__(self):
        return "Solution(%s, %f, %d, %f, %f)" % (
        self.__center, self.__rotation, self.__parity, self.__hFOV, self.__vFOV)

    @classmethod
    def getName(cls):
        raise NotImplementedError("IPlateSolver.getName not implemented")

    @property
    def center(self):
        """Coordinate(RA,dec) -instance at the image center"""
        return self.__center

    @property
    def rotation(self):
        """Image rotation in degrees"""
        return self.__rotation

    @property
    def parity(self):
        """Image parity: 0=right handed coordinates, 1=left handed coordinates"""
        return self.__parity

    @property
    def fieldOfView(self):
        """2-tuple of horizontal FOV and vertical FOV in degrees"""
        return self.__hFOV, self.__vFOV

    @property
    def wcsInfo(self):
        """Dict of WCS information {key:value} if available"""
        return self.__wcsInfo


class IPlateSolver(Configurable):
    """
    Plate solver interface
    Mandatory properties to implement:
        bool hasSolution ro
        Solution solution ro
    Functions:
        bool solve(imagePath, target=None, minFOV=None, maxFOV=None, callback=None)
    """

    @property
    def hasSolution(self):
        """bool - is a solution available"""
        return False

    @property
    def solution(self):
        """Get current solution or None if not available"""
        return None

    @property
    def timeout(self):
        """Current timeout for finding a solution, 0=not supported"""
        return 0

    @timeout.setter
    def timeout(self, value):
        """Set timeout for finding a solution"""
        pass

    def solve(self, imagePath, target=None, targetRadius=3, minFOV=None, maxFOV=None, callback=None):
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
        return None

    def reset(self):
        """Reset current state"""
        pass

    def abort(self):
        """Abort on-going solver is possible"""
        pass
