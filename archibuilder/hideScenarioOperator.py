
import bpy

def menu_func(self, context):
    text = "Show scenario" if HideScenarioOperator.hidden else "Hide scenario"
    icon = "HIDE_ON" if HideScenarioOperator.hidden else "HIDE_OFF"
    self.layout.operator(HideScenarioOperator.bl_idname, text=text, icon=icon)

def autoregister():
    global classes
    classes = [ HideScenarioOperator ]
    
    for c in classes:
        bpy.utils.register_class(c)
    
    bpy.types.VIEW3D_MT_view.append(menu_func)

def autounregister():
    global classes

    bpy.types.VIEW3D_MT_view.append(menu_func)

    for c in classes:
        bpy.utils.unregister_class(c)

scenario_obj = { "WALL", "CEIL"}

class HideScenarioOperator(bpy.types.Operator):
    bl_idname = "object.hidescenario"
    bl_label = "Hide scenario"

    hidden = False

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        for obj in bpy.data.objects:
            if hasattr(obj, "object_type") and obj.object_type in scenario_obj:
                obj.hide_set(not HideScenarioOperator.hidden)
        
        HideScenarioOperator.hidden = not HideScenarioOperator.hidden
        return {'FINISHED'}
