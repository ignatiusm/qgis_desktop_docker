"""
/***************************************************************************
        QuickOSM QGIS plugin
        OSM Overpass API frontend
                             -------------------
        begin                : 2017-11-11
        copyright            : (C) 2017 by Etienne Trimaille
        email                : etienne dot trimaille at gmail dot com
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

# import codecs
# import re
# import processing
from processing.algs.qgis.QgisAlgorithm import QgisAlgorithm
from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterString,
    QgsProcessingOutputFile,
)


class DownloadOverpassUrl(QgisAlgorithm):

    URL = 'URL'
    OUTPUT = 'OUTPUT'

    def __init__(self):
        super(DownloadOverpassUrl, self).__init__()
        self.feedback = None

    def group(self):
        return self.tr('Advanced')

    @staticmethod
    def groupId():
        return 'advanced'

    @staticmethod
    def name():
        return 'downloadoverpassquery'

    def displayName(self):
        return self.tr('Download from Overpass')

    def flags(self):
        return super().flags()  # | QgsProcessingAlgorithm.FlagHideFromToolbox

    def shortHelpString(self):
        return self.tr('Like the native QGIS File Downloader algorithm, this algorithm will '
                  'perform a OSM integrity check at the end of the download.')

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterString(
                self.URL, self.tr('URL, with the query encoded')))

        self.addOutput(
            QgsProcessingOutputFile(
                self.OUTPUT, self.tr('Output')))

    def processAlgorithm(self, parameters, context, feedback):
        self.feedback = feedback
        url = self.parameterAsString(parameters, self.URL, context)
        output = self.parameterAsFileOutput(parameters, self.OUTPUT, context)

        # processing.run("native:filedownloader", {
        #     'URL': url,
        #     'OUTPUT': output,
        # }, context=context, feedback=feedback)

        # file_obj = codecs.open(self.result_path, 'r', 'utf-8')
        # file_obj.seek(0, 2)
        # fsize = file_obj.tell()
        # file_obj.seek(max(fsize - 1024, 0), 0)
        # lines = file_obj.readlines()
        # file_obj.close()
        #
        # lines = lines[-10:]  # Get last 10 lines
        # timeout = '<remark> runtime error: Query timed out in "[a-z]+" ' \
        #           'at line [\d]+ after ([\d]+) seconds. </remark>'
        # if re.search(timeout, ''.join(lines)):
        #     raise QgsProcessingException(tr('Overpass API timeout'))

        outputs = {
            self.OUTPUT: output,
        }
        return outputs
