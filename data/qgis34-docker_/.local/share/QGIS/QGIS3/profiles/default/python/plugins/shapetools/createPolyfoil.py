import os
import math
from geographiclib.geodesic import Geodesic

from qgis.core import (QgsVectorLayer,
    QgsPointXY, QgsFeature, QgsGeometry, 
    QgsProject, QgsWkbTypes, QgsCoordinateTransform)
    
from qgis.core import (QgsProcessing,
    QgsFeatureSink,
    QgsProcessingAlgorithm,
    QgsProcessingParameterNumber,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsProcessingParameterFeatureSink)

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QUrl

from .settings import epsg4326, geod
from .utils import tr, conversionToMeters, DISTANCE_LABELS

SHAPE_TYPE=[tr("Polygon"),tr("Line")]

class CreatePolyfoilAlgorithm(QgsProcessingAlgorithm):
    """CreatePolyfoilAlgorithm
    Algorithm to create a hypocycloid shape.
    """

    PrmInputLayer = 'InputLayer'
    PrmOutputLayer = 'OutputLayer'
    PrmShapeType = 'ShapeType'
    PrmLobesField = 'LobesField'
    PrmStartingAngleField = 'StartingAngleField'
    PrmRadiusField = 'RadiusField'
    PrmLobes = 'Lobes'
    PrmRadius = 'Radius'
    PrmStartingAngle = 'StartingAngle'
    PrmUnitsOfMeasure = 'UnitsOfMeasure'
    PrmDrawingSegments = 'DrawingSegments'

    def initAlgorithm(self, config):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.PrmInputLayer,
                tr('Input point layer'),
                [QgsProcessing.TypeVectorPoint])
        )
        self.addParameter(
            QgsProcessingParameterEnum(
                self.PrmShapeType,
                tr('Shape type'),
                options=SHAPE_TYPE,
                defaultValue=0,
                optional=False)
        )
        self.addParameter(
            QgsProcessingParameterField(
                self.PrmLobesField,
                tr('Number of lobes field'),
                parentLayerParameterName=self.PrmInputLayer,
                type=QgsProcessingParameterField.Any,
                optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                self.PrmStartingAngleField,
                tr('Starting angle field'),
                parentLayerParameterName=self.PrmInputLayer,
                type=QgsProcessingParameterField.Any,
                optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                self.PrmRadiusField,
                tr('Radius field'),
                parentLayerParameterName=self.PrmInputLayer,
                type=QgsProcessingParameterField.Any,
                optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.PrmLobes,
                tr('Number of lobes'),
                QgsProcessingParameterNumber.Integer,
                defaultValue=5,
                minValue=3,
                optional=True)
            )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.PrmStartingAngle,
                tr('Starting angle'),
                QgsProcessingParameterNumber.Double,
                defaultValue=0,
                optional=True)
            )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.PrmRadius,
                tr('Radius'),
                QgsProcessingParameterNumber.Double,
                defaultValue=40.0,
                minValue=0,
                optional=True)
            )
        self.addParameter(
            QgsProcessingParameterEnum(
                self.PrmUnitsOfMeasure,
                tr('Radius units of measure'),
                options=DISTANCE_LABELS,
                defaultValue=0,
                optional=False)
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.PrmDrawingSegments,
                tr('Number of drawing segments'),
                QgsProcessingParameterNumber.Integer,
                defaultValue=720,
                minValue=4,
                optional=True)
            )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.PrmOutputLayer,
                tr('Output layer'))
            )
    
    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.PrmInputLayer, context)
        shapetype = self.parameterAsInt(parameters, self.PrmShapeType, context)
        lobescol = self.parameterAsString(parameters, self.PrmLobesField, context)
        startanglecol = self.parameterAsString(parameters, self.PrmStartingAngleField, context)
        radiuscol = self.parameterAsString(parameters, self.PrmRadiusField, context)
        radius = self.parameterAsDouble(parameters, self.PrmRadius, context)
        startAngle = self.parameterAsDouble(parameters, self.PrmStartingAngle, context)
        lobes = self.parameterAsInt(parameters, self.PrmLobes, context)
        segments = self.parameterAsInt(parameters, self.PrmDrawingSegments, context)
        units = self.parameterAsInt(parameters, self.PrmUnitsOfMeasure, context)
        
        measureFactor = conversionToMeters(units)
        radius *= measureFactor
        r = radius / lobes

        srcCRS = source.sourceCrs()
        if shapetype == 0:
            (sink, dest_id) = self.parameterAsSink(parameters,
                self.PrmOutputLayer, context, source.fields(),
                QgsWkbTypes.Polygon, srcCRS)
        else:
            (sink, dest_id) = self.parameterAsSink(parameters,
                self.PrmOutputLayer, context, source.fields(),
                QgsWkbTypes.LineString, srcCRS)
                
        if srcCRS != epsg4326:
            geomTo4326 = QgsCoordinateTransform(srcCRS, epsg4326, QgsProject.instance())
            toSinkCrs = QgsCoordinateTransform(epsg4326, srcCRS, QgsProject.instance())
        
        featureCount = source.featureCount()
        total = 100.0 / featureCount if featureCount else 0
        
        step = 360.0 / segments
        numbad = 0
        iterator = source.getFeatures()
        for index, feature in enumerate(iterator):
            if feedback.isCanceled():
                break
            try:
                if startanglecol:
                    sangle = float(feature[startanglecol])
                else:
                    sangle = startAngle
                if lobescol:
                    lobes2 = int(feature[lobescol])
                else:
                    lobes2 = lobes
                if radiuscol:
                    radius2 = float(feature[radiuscol]) * measureFactor
                else:
                    radius2 = radius
                r = radius2 / lobes2
            except:
                numbad += 1
                continue
            pts = []
            pt = feature.geometry().asPoint()
            # make sure the coordinates are in EPSG:4326
            if srcCRS != epsg4326:
                pt = geomTo4326.transform(pt.x(), pt.y())
            angle = 0.0
            while angle <= 360.0:
                a = math.radians(angle-sangle)
                x = r * (lobes2 - 1.0)*math.cos(a) + r * math.cos((lobes2 - 1.0) * a)
                y = r * (lobes2 - 1.0)*math.sin(a) - r * math.sin((lobes2 - 1.0) * a)
                dist = math.sqrt(x*x + y*y)
                g = geod.Direct(pt.y(), pt.x(), angle, dist, Geodesic.LATITUDE | Geodesic.LONGITUDE)
                pts.append(QgsPointXY(g['lon2'], g['lat2']))
                angle += step
                
            # If the Output crs is not 4326 transform the points to the proper crs
            if srcCRS != epsg4326:
                for x, ptout in enumerate(pts):
                    pts[x] = toSinkCrs.transform(ptout)
                    
            f = QgsFeature()
            if shapetype == 0:
                f.setGeometry(QgsGeometry.fromPolygonXY([pts]))
            else:
                f.setGeometry(QgsGeometry.fromPolylineXY(pts))
            f.setAttributes(feature.attributes())
            sink.addFeature(f)
            
            if index % 100 == 0:
                feedback.setProgress(int(index * total))
            
        return {self.PrmOutputLayer: dest_id}
        
    def name(self):
        return 'createpolyfoil'

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(__file__),'images/polyfoil.png'))
    
    def displayName(self):
        return tr('Create polyfoil')
    
    def group(self):
        return tr('Geodesic vector creation')
        
    def groupId(self):
        return 'vectorcreation'
        
    def helpUrl(self):
        file = os.path.dirname(__file__)+'/index.html'
        if not os.path.exists(file):
            return ''
        return QUrl.fromLocalFile(file).toString(QUrl.FullyEncoded)
        
    def createInstance(self):
        return CreatePolyfoilAlgorithm()

