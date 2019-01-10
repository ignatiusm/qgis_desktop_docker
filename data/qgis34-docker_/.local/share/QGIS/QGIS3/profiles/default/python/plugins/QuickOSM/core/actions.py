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

from QuickOSM.core.utilities.tools import tr, resources_path
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtGui import QDesktopServices
from qgis.core import Qgis, QgsAction
from qgis.utils import iface, plugins

ACTIONS_PATH = 'from QuickOSM.core.actions import Actions;'
ACTIONS_VISIBILITY = ['Canvas', 'Feature', 'Field']


def add_actions(layer, keys):
    """Add actions on layer.

    :param layer: The layer.
    :type layer: QgsVectorLayer

    :param keys: The list of keys in the layer.
    :type keys: list
    """
    actions = layer.actions()

    title = tr('OpenStreetMap Browser')
    osm_browser = QgsAction(
        QgsAction.OpenUrl,
        title,
        'http://www.openstreetmap.org/browse/[% "osm_type" %]/[% "osm_id" %]',
        '',
        False,
        title,
        ACTIONS_VISIBILITY,
        ''
    )
    actions.addAction(osm_browser)

    title = 'Mapillary'
    mapillary = QgsAction(
        QgsAction.GenericPython,
        title,
        ACTIONS_PATH + 'Actions.run("mapillary","[% "mapillary" %]")',
        resources_path('mapillary_logo.svg'),
        False,
        title,
        ACTIONS_VISIBILITY,
        ''
    )
    actions.addAction(mapillary)

    title = 'JOSM'
    josm = QgsAction(
        QgsAction.GenericPython,
        title,
        ACTIONS_PATH + 'Actions.run("josm","[% "full_id" %]")',
        resources_path('josm_icon.svg'),
        False,
        title,
        ACTIONS_VISIBILITY,
        ''
    )
    actions.addAction(josm)

    title = tr('User default editor')
    default_editor = QgsAction(
        QgsAction.OpenUrl,
        title,
        'http://www.openstreetmap.org/edit?[% "osm_type" %]=[% "osm_id" %]',
        '',
        False,
        title,
        ACTIONS_VISIBILITY,
        ''
    )
    actions.addAction(default_editor)

    for link in ['url', 'website', 'wikipedia', 'wikidata', 'ref:UAI']:
        if link in keys:

            # Add an image to the action if available
            image = ''
            if link == 'wikipedia':
                image = resources_path('wikipedia.png')
            elif link == 'wikidata':
                image = resources_path('wikidata.png')
            elif link in ['url', 'website']:
                image = resources_path('external_link.png')

            link = link.replace(":", "_")
            generic = QgsAction(
                QgsAction.GenericPython,
                link,
                (ACTIONS_PATH +
                    'Actions.run("' + link + '","[% "' + link + '" %]")'),
                image,
                False,
                link,
                ACTIONS_VISIBILITY,
                ''
            )
            actions.addAction(generic)

    if 'network' in keys and 'ref' in keys:
        sketch_line = QgsAction(
            QgsAction.GenericPython,
            tr('Sketchline'),
            (ACTIONS_PATH +
             'Actions.run_sketch_line("[% "network" %]","[% "ref" %]")'),
            '',
            False,
            '',
            ACTIONS_VISIBILITY,
            ''
        )
        actions.addAction(sketch_line)


class Actions(object):
    """
    Manage actions available on layers
    """

    @staticmethod
    def run(field, value):
        """
        Run an action with only one value as parameter

        @param field:Type of the action
        @type field:str
        @param value:Value of the field for one entity
        @type value:str
        """

        if value == '':
            iface.messageBar().pushMessage(
                tr('Sorry, this field \'{}\' is empty for this entity.'
                   .format(field)),
                level=Qgis.Warning, duration=7)
        else:

            if field in ['url', 'website', 'wikipedia', 'wikidata']:
                var = QDesktopServices()
                url = None

                if field == 'url' or field == 'website':
                    url = value

                if field == 'ref_UAI':
                    url = "http://www.education.gouv.fr/pid24302/annuaire-" \
                          "resultat-recherche.html?lycee_name=" + value

                if field == 'wikipedia':
                    url = "http://en.wikipedia.org/wiki/" + value

                if field == 'wikidata':
                    url = "http://www.wikidata.org/wiki/" + value

                var.openUrl(QUrl(url))

            elif field == 'mapillary':
                if 'go2mapillary' in plugins:
                    plugins['go2mapillary'].dockwidget.show()
                    plugins["go2mapillary"].mainAction.setChecked(False)
                    plugins['go2mapillary'].viewer.openLocation(value)
                else:
                    var = QDesktopServices()
                    url = 'https://www.mapillary.com/map/im/' + value
                    var.openUrl(QUrl(url))

            elif field == 'josm':
                import urllib.request, urllib.error, urllib.parse
                try:
                    url = 'http://localhost:8111/load_object?objects=' + value
                    urllib.request.urlopen(url).read()
                except urllib.error.URLError:
                    iface.messageBar().pushMessage(
                        tr('The JOSM remote seems to be disabled.'),
                        level=Qgis.Critical,
                        duration=7)

            # NOT USED
            elif field == 'rawedit':
                # url = QUrl("http://rawedit.openstreetmap.fr/edit/" + value)
                # web_browser = QWebView(None)
                # web_browser.load(url)
                # web_browser.show()
                pass

    @staticmethod
    def run_sketch_line(network, ref):
        """
        Run an action with two values for sketchline

        @param network:network of the bus
        @type network:str
        @param ref:ref of the bus
        @type ref:str
        """
        if network == '' or ref == '':
            iface.messageBar().pushMessage(
                tr('Sorry, this field is empty for this entity.'),
                level=Qgis.Warning,
                duration=7)
        else:
            var = QDesktopServices()
            url = 'http://www.overpass-api.de/api/sketch-line?' \
                  'network=' + network + '&ref=' + ref
            var.openUrl(QUrl(url))
