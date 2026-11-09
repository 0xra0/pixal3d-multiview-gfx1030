import sys, os
sys.path.insert(0, "/mnt/sata/loopcut/loopcut/harness/local_evals")
os.environ["LOCAL_EVAL_OUT"] = "/mnt/ssd/work/loopcut-local/selfcheck-out"
import bpy, tasks
tasks.setup("gn_scatter"); tasks.reference("gn_scatter")
g = tasks.evaluated(tasks.get("Ground"))
print("HAS evaluated_geometry", hasattr(g, "evaluated_geometry"))
gs = g.evaluated_geometry()
print("GS attrs", [a for a in dir(gs) if not a.startswith("_")])
pc = gs.instances_pointcloud()
print("INSTANCES", len(pc.points) if pc else None)
refs = gs.instance_references()
print("REFS", [type(r).__name__ + ":" + getattr(r, "name", "") for r in refs][:5])
dg = bpy.context.evaluated_depsgraph_get()
print("DG", [(i.is_instance, i.object.name, i.parent.name if i.parent else None) for i in dg.object_instances][:6])
