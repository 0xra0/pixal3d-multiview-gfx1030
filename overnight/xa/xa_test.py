import sys, time, numpy as np, trimesh, xatlas
m = trimesh.load(sys.argv[1], force="mesh", process=False)
m.merge_vertices(merge_tex=True, merge_norm=True)
v, f = np.asarray(m.vertices, np.float32), np.asarray(m.faces, np.uint32)
print("faces", len(f), "verts", len(v))
for res, pad, cfg in [(2048, 4, {}), (2048, 4, {"max_cost": 4.0}), (2048, 4, {"max_cost": 8.0, "normal_deviation_weight": 1.0})]:
    t = time.time()
    a = xatlas.Atlas(); a.add_mesh(v, f)
    co = xatlas.ChartOptions()
    for k, val in cfg.items(): setattr(co, k, val)
    po = xatlas.PackOptions(); po.resolution = res; po.padding = pad; po.bilinear = True; po.rotate_charts = True
    a.generate(co, po)
    vm, idx, uv = a[0]
    tri = uv[idx]
    ar = 0.5 * np.abs((tri[:,1,0]-tri[:,0,0])*(tri[:,2,1]-tri[:,0,1]) - (tri[:,2,0]-tri[:,0,0])*(tri[:,1,1]-tri[:,0,1]))
    print(cfg, "charts", a.chart_count, "coverage", round(float(ar.sum()), 4), "util", round(a.utilization, 3), "zero", int((ar < 1e-12).sum()), "secs", round(time.time() - t, 1))
