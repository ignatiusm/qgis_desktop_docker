# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QuickOSM
 A QGIS plugin
 OSM Overpass API frontend
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

import json

from QuickOSM.core.exceptions import \
    NominatimAreaException, NetWorkErrorException
from qgis.PyQt.QtCore import QUrl, QUrlQuery, QEventLoop
from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkReply
from qgis.core import QgsNetworkAccessManager


class Nominatim(object):
    """Manage connexion to Nominatim."""

    def __init__(self,
                 url="https://nominatim.openstreetmap.org/search?format=json"):
        """
        Constructor
        @param url:URL of Nominatim
        @type url:str
        """

        self.__url = url
        self.network = QgsNetworkAccessManager.instance()
        self.data = None
        self.network_reply = None
        self.loop = None

    def query(self, query):
        """
        Perform a nominatim query

        @param query: Query to execute
        @type query: str

        @raise NetWorkErrorException

        @return: the result of the query
        @rtype: str
        """

        url_query = QUrl(self.__url)

        # query = QUrl.toPercentEncoding(query)
        query_string = QUrlQuery()
        query_string.addQueryItem('q', query)
        query_string.addQueryItem('format', 'json')
        query_string.addQueryItem('info', 'QgisQuickOSMPlugin')
        url_query.setQuery(query_string)

        request = QNetworkRequest(url_query)
        # request.setRawHeader("User-Agent", "QuickOSM")
        self.network_reply = self.network.get(request)
        self.loop = QEventLoop()
        self.network.finished.connect(self._end_of_request)
        self.loop.exec_()

        if self.network_reply.error() == QNetworkReply.NoError:
            return json.loads(self.data)
        else:
            raise NetWorkErrorException(suffix="Nominatim API")

    def _end_of_request(self):
        self.data = self.network_reply.readAll().data().decode('utf-8')
        self.loop.quit()

    def get_first_polygon_from_query(self, query):
        """
        Get first OSM_ID of a Nominatim area

        @param query: Query to execute
        @type query: str

        @raise NominatimAreaException:

        @return: First relation's osm_id
        @rtype: str
        """
        data = self.query(query)
        for result in data:
            if result['osm_type'] == "relation":
                return result['osm_id']

        # If no result has been return
        raise NominatimAreaException

    def get_first_point_from_query(self, query):
        """
        Get first longitude, latitude of a Nominatim point

        @param query: Query to execute
        @type query: str

        @raise NominatimAreaException:

        @return: First relation's osm_id
        @rtype: str
        """
        data = self.query(query)
        for result in data:
            if result['osm_type'] == "node":
                return result['lon'], result['lat']

        # If no result has been return
        raise NominatimAreaException
