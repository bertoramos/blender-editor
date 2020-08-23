
import bpy

# begin local import: Change to from . import MODULE
import cursorListener as cl
import pathEditor as pe
import robot as robot_tools
# end local import: Change to from . import MODULE

keymaps = []

def autoregister():
    global classes
    classes = [PathCreationPanel, ToolsPanel, PathEditorMenu]
    for cls in classes:
        bpy.utils.register_class(cls)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')

        kmi = km.keymap_items.new("wm.call_menu_pie", type='Q', value='PRESS', ctrl=True, shift=True).properties.name = PathEditorMenu.bl_idname
        keymaps.append((km, kmi))

def autounregister():
    global classes
    for cls in classes:
        bpy.utils.unregister_class(cls)

    for km, kmi in keymaps:
        km.keymap_items.remove(kmi)
    keymaps.clear()


class PathCreationPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_PathCreationPanel"
    bl_label = "Create path"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Robot Control"

    def draw(self, context):
        self.layout.operator(cl.StartPosesListener.bl_idname, icon="CURVE_PATH", text="Start editor")
        self.layout.operator(cl.StopPosesListener.bl_idname, icon="DISK_DRIVE", text="Stop editor (Save poses)")
        self.layout.operator(pe.RemoveLastSavedPoseOperator.bl_idname, icon="GPBRUSH_ERASE_STROKE")
        self.layout.operator(pe.ClearPathOperator.bl_idname, icon="X")

class ToolsPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_ToolsPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Path creation tools"

    @classmethod
    def poll(cls, context):
        # Cursor active?
        return any([scene.is_cursor_active for scene in bpy.data.scenes])

    def draw(self, context):
        self.layout.operator(pe.SavePoseOperator.bl_idname, icon="IMPORT")
        self.layout.operator(pe.UndoPoseOperator.bl_idname, icon="LOOP_BACK")
        self.layout.operator(pe.MoveCursorToLastPoseOperator.bl_idname, icon="REW")
        self.layout.operator(pe.SelectCursorOperator.bl_idname, icon="ORIENTATION_CURSOR")


class PathEditorMenu(bpy.types.Menu):
    bl_label = "Path editor menupie"
    bl_idname = "OBJECT_MT_PathEditorMenu"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator(pe.SavePoseOperator.bl_idname, icon="IMPORT")
        pie.operator(pe.UndoPoseOperator.bl_idname, icon="LOOP_BACK")
        pie.operator(pe.MoveCursorToLastPoseOperator.bl_idname, icon="REW")
        pie.operator(pe.SelectCursorOperator.bl_idname, icon="ORIENTATION_CURSOR")
