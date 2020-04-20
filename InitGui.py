class HullsWorkbench ( Workbench ):
    Icon = FreeCAD.getHomePath() + "Mod/Hulls/Resources/icons/HullsWorkbench.svg"
    MenuText = "Hulls"
    ToolTip = "Hulls workbench"

    def Initialize(self):
        # load the module
        self.appendToolbar('Hulls', ['Hulls_NewHull'])
        self.appendMenu('Hulls',['Hulls_NewHull'])

    def GetClassName(self):
        return "Gui::PythonWorkbench"

Gui.addWorkbench(HullsWorkbench())

from Hulls import CmdNewHull
FreeCADGui.addCommand('Hulls_NewHull', CmdNewHull())
