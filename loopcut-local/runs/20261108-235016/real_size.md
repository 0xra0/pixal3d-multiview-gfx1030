## user
Scale Sword uniformly so it is 1.28 m tall, then apply the scale.

## assistant
Sword's height is 5.0 m (Z from -2.5 to 2.5), so the uniform factor is 0.256. I'll bake the existing non-uniform scale first so the sword's proportions stay as displayed, then scale uniformly and apply.

## tool run_python [done]
Uniformly scale Sword to 1.28 m tall (preserving proportions) and apply the scale

```python
import bpy
from mathutils import Matrix

obj = bpy.data.objects['Sword']
me = obj.data

# Bake the existing non-uniform scale into the mesh so proportions are preserved
mat = Matrix.Diagonal((obj.scale.x, obj.scale.y, obj.scale.z, 1.0))
for v in me.vertices:
    v.co = mat @ v.co
obj.scale = (1.0, 1.0, 1.0)

# Uniform scale to 1.28 m tall, then apply it
factor = 1.28 / 5.0
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
obj.scale = (factor, factor, factor)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

bb = [obj.matrix_world @ v.co for v in me.vertices]
zs = [p.z for p in bb]
print("scale:", obj.scale, "height:", max(zs) - min(zs))

```

## assistant
Done — Sword is now 1.28 m tall with scale applied (1, 1, 1).

- I baked the original non-uniform scale (1, 0.1, 5) into the mesh first, so the proportions you see were kept rather than squaring up to a cube.
- Then uniform factor 0.256 and applied: new bounds `[-0.128, -0.0128, -0.64] .. [0.128, 0.0128, 0.64]`, i.e. 0.256 × 0.128 × 1.28 m.

## changes
1 changed
