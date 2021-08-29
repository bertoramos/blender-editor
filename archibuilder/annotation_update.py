
import bpy
from math import degrees

# begin local import: Change to from . import MODULE
import beaconOperator
# end local import: Change to from . import MODULE

def autoregister():
    bpy.app.handlers.depsgraph_update_post.append(update_annotations)

def autounregister():
    if update_annotations in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(update_annotations)


def update_bluetooth_beacon_annotation(obj):
    old_nota = obj.children[0]
    old_nota.parent = None
    bpy.data.objects.remove(old_nota)

    name = obj.name
    loc = obj.location.xyz
    distance = obj.data.distance
    nota = beaconOperator.draw_bluetooth_note(bpy.context, name, loc, distance)

    bpy.data.objects[nota].parent = obj
    """
    for o in bpy.data.objects:
        o.select_set(False)
    obj.select_set(True)
    """

def update_ultrasound_beacon_annotation(obj):
    old_nota = obj.children[0]
    old_nota.parent = None
    bpy.data.objects.remove(old_nota)

    name = obj.name
    loc = obj.location.xyz
    distance = obj.data.distance
    rotation = obj.rotation_euler
    spot_size = degrees(obj.data.spot_size)

    nota = beaconOperator.draw_ultrasound_note(bpy.context, name, loc, rotation, distance, spot_size)

    bpy.data.objects[nota].parent = obj
    """
    for o in bpy.data.objects:
        o.select_set(False)
    obj.select_set(True)
    """

def update_annotations(scene):
    for obj in bpy.context.selected_objects:
        if obj.object_type == "BLUETOOTH_BEACON":
            update_bluetooth_beacon_annotation(obj)
        if obj.object_type == "INFRARED_BEACON":
            update_ultrasound_beacon_annotation(obj)
