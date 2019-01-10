# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QuickOSM
                                 A QGIS plugin
 OSM's Overpass API frontend
                             -------------------
        begin                : 2014-06-11
        copyright            : (C) 2014 by 3Liz
        email                : info at 3liz dot com
        contributor          : Etienne Trimaille
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from QuickOSM.core.utilities.tools import tr
# from processing.core.GeoAlgorithmExecutionException import \
#     GeoAlgorithmExecutionException
from qgis.core import Qgis


class QuickOsmException(BaseException):
    def __init__(self, msg=None):
        if not msg:
            msg = tr('QuickOSM')
        self.msg = msg
        BaseException.__init__(self, msg)
        self.level = Qgis.Critical
        self.duration = 7


class GeoAlgorithmException(QuickOsmException):
    def __init__(self, msg=None):
        if not msg:
            msg = tr('GeoAlgorithm exception')
        QuickOsmException.__init__(self, msg)


'''
Overpass or network
'''


class OverpassBadRequestException(QuickOsmException):
    def __init__(self, msg=None):
        if not msg:
            msg = tr('Bad request OverpassAPI')
        QuickOsmException.__init__(self, msg)


class OverpassTimeoutException(QuickOsmException):
    def __init__(self, msg=None):
        if not msg:
            msg = tr('OverpassAPI timeout')
        QuickOsmException.__init__(self, msg)


class NetWorkErrorException(QuickOsmException):
    def __init__(self, msg=None, suffix=None):
        if not msg:
            msg = tr('Network error')
        if suffix:
            msg = msg + ' with ' + suffix
        QuickOsmException.__init__(self, msg)

'''
QueryFactory
'''


class QueryFactoryException(QuickOsmException):
    def __init__(self, msg=None, suffix=None):
        if not msg:
            msg = tr('Error while building the query')
        if suffix:
            msg = msg + " : " + suffix
        QuickOsmException.__init__(self, msg)


class QueryNotSupported(QuickOsmException):
    def __init__(self, key):
        msg = tr('The query is not supported by the plugin because of '
                 ': %s' % key)
        QuickOsmException.__init__(self, msg)

'''
Nominatim
'''


class NominatimAreaException(QuickOsmException):
    def __init__(self, msg=None):
        if not msg:
            msg = tr('No nominatim area')
        QuickOsmException.__init__(self, msg)

'''
Ogr2Ogr
'''


class Ogr2OgrException(QuickOsmException):
    def __init__(self, msg=None):
        if not msg:
            msg = tr('Error with ogr2ogr')
        QuickOsmException.__init__(self, msg)


class NoLayerException(QuickOsmException):
    def __init__(self, msg=None, suffix=None):
        if not msg:
            msg = tr('The layer is missing :')
        if suffix:
            msg = msg + " " + suffix
        QuickOsmException.__init__(self, msg)


'''
File and directory
'''


class FileDoesntExistException(QuickOsmException):
    def __init__(self, msg=None, suffix=None):
        if not msg:
            msg = tr('The file does not exist')
        if suffix:
            msg = msg + " " + suffix
        QuickOsmException.__init__(self, msg)


class DirectoryOutPutException(QuickOsmException):
    def __init__(self, msg=None):
        if not msg:
            msg = tr('The output directory does not exist.')
        QuickOsmException.__init__(self, msg)


class FileOutPutException(QuickOsmException):
    def __init__(self, msg=None, suffix=None):
        if not msg:
            msg = tr('The output file already exist, set a prefix')
        if suffix:
            msg = msg + " " + suffix
        QuickOsmException.__init__(self, msg)


class OutPutFormatException(QuickOsmException):
    def __init__(self, msg=None):
        if not msg:
            msg = tr('Output not available')
        QuickOsmException.__init__(self, msg)


class QueryAlreadyExistsException(QuickOsmException):
    def __init__(self, msg=None):
        if not msg:
            msg = tr('This query already exists')
        QuickOsmException.__init__(self, msg)

'''
Forms
'''


class MissingParameterException(QuickOsmException):
    def __init__(self, msg=None, suffix=None):
        if not msg:
            msg = tr('A parameter is missing :')
        if suffix:
            msg = msg + " " + suffix
        QuickOsmException.__init__(self, msg)


class OsmObjectsException(QuickOsmException):
    def __init__(self, msg=None):
        if not msg:
            msg = tr('No osm objects selected')
        QuickOsmException.__init__(self, msg)


class OutPutGeomTypesException(QuickOsmException):
    def __init__(self, msg=None):
        if not msg:
            msg = tr('No outputs selected')
        QuickOsmException.__init__(self, msg)
