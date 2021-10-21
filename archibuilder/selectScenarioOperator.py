
import bpy

def menu_func(self, context):
    self.layout.operator(SelectScenarioOperator.bl_idname, icon='VIEW_PAN')

def autoregister():
    global classes
    classes = [ SelectScenarioOperator ]
    
    for c in classes:
        bpy.utils.register_class(c)
    
    bpy.types.VIEW3D_MT_select_object.append(menu_func)

def autounregister():
    global classes

    bpy.types.VIEW3D_MT_select_object.append(menu_func)

    for c in classes:
        bpy.utils.unregister_class(c)

scenario_obj = { "WALL", "CEIL", "OBSTACLE"}

class SelectScenarioOperator(bpy.types.Operator):
    bl_idname = "object.selectscenario"
    bl_label = "Select scenario"

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        for obj in bpy.data.objects:
            if hasattr(obj, "object_type") and obj.object_type in scenario_obj:
                obj.select_set(True)
        return {'FINISHED'}
