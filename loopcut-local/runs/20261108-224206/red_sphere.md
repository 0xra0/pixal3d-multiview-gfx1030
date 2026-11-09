## user
Add a UV sphere of radius 0.5 m resting on top of the cube, centred on it, with a pure red material (red base colour).

## assistant
Simple build: cube top is at z=1.0, so the sphere (r=0.5) centres at z=1.5. I'll add it plus a pure-red Principled material.

## tool run_python [done]
Add UV sphere (r=0.5) centred on top of the cube with a pure red material

```python

import bpy

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(0.0, 0.0, 1.5), segments=32, ring_count=16)
sphere = bpy.context.active_object
sphere.name = "Sphere"

mat = bpy.data.materials.new("Red")
mat.use_nodes = True
bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
bsdf.inputs["Base Color"].default_value = (1.0, 0.0, 0.0, 1.0)
sphere.data.materials.append(mat)

print(sphere.name, sphere.location)

```

## tool check_contact [done]
Check contact: Sphere rests_on Cube

## assistant
Done — verified contact passes (sphere's lowest point touches the cube's top face), centred on it, and the "Red" material has pure red Base Color on the Principled BSDF.

Verified by Loopcut on this scene: 1 of 1 checks.
Passed: sphere rests on cube.

## changes
2 added, 1 changed
