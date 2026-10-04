import hashlib,json,subprocess,tempfile
from pathlib import Path
host=Path("/opt/rx/bin/rx-hostd")
source=Path("/config/host/startup.json")
original=json.loads(source.read_text())
root=Path(tempfile.mkdtemp(prefix="f2-support-preflight-"))
def inspect(path):
 p=subprocess.run([str(host),"inspect",str(path)],capture_output=True,text=True)
 return {"argv":["/opt/rx/bin/rx-hostd","inspect",str(path)],"rc":p.returncode,"stdout":p.stdout,"stderr":p.stderr}
baseline=inspect(source)
bindings=json.loads(Path(original["bindings"]["path"]).read_text())
before=bindings[0]["condition_ids"][:]
bindings[0]["condition_ids"].append("gripper.part_held")
raw=json.dumps(bindings,sort_keys=True,separators=(",",":")).encode()
b=root/"bindings.json"; b.write_bytes(raw)
original["bindings"]={"path":str(b),"sha256":hashlib.sha256(raw).hexdigest()}
modified=root/"startup.json"; modified.write_text(json.dumps(original,sort_keys=True,separators=(",",":")))
negative=inspect(modified)
print(json.dumps({"executor":"Codex","acceptance":"NOT_REQUESTED","scope":"Read-only product CLI inspection in an ephemeral container; not a two-Host Run","host_binary_sha256":hashlib.sha256(host.read_bytes()).hexdigest(),"baseline_condition_ids":before,"proposed_existing_boolean_guard":"gripper.part_held","baseline":baseline,"support_guard":negative},indent=2))
