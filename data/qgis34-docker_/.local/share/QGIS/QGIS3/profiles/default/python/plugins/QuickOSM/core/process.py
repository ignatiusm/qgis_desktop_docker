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
import logging
import time
from os.path import dirname, abspath, join, isfile

from QuickOSM.core.actions import add_actions
from QuickOSM.core.api.connexion_oapi import ConnexionOAPI
from QuickOSM.core.exceptions import FileOutPutException
from QuickOSM.core.parser.osm_parser import OsmParser
from QuickOSM.core.query_factory import QueryFactory
from QuickOSM.core.query_preparation import QueryPreparation
from QuickOSM.core.utilities.operating_system import get_default_encoding
from QuickOSM.core.utilities.tools import get_setting
from QuickOSM.core.utilities.tools import tr
from QuickOSM.definitions.osm import QueryType
from QuickOSM.definitions.overpass import OVERPASS_SERVERS
from qgis.PyQt.QtWidgets import QApplication
from qgis.core import (
    QgsVectorLayer, QgsVectorFileWriter, QgsProject, QgsWkbTypes)

LOGGER = logging.getLogger('QuickOSM')


def open_file(
        dialog=None,
        osm_file=None,
        output_geom_types=None,
        white_list_column=None,
        layer_name="OsmFile",
        config_outputs=None,
        output_dir=None,
        prefix_file=None):
    """
    Open an osm file.

    Memory layer if no output directory is set, or Geojson in the output directory.
    """
    outputs = {}
    if output_dir:
        for layer in ['points', 'lines', 'multilinestrings', 'multipolygons']:
            if not prefix_file:
                prefix_file = layer_name

            outputs[layer] = join(
                output_dir, prefix_file + "_" + layer + ".geojson")

            if isfile(outputs[layer]):
                raise FileOutPutException(suffix='(' + outputs[layer] + ')')

    # Parsing the file
    osm_parser = OsmParser(
        osm_file=osm_file,
        layers=output_geom_types,
        white_list_column=white_list_column)

    osm_parser.signalText.connect(dialog.set_progress_text)
    osm_parser.signalPercentage.connect(dialog.set_progress_percentage)

    start_time = time.time()
    layers = osm_parser.parse()
    elapsed_time = time.time() - start_time
    parser_time = time.strftime("%Hh %Mm %Ss", time.gmtime(elapsed_time))
    LOGGER.info('The OSM parser took: {}'.format(parser_time))

    # Finishing the process with geojson or memory layer
    num_layers = 0

    for i, (layer, item) in enumerate(layers.items()):
        dialog.set_progress_percentage(i / len(layers) * 100)
        QApplication.processEvents()
        if item['featureCount'] and layer in output_geom_types:

            final_layer_name = layer_name
            # If configOutputs is not None (from My Queries)
            if config_outputs:
                if config_outputs[layer]['namelayer']:
                    final_layer_name = config_outputs[layer]['namelayer']

            if output_dir:
                dialog.set_progress_text(tr('From memory to GeoJSON: ' + layer))
                # Transforming the vector file
                osm_geometries = {
                    'points': QgsWkbTypes.Point,
                    'lines': QgsWkbTypes.LineString,
                    'multilinestrings': QgsWkbTypes.MultiLineString,
                    'multipolygons': QgsWkbTypes.MultiPolygon}
                memory_layer = item['vector_layer']

                encoding = get_default_encoding()
                writer = QgsVectorFileWriter(
                    outputs[layer],
                    encoding,
                    memory_layer.fields(),
                    osm_geometries[layer],
                    memory_layer.crs(),
                    "GeoJSON")

                for f in memory_layer.getFeatures():
                    writer.addFeature(f)

                del writer

                # Loading the final vector file
                new_layer = QgsVectorLayer(outputs[layer], final_layer_name, "ogr")
            else:
                new_layer = item['vector_layer']
                new_layer.setName(final_layer_name)

            # Try to set styling if defined
            if config_outputs and config_outputs[layer]['style']:
                new_layer.loadNamedStyle(config_outputs[layer]['style'])
            else:
                # Loading default styles
                if layer == "multilinestrings" or layer == "lines":
                    if "colour" in item['tags']:
                        new_layer.loadNamedStyle(
                            join(dirname(dirname(abspath(__file__))),
                                 "styles",
                                 layer + "_colour.qml"))

            # Add action about OpenStreetMap
            add_actions(new_layer, item['tags'])

            QgsProject.instance().addMapLayer(new_layer)
            num_layers += 1

    return num_layers


def process_query(
        dialog=None,
        query=None,
        nominatim=None,
        bbox=None,
        output_dir=None,
        prefix_file=None,
        output_geometry_types=None,
        layer_name="OsmQuery",
        white_list_values=None,
        config_outputs=None):
    """execute a query and send the result file to open_file."""

    # Prepare outputs
    dialog.set_progress_text(tr('Prepare outputs'))

    # Getting the default overpass api and running the query
    server = get_setting('defaultOAPI', OVERPASS_SERVERS[0]) + 'interpreter'
    dialog.set_progress_text(
        tr('Downloading data from Overpass {}').format(server))
    # Replace Nominatim or BBOX
    query = QueryPreparation(query, bbox, nominatim, server)
    QApplication.processEvents()
    query.prepare_query()
    url = query.prepare_url()
    connexion_overpass_api = ConnexionOAPI(url)
    LOGGER.debug('Encoded URL: {}'.format(url))
    osm_file = connexion_overpass_api.run()

    return open_file(
        dialog=dialog,
        osm_file=osm_file,
        output_geom_types=output_geometry_types,
        white_list_column=white_list_values,
        layer_name=layer_name,
        output_dir=output_dir,
        prefix_file=prefix_file,
        config_outputs=config_outputs)


def process_quick_query(
        dialog=None,
        key=None,
        value=None,
        bbox=None,
        nominatim=None,
        is_around=None,
        distance=None,
        osm_objects=None,
        timeout=25,
        output_directory=None,
        prefix_file=None,
        output_geometry_types=None):
    """
    Generate a query and send it to process_query.
    """
    # TODO
    # Move this logic UP
    # Copy/paste in quick_query_dialog.py
    distance_string = None
    if is_around and nominatim:
        query_type = QueryType.AroundArea
        distance_string = str(distance)
    elif not is_around and nominatim:
        query_type = QueryType.InArea
    elif bbox:
        query_type = QueryType.BBox
    else:
        query_type = QueryType.NotSpatial
    # End todo

    # Building the query
    query_factory = QueryFactory(
        query_type=query_type,
        key=key,
        value=value,
        area=nominatim,
        around_distance=distance,
        osm_objects=osm_objects,
        timeout=timeout
    )
    query = query_factory.make()

    # Generate layer name as following (if defined)
    if not key:
        key = tr('allKeys')
    expected_name = [key, value, nominatim, distance_string]
    layer_name = '_'.join([f for f in expected_name if f])
    LOGGER.info('Query: {}'.format(layer_name))

    # Call process_query with the new query
    return process_query(
        dialog=dialog,
        query=query,
        nominatim=nominatim,
        bbox=bbox,
        output_dir=output_directory,
        prefix_file=prefix_file,
        output_geometry_types=output_geometry_types,
        layer_name=layer_name)
