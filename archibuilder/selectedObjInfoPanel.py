
import bpy

def autoregister():
    bpy.utils.register_class(SelectedObjectInfoPanel)

def autounregister():
    bpy.utils.unregister_class(SelectedObjectInfoPanel)

class SelectedObjectInfoPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_SelectedObjectInfoPanel"
    bl_label = "Properties"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Archibuilder" # Add new tab to N-Panel
    
    def draw(self, context):
        obj = context.object
        
        if obj is not None:
            if obj.object_type == "BLUETOOTH_BEACON":
                self.layout.label(text="Name : " + obj.name)
                self.layout.label(text="Type : Bluetooth beacon")
                self.layout.label(text="MAC address : " + obj['mac'])
