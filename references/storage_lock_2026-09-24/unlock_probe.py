import os,fcntl,json,tempfile

def blocked(path):
 with open(path,'a+') as contender:
  try:fcntl.flock(contender,fcntl.LOCK_EX|fcntl.LOCK_NB);return False
  except BlockingIOError:return True

def child(owner):
 pr,cw=os.pipe();cr,pw=os.pipe();pid=os.fork()
 if pid==0:
  os.close(pr);os.close(pw);os.write(cw,b'R')
  command=os.read(cr,1)
  if command==b'U':fcntl.flock(owner,fcntl.LOCK_UN)
  os.write(cw,b'A');os.read(cr,1);os._exit(0)
 os.close(cw);os.close(cr);assert os.read(pr,1)==b'R';return pid,pr,pw
rows=[]
with tempfile.TemporaryDirectory() as d:
 path=d+'/owner.lock';owner=open(path,'w+');fcntl.flock(owner,fcntl.LOCK_EX|fcntl.LOCK_NB)
 pid,r,w=child(owner)
 assert blocked(path),'live owner must refuse entrant'
 fcntl.flock(owner,fcntl.LOCK_UN)
 contender=open(path,'a+');fcntl.flock(contender,fcntl.LOCK_EX|fcntl.LOCK_NB)
 assert blocked(path),'new live owner must refuse third entrant'
 # An old duplicate must not release a different open-file-description owner.
 os.write(w,b'U');assert os.read(r,1)==b'A'
 assert blocked(path),'old child unlock must not release new owner'
 owner.close();assert blocked(path),'closing former owner must not release new owner'
 os.write(w,b'X');os.waitpid(pid,0);os.close(r);os.close(w)
 assert blocked(path),'old child exit must not release new owner'
 fcntl.flock(contender,fcntl.LOCK_UN);contender.close();assert not blocked(path)
 rows.append(dict(scene='owner_unlock_with_fork_duplicate',live_owner_denied=True,reacquired_while_child_alive=True,new_owner_denial_survives_old_child_unlock_close_exit=True))
 # Dangerous rival: blindly unlocking the inherited description from child Drop.
 owner=open(path,'a+');fcntl.flock(owner,fcntl.LOCK_EX|fcntl.LOCK_NB);pid,r,w=child(owner)
 assert blocked(path);os.write(w,b'U');assert os.read(r,1)==b'A'
 admitted=not blocked(path);assert admitted
 rows.append(dict(scene='blind_descendant_unlock_counterexample',parent_owner_still_open=True,second_writer_wrongly_admitted=admitted,meaning='raw LOCK_UN releases shared description; unconditional inherited guard Drop would weaken ownership'))
 os.write(w,b'X');os.waitpid(pid,0);os.close(r);os.close(w);owner.close()
print(json.dumps({'result':'PREMISE_CONFIRMED_WITH_DESCENDANT_RELEASE_HAZARD','scenes':rows}))
