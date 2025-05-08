
import bpy

class CustomOverrideOperator(bpy.types.Operator):
    bl_idname = "object.override_delete"
    bl_label = "Custom Override Operator"

    def execute(self, context):
        print("Custom Override Operator executed!")
        return {'FINISHED'}

# Function to replace the operator for object.delete keymap
def replace_operator_in_keymap():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.user  # Use 'user' for user preferences

    # Access the keymap for 'Object Mode'
    km = kc.keymaps.get('Object Mode', None)
    if km:
        # Search for the specific keymap item (object.delete)
        for kmi in km.keymap_items:
            if kmi.idname == 'object.delete':
                # Replace the operator with your custom one
                kmi.idname = 'object.override_delete'  # Replace with your operator ID
                print("Operator replaced:", kmi)
                break
        else:
            print("object.delete keymap not found.")
    else:
        print("Object Mode keymap not found.")

def register():
    bpy.utils.register_class(CustomOverrideOperator)
    replace_operator_in_keymap()
    

def unregister():
    bpy.utils.unregister_class(CustomOverrideOperator)

if __name__=="__main__":
    register()
    

