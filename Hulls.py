import FreeCAD, FreeCADGui, os, Part
from pivy import coin
import math

ui_path = os.path.join(os.path.dirname(__file__), 'hulls.ui')

class NewHullPanel():
    def __init__(self):
        self.form = FreeCADGui.PySideUic.loadUi(ui_path)

    def accept(self):
        obj = FreeCAD.ActiveDocument.addObject('App::FeaturePython', 'Hull')
        Hull(obj,
             self.form.loa.value(),
             self.form.beam.value(),
             [self.form.closedFore.isChecked(), self.form.closedAft.isChecked()],
             self.form.topSymmetrical.isChecked(),
             self.form.stations.value(),
             self.form.lines.value()
        )
        return True

class CmdNewHull():
    def __init__(self):
        self.panel = None

    def Activated(self):
        self.panel = NewHullPanel()
        FreeCADGui.Control.showDialog(self.panel)

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

    def GetResources(self):
        return { 'Pixmap': ':/icons/Hull.svg',
                 'MenuText': 'New Hull',
                 'ToolTip': 'Generate hull form' }

class Hull():
    def __init__(self, obj, LOA, beam, ends, symmetric, stations, lines):
        # self.Type = 'hull'
        obj.addProperty('App::PropertyLength', 'LOA', 'Hull', 'Length overall').LOA = 12000

        obj.addProperty('App::PropertyPythonObject', 'Points', 'Hull', 'Net of points')
        obj.Points = self.initialGeom(LOA, beam, ends, symmetric, stations, lines)
        obj.Proxy = self
        HullViewProvider(obj.ViewObject)

    def initialGeom(self, LOA, beam, ends, symmetric, stations, lines):
        # LOA = LOA / 1000
        # beam = beam / 1000
        r = beam / 2
        da = math.pi / 2 / (lines + 1)
        station_space = LOA / (stations - 1)
        vertices = [
            [
                coin.SbVec3f(ii * station_space, r * math.cos(da * jj), r * math.sin(da * jj))
                for jj in range(lines + 2)
            ]
            for ii in range(stations)
        ]
        if ends[0]:
            vertices[0] = [[0,0,0] for jj in range(lines+2)]
        if ends[1]:
            x = vertices[-1][0][0]
            vertices[-1] = [[x,0,0] for jj in range(lines+2)]
        return vertices

    def onChanged(self, fp, prop):
        pass

    def execute(self, obj):
        pass

class HullViewProvider():
    def __init__(self, obj):
        obj.addProperty('App::PropertyColor', 'Color', 'Hull', 'Color of the vertex mesh').Color = (1.0, 0.0, 0.0)
        obj.Proxy = self

    def attach(self, obj):
        self.sphereColor = coin.SoBaseColor()
        self.sphereColor.rgb.setValue(1.0, 0.0, 0.0)
        self.lineColor = coin.SoBaseColor()
        self.lineColor.rgb.setValue(1.0, 1.0, 0.0)
        self.scale = coin.SoScale()
        self.scale.scaleFactor.setValue(1.0, 1.0, 1.0)
        self.wireframe = coin.SoGroup()
        self.shaded = coin.SoGroup()

        vertexNet = coin.SoGroup()
        vertex_data = obj.Object.getPropertyByName('Points')
        for ii, data_row in enumerate(vertex_data):
            for jj, data_point in enumerate(data_row):
                vertex = coin.SoSeparator()
                coord = coin.SoCoordinate3()
                coord.point.setValue(data_point)
                s = coin.SoType.fromName("SoBrepPointSet").createInstance()
                s.numPoints.setValue(1)
                pointstyle = coin.SoDrawStyle()
                pointstyle.style = coin.SoDrawStyle.POINTS
                vertex += pointstyle
                vertex += coord
                vertex += s
                vertexNet += vertex

        lines = coin.SoGroup()
        for ii, data_row in enumerate(vertex_data):
            line = coin.SoSeparator()
            coords = coin.SoCoordinate3()
            coords.point.setValues(0, len(data_row), data_row)
            lineSet = coin.SoType.fromName("SoBrepEdgeSet").createInstance()
            lineSet.coordIndex.setValues(0, len(data_row), range(len(data_row)))
            line += coords
            line += lineSet
            lines += line

        stations = coin.SoGroup()
        for ii in range(len(vertex_data[0])):
            line = coin.SoSeparator()
            coord_data = [vertex_data[jj][ii] for jj in range(len(vertex_data))]
            coords = coin.SoCoordinate3()
            coords.point.setValues(0, len(coord_data), coord_data)
            lineSet = coin.SoType.fromName("SoBrepEdgeSet").createInstance()
            lineSet.coordIndex.setValues(0, len(coord_data), range(len(coord_data)))
            line += coords
            line += lineSet
            stations += line

        style = coin.SoDrawStyle()
        style.style = coin.SoDrawStyle.LINES
        self.wireframe += style
        self.wireframe += self.scale
        self.wireframe += self.sphereColor
        self.wireframe += vertexNet
        self.wireframe += self.lineColor
        self.wireframe += lines
        self.wireframe += stations
        obj.addDisplayMode(self.wireframe, 'Wireframe')

        self.shaded += self.scale
        self.shaded += self.sphereColor
        self.shaded += vertexNet
        self.shaded += self.lineColor
        self.shaded += lines
        self.shaded += stations
        obj.addDisplayMode(self.shaded, 'Shaded')
        vertex_data[1][0].setValue(100, 5000, -600)

    def updateData(self, fp, prop):
        self.scale.scaleFactor.setValue(1.0, 1.0, 1.0)
        pass

    def getDisplayModes(self, obj):
        return ['Wireframe', 'Shaded']

    def getDefaultDisplayMode(self):
        return 'Shaded'

    def setDisplayMode(self, mode):
        return mode

    def onChanged(self, vp, prop):
        pass

    def getIcon(self):
        return """
/* XPM */
static const char * ViewProviderBox_xpm[] = {
"16 16 6 1",
"    c None",
".   c #141010",
"+   c #615BD2",
"@   c #C39D55",
"#   c #000000",
"$   c #57C355",
"        ........",
"   ......++..+..",
"   .@@@@.++..++.",
"   .@@@@.++..++.",
"   .@@  .++++++.",
"  ..@@  .++..++.",
"###@@@@ .++..++.",
"##$.@@$#.++++++.",
"#$#$.$$$........",
"#$$#######      ",
"#$$#$$$$$#      ",
"#$$#$$$$$#      ",
"#$$#$$$$$#      ",
" #$#$$$$$#      ",
"  ##$$$$$#      ",
"   #######      "};
"""

    def __getstate__(self):
        return None

    def __setState__(self, state):
        return None
