import json,socket,subprocess
rows=[]
for lang in ['python','cpp']:
 for mode in ['direct','socket','spoof']:
  if lang=='cpp':r=subprocess.run(['/probe/caller',mode],capture_output=True,text=True)
  elif mode=='direct':r=subprocess.run(['/probe/helper'],capture_output=True,text=True)
  else:
   a,b=socket.socketpair();a.sendall(b'P')
   r=subprocess.run(['/probe/owner' if mode=='spoof' else 'helper'],executable='/probe/helper',stdin=b,capture_output=True,text=True)
   a.close();b.close()
  rows.append(dict(language=lang,mode=mode,exit=r.returncode,stdout=r.stdout.strip(),stderr=r.stderr.strip()))
  assert r.returncode in [21,22],rows[-1]
r=subprocess.run(['/probe/owner'],capture_output=True,text=True)
rows.append(dict(language='compiled_owner_surrogate',mode='positive',exit=r.returncode,stdout=r.stdout.strip()))
assert r.returncode==0,rows[-1]
print(json.dumps({'scope':'Linux mechanism probe only; surrogate owner; no DYNAMIXEL implementation or product Host claim','rows':rows},indent=2))
