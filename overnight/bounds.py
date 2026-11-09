import sys, trimesh
for p in sys.argv[1:]:
    s = trimesh.load(p, force='scene')
    b = s.bounds; e = b[1]-b[0]
    print(p.split('/GameAssets/')[-1] if '/GameAssets/' in p else p.split('overnight/')[-1], 'ext', e.round(3), 'min', b[0].round(3), 'faces', sum(len(g.faces) for g in s.geometry.values()))
