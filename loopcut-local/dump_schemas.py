"""Headless: how big are the tool schemas a single local agent gets? Prints count and size per tool."""
import json, sys
sys.path.insert(0, "/mnt/sata/loopcut/loopcut/harness")
import checkout
checkout.use()
from loopcut import tools, agent
names = [(s["function"]["name"], len(json.dumps(s))) for s in tools.SCHEMAS]
total = sum(n for _, n in names)
print(f"SCHEMAS {len(names)} tools, {total} chars ~{total // 4} tokens; system prompt {len(agent.SYSTEM_PROMPT)} chars")
for name, n in sorted(names, key=lambda x: -x[1]):
    print(f"  {n:6d} {name}")
