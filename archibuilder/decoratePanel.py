
import bpy
import beaconOperator as bo
import obstacleOperator as oo

def autoregister():
    bpy.utils.register_class(DecoratePanel)

def autounregister():
    bpy.utils.unregister_class(DecoratePanel)

class DecoratePanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_DecoratePanel"
    bl_label = "Decorate"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Archibuilder" # Add new tab to N-Panel

    def draw(self, context):
        self.layout.operator(oo.AddObstacleOperator.bl_idname, icon='MESH_CUBE', text="Create object")
        self.layout.operator(bo.AddBeaconOperator.bl_idname, icon='LIGHT_POINT', text="Create beacon")
