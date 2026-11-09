import json, sys
r = json.load(open(sys.argv[1] + "/asset_report.json"))
u = r["uv"]
print("status", r["status"], "coverage", round(u["metrics"]["coverage"], 4), "islands", u["metrics"]["islands"], "subpx", u["metrics"]["islands_under_one_pixel"],
      "isolated", u.get("isolated_faces"), "method", u.get("method"), u.get("method_fallback"), "relax", u["chart_relaxation"].get("accepted"))
print("pack", u["pack_candidates"]); print("bake miss", [x["fraction"] for x in r["bake"]["projection_miss"]], "black", round(r["bake"]["basecolor_black_fraction"], 3))
print("issues", [i["code"] for i in r["quality"]["issues"]])
