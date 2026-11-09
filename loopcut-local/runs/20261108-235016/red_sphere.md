## user
Add a UV sphere of radius 0.5 m resting on top of the cube, centred on it, with a pure red material (red base colour).

## assistant
Creating the sphere on the cube's top face (top at z=1, so centre at z=1.5) and a pure red material.

## tool run_python [done]
Add UV sphere (r=0.5) centred on top of the cube with a pure red material

```python
import bpy

# Create UV sphere of radius 0.5
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, segments=32, ring_count=16, location=(0.0, 0.0, 1.5))
sphere = bpy.context.active_object
sphere.name = "Sphere"

# Pure red material
mat = bpy.data.materials.new("Red")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (1.0, 0.0, 0.0, 1.0)

sphere.data.materials.append(mat)
print(sphere.name, sphere.location, len(sphere.data.vertices), len(sphere.data.polygons))

```

## tool check_contact [done]
Check contact: Sphere rests_on Cube

## assistant
Done.

- **Sphere** — UV sphere, radius 0.5 m (32 segments / 16 rings, 482 verts), origin at `(0, 0, 1.5)`, so it sits tangent on the cube's top face at z = 1, centred in X/Y. Contact check confirms it touches the cube with no penetration.
- **Material `Red`** — Principled BSDF, Base Color `(1, 0, 0)`. The capture looks slightly washed because AgX view transform tone-maps pure red; the material value itself is pure red.

Verified by Loopcut on this scene: 1 of 1 checks.
Passed: sphere rests on cube.

## changes
2 added, 1 changed
