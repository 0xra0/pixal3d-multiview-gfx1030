import bpy
from bpy_extras import anim_utils
m = bpy.data.materials.new("t")
print("RENDER_METHODS", [i.identifier for i in bpy.types.Material.bl_rna.properties["surface_render_method"].enum_items])
bpy.ops.mesh.primitive_cube_add()
ob = bpy.context.object
ob.location.x = 1; ob.keyframe_insert("location", frame=1)
ob.location.x = 3; ob.keyframe_insert("location", frame=20)
ad = ob.animation_data
cb = anim_utils.action_get_channelbag_for_slot(ad.action, ad.action_slot)
print("KEYFRAME_SLOT", ad.action is not None, ad.action_slot is not None, len(cb.fcurves),
      [k.co[:] for k in cb.fcurves[0].keyframe_points])
try:
    bpy.ops.object.shade_auto_smooth(); print("AUTO_SMOOTH_OK", [m.type for m in ob.modifiers])
except Exception as ex:
    print("AUTO_SMOOTH_FAIL", ex)
