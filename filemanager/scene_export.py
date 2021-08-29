
import bpy
from bpy.types import Operator, Panel, PropertyGroup
import os
import re

# begin local import: Change to from . import MODULE
# end local import: Change to from . import MODULE

def autoregister():
    global classes
    classes = [FileProps, ExportScenarioOperator, ExportScenarioPanel]
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.file_props = bpy.props.PointerProperty(type=FileProps)

def autounregister():
    global classes
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.file_props


exportable_objects = {"WALL",
                      "CEIL",
                      "OBSTACLE",
                      "OBSTACLE_MARGIN",
                      "BLUETOOTH_BEACON",
                      "ULTRASOUND_BEACON",
                      "OTHER"}

def export():
    path = bpy.context.scene.file_props.prop_path
    filename = bpy.context.scene.file_props.prop_name
    filepath = os.path.join(path, filename)

    if not os.access(path, os.W_OK):
        return False

    bpy.ops.scene.new(type='FULL_COPY')
    current_scene = bpy.context.scene

    wm = bpy.context.window_manager

    wm.progress_begin(0, len(current_scene.objects))

    i = 0
    for obj in current_scene.objects:
        if obj.object_type not in exportable_objects:
            dat = obj.data
            mat = obj.active_material
            bpy.data.objects.remove(obj, do_unlink=True)
            if dat is not None:
                if dat.name_full in bpy.data.meshes:
                    bpy.data.meshes.remove(dat)
            #if mat is not None:
            #    bpy.data.materials.remove(mat)
        wm.progress_update(i)
        i += 1
    # write scene
    data_blocks = {current_scene}
    bpy.data.libraries.write(filepath, data_blocks)

    for obj in current_scene.objects:
        bpy.data.objects.remove(obj)

    bpy.data.scenes.remove(current_scene)

    wm.progress_end()
    return True

def update_filename(self, context):
    pass

def set_filename(self, value):
    filename = value.split("\\")[-1]
    if not re.search(r"^[^.]+\.blend$", filename):
        chunks = filename.split(".")
        if filename.endswith(".blend"):
            filename = chunks[-2] + "." + chunks[-1]
        else:
            filename = chunks[-1] + ".blend"
    filename = "scenario.blend" if filename == ".blend" else filename
    self["prop_name"] = filename

def get_filename(self):
    return self.get("prop_name", "scenario.blend")

class FileProps(PropertyGroup):
    prop_path: bpy.props.StringProperty(name="File path", description="File path", default="", subtype="DIR_PATH")
    prop_name: bpy.props.StringProperty(name="File name", description="File name", default="", subtype="FILE_NAME", update=update_filename, get=get_filename, set=set_filename)

class ExportScenarioOperator(Operator):
    bl_idname = "export.scene_export"
    bl_label = 'Export scene'
    bl_options = {"REGISTER"}
    bl_description = "Export scenario into .blend file"

    @classmethod
    def poll(cls, context):
        # Si en alguna escena se indica que esta el cursor activo, no puede exportarse el escenario
        return True

    def execute(self, context):
        if export():
            self.report({'INFO'}, "Exported")
        else:
            self.report({'INFO'}, " Can't be exported")
        return {'FINISHED'}

class ExportScenarioPanel(Panel):
    bl_idname = "OBJECT_PT_ExportScenePanel"
    bl_label = "File"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Options"

    def draw(self, context):
        props = bpy.context.scene.file_props
        self.layout.prop(props, "prop_path", text="")
        self.layout.prop(props, "prop_name", text="")
        self.layout.operator("export.scene_export", icon='EXPORT', text="Save scene")
