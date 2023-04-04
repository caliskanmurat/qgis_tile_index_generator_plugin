from qgis.gui import QgsRubberBand, QgsMapToolEmitPoint, QgsMapTool
from PyQt5 import QtGui
from qgis.core import QgsWkbTypes, QgsRectangle, QgsPointXY

from shapely.wkt import loads

from qgis.core import QgsProject
from qgis.PyQt.QtWidgets import QMessageBox

class RectangleMapTool(QgsMapToolEmitPoint):
    def __init__(self, canvas, dlg):
        self.canvas = canvas
        QgsMapToolEmitPoint.__init__(self, self.canvas)
        self.rubberBand = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
        self.rubberBand.setColor(QtGui.QColor(0, 0, 255))
        self.rubberBand.setFillColor(QtGui.QColor(0, 0, 255, 50))
        self.rubberBand.setWidth(1)
        self.reset()
        self.dlg = dlg
    
    def reset(self):
        self.startPoint = self.endPoint = None
        self.isEmittingPoint = False
        self.rubberBand.reset(QgsWkbTypes.PolygonGeometry)
    
    def canvasPressEvent(self, e):
        self.startPoint = self.toMapCoordinates(e.pos())
        self.endPoint = self.startPoint
        self.isEmittingPoint = True
        self.showRect(self.startPoint, self.endPoint)
    
    def canvasReleaseEvent(self, e):
        self.isEmittingPoint = False
        r = self.rectangle()
        if r is not None:
            self.deactivate()
            self.reset()
            self.canvas.unsetMapTool(self)
            self.canvas.refresh()
            self.dlg.showNormal()
            
            """ ------------------ """
            
            self.wkt_ext = r.asWktPolygon()
            geom = loads(self.wkt_ext)
            self.srs = QgsProject.instance().crs().authid()
            self.setMaxValues(self.srs)
            
            if self.srs in "EPSG:3857":
                minx, miny, maxx, maxy = geom.bounds
                
                self.w_minx, self.w_miny, self.w_maxx, self.w_maxy = -20037508.3428, -20037508.3428, 20037508.3428, 20037508.3428 #EPSG:3857
                self.dlg.lbl_srs.setText(self.srs)
                
            elif self.srs == "EPSG:4326":
                minx, miny, maxx, maxy = geom.bounds
                
                self.w_minx, self.w_miny, self.w_maxx, self.w_maxy = -180, -85.05112877980660357, 180, 85.05112877980660357 #EPSG:4326
                self.dlg.lbl_srs.setText(self.srs)
                
            else:
                minx=miny=maxx=maxy = 0
                self.dlg.lbl_srs.setText("Unavaliable")
                QMessageBox.critical(None, "ERROR", "Available SRSs --> EPSG:3857, EPSG:4326")
            
            try:
                if (minx < self.w_minx) or (miny < self.w_miny) or (maxx > self.w_maxx) or (maxy > self.w_maxy):
                    print("mmmm")
                    minx=miny=maxx=maxy = 0
                    QMessageBox.critical(None, "ERROR", "Canvas extent is out of CRS extent!")
            except:
                minx=miny=maxx=maxy = 0
                
            self.dlg.sb_extent_minx.setValue(minx)
            self.dlg.sb_extent_miny.setValue(miny)
            self.dlg.sb_extent_maxx.setValue(maxx)
            self.dlg.sb_extent_maxy.setValue(maxy)
            
            """ ------------------ """
            
    def canvasMoveEvent(self, e):
        if not self.isEmittingPoint:
            return
    
        self.endPoint = self.toMapCoordinates(e.pos())
        self.showRect(self.startPoint, self.endPoint)
    
    def showRect(self, startPoint, endPoint):
        self.rubberBand.reset(QgsWkbTypes.PolygonGeometry)
        if startPoint.x() == endPoint.x() or startPoint.y() == endPoint.y():
            return
      
        self.point1 = QgsPointXY(startPoint.x(), startPoint.y())
        self.point2 = QgsPointXY(startPoint.x(), endPoint.y())
        self.point3 = QgsPointXY(endPoint.x(), endPoint.y())
        self.point4 = QgsPointXY(endPoint.x(), startPoint.y())
      
        self.rubberBand.addPoint(self.point1, False)
        self.rubberBand.addPoint(self.point2, False)
        self.rubberBand.addPoint(self.point3, False)
        self.rubberBand.addPoint(self.point4, False)
        self.rubberBand.addPoint(self.point1, True)    # true to update canvas
        
        self.rubberBand.show()

    def rectangle(self):
        if self.startPoint is None or self.endPoint is None:
            return None
        elif (self.startPoint.x() == self.endPoint.x() or self.startPoint.y() == self.endPoint.y()):
            return None
        return QgsRectangle(self.startPoint, self.endPoint)
    
    def deactivate(self):
        QgsMapTool.deactivate(self)
        self.deactivated.emit()

    def setMaxValues(self, srs):
        if srs == "EPSG:4326":
            w_minx, w_miny, w_maxx, w_maxy = -180, -85.05112877980660357, 180, 85.05112877980660357 #EPSG:4326
        else:
            w_minx, w_miny, w_maxx, w_maxy = -20037508.3428, -20037508.3428, 20037508.3428, 20037508.3428 #EPSG:3857
        
        self.dlg.sb_extent_minx.setMinimum(w_minx)
        self.dlg.sb_extent_minx.setMaximum(w_maxx)
        
        self.dlg.sb_extent_miny.setMinimum(w_miny)
        self.dlg.sb_extent_miny.setMaximum(w_maxy)
        
        self.dlg.sb_extent_maxx.setMinimum(w_minx)
        self.dlg.sb_extent_maxx.setMaximum(w_maxx)
        
        self.dlg.sb_extent_maxy.setMinimum(w_miny)
        self.dlg.sb_extent_maxy.setMaximum(w_maxy)