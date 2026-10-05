from pathlib import Path
import subprocess,time,json
root=Path(__file__).parent
for name in ['installation.py','author_workflow.py','publish.py','configure_runtime.py','commission_process.py','qualify.py','activate.py','run.py']:
 started=time.monotonic()
 p=subprocess.run(['python3',str(root/name)],capture_output=True,text=True)
 (root/(name+'.stdout')).write_text(p.stdout);(root/(name+'.stderr')).write_text(p.stderr)
 with (root/'helper-invocations.jsonl').open('a') as f:f.write(json.dumps({'helper':name,'rc':p.returncode,'wall_seconds':time.monotonic()-started})+'\n')
 print(name,p.returncode,p.stdout[-350:],p.stderr[-1000:],flush=True)
 if p.returncode:raise SystemExit(p.returncode)
