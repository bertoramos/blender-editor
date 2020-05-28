
import bpy
import atexit
import time

"""
@atexit.register
def on_exit():
    s = ""
    if bpy.context.scene.com_props.prop_running_nav:
        res = bpy.ops.wm.stop_plan()
        s += str(res) + " "

    if bpy.context.scene.com_props.prop_mode == 1: # En modo robot
        res = bpy.ops.wm.change_mode()
        s += str(res) + " "

    if bpy.context.scene.is_cursor_active:
        res = bpy.ops.scene.stop_cursor_listener()
        s += str(res) + " "

    print(s)
"""
