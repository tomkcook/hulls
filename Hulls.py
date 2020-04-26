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

        obj.addProperty('App::PropertyVectorList', 'Points', 'Hull', 'Net of points')
        obj.addProperty('App::PropertyInteger', 'NetWidth', 'Hull', 'Number of lines + 2').NetWidth = lines + 2
        obj.addProperty('App::PropertyInteger', 'NetLength', 'Hull', 'Number of stations').NetLength = stations
        print('Setting points')
        obj.Points = self.initialGeom(LOA, beam, ends, symmetric, stations, lines)
        print('Set')
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
                FreeCAD.Vector(ii * station_space, r * math.cos(da * jj), r * math.sin(da * jj))
                for jj in range(lines + 2)
            ]
            for ii in range(stations)
        ]
        if ends[0]:
            vertices[0] = [FreeCAD.Vector(0,0,0) for jj in range(lines+2)]
        if ends[1]:
            x = vertices[-1][0][0]
            vertices[-1] = [FreeCAD.Vector(x,0,0) for jj in range(lines+2)]
        vertices = [v for row in vertices for v in row]
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
        self.wireframe = coin.SoGroup()
        self.shaded = coin.SoSeparator()
        self.drawStyle = coin.SoDrawStyle()
        self.drawStyle.pointSize.setValue(10)
        self.drawStyle.style = coin.SoDrawStyle.LINES
        self.pointMaterial = coin.SoMaterial()
        self.pointMaterial.diffuseColor = (1.0, 0.0, 0.0)
        self.shaded += self.drawStyle
        self.shaded += self.pointMaterial
        self.wireframe += self.drawStyle
        self.wireframe += self.pointMaterial

        vertex_data = obj.Object.getPropertyByName('Points')
        n = obj.Object.getPropertyByName('NetWidth')
        m = obj.Object.getPropertyByName('NetLength')
        coord = coin.SoCoordinate3()
        coord.point.setValues(0, len(vertex_data), vertex_data)

        for ii in range(n):
            for jj in range(m):
                sep = coin.SoSeparator()
                sep += self.pointMaterial
                p = vertex_data[ii * m + jj]
                co = coin.SoCoordinate3()
                co.point.setValue(p[0], p[1], p[2])
                sep += co
                s = coin.SoType.fromName('SoPointSet').createInstance()
                s.numPoints.setValue(1)
                sep += s
                self.shaded += sep

        stations = coin.SoSeparator()
        stations += coord
        for ii in range(n):
            sep = coin.SoSeparator()
            indices = [ii + jj * n for jj in range(m)]
            lineSet = coin.SoType.fromName('SoBrepEdgeSet').createInstance()
            lineSet.coordIndex.setValues(0, len(indices), indices)
            sep += lineSet
            stations += sep

        self.shaded += stations
        self.wireframe += stations

        lines = coin.SoSeparator()
        lines += coord
        for jj in range(m):
            indices = [ii + jj * n for ii in range(n)]
            lineSet = coin.SoType.fromName('SoBrepEdgeSet').createInstance()
            lineSet.coordIndex.setValues(0, len(indices), indices)
            lines += lineSet

        self.shaded += lines
        self.wireframe += lines

        obj.addDisplayMode(self.wireframe, 'Wireframe')
        obj.addDisplayMode(self.shaded, 'Shaded')

    def updateData(self, fp, prop):
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
