from pathlib import Path
import subprocess,json,shutil,hashlib,tarfile
w=Path('/Users/ojaehong/RX_automation/rx_ws');base=w/'.g5-2-evidence';e=base/'release-clarified';context=e/'image';context.mkdir(exist_ok=False);(context/'bin').mkdir();rows=[]
def run(label,cmd):
 r=subprocess.run(cmd,capture_output=True,text=True);(e/(label+'.stdout')).write_text(r.stdout);(e/(label+'.stderr')).write_text(r.stderr);rows.append({'label':label,'argv':cmd,'exit':r.returncode});(e/'image-commands.json').write_text(json.dumps(rows,indent=2));assert r.returncode==0,(label,r.stderr[-3000:]);return r.stdout
for name in ['rx-hostd','rx-executor-service','rx-process-compile','rx-solutionsd','rx-process-package','rx-device-package']:shutil.copy2(base/'linux-target/debug'/name,context/'bin'/name)
shutil.copy2(base/'native-build/rx-dynamixel-ping',context/'bin/rx-dynamixel-ping')
for name in ['audit_native_install.py','write_runtime_inventory.py']:shutil.copy2(w/'rx-solutions/tools'/name,context/name)
shutil.copy2(w/'rx-solutions/native/dynamixel/vendor/LICENSE',context/'DynamixelSDK-LICENSE')
shutil.copy2(w/'rx-solutions/NOTICE',context/'NOTICE')
(context/'Dockerfile').write_text('''FROM rx-g5-solutions-runtime:latest
USER 0
COPY bin/ /opt/rx/bin/
COPY NOTICE /opt/rx/NOTICE
COPY audit_native_install.py write_runtime_inventory.py /opt/rx/tools/
COPY DynamixelSDK-LICENSE /opt/rx/licenses/DynamixelSDK/LICENSE
RUN rm /opt/rx/manifests/release.json /opt/rx/manifests/revocations.json && . /opt/ros/jazzy/setup.sh && /opt/rx/bin/rx-hostd drivers dynamixel > /opt/rx/manifests/dynamixel-driver.json && python3 /opt/rx/tools/audit_native_install.py --catalog /opt/rx/catalogs/device-support.v1.json --output /opt/rx/manifests/native-install-audit.json && python3 /opt/rx/tools/write_runtime_inventory.py
USER 10001:10001
''')
run('image-unsigned',['docker','build','-t','rx-g5-2-clarified-unsigned',str(context)])
for name in ['runtime-files.json','dynamixel-driver.json']:
 data=run('extract-'+name,['docker','run','--rm','--entrypoint','cat','rx-g5-2-clarified-unsigned','/opt/rx/manifests/'+name]);(e/name).write_text(data)
run('sign-runtime',['python3',str(w/'rx-platform/tools/sign_release.py'),'--key',str(w/'rx-platform/.tools/release-keys/development-release.pem'),'--inventory',str(e/'runtime-files.json'),'--version','7','--revocation-version','1','--output',str(context/'signed')])
(context/'Signed.Dockerfile').write_text('FROM rx-g5-2-clarified-unsigned\nUSER 0\nCOPY signed/ /opt/rx/manifests/\nUSER 10001:10001\n')
run('image-signed',['docker','build','-f',str(context/'Signed.Dockerfile'),'-t','rx-g5-2-clarified-runtime',str(context)])
images={k:json.loads(run('image-'+k,['docker','image','inspect',tag]))[0]['Id'] for k,tag in [('platform','rx-g5-platform-runtime:latest'),('solutions','rx-g5-2-clarified-runtime:latest')]}
logs={}
for index,test,names in [(1,'process_crash',['sigkill_at_both_journal_native_boundaries_never_replays_device_effect']),(2,'assignment_journal',['lost_run_initialization_reply_recovers_binding_without_reinitializing','run_creation_marker_cannot_change_after_header_initialization'])]:
 vals=[json.loads(line) for line in (e/f'final-build-{index}.stdout').read_text().splitlines() if line.startswith('{')]
 exe=next(v['executable'] for v in vals if v.get('executable') and v.get('target',{}).get('name')==test)
 for name in names:
  label='release-'+name;out=run(label,['docker','run','--rm','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--tmpfs','/tmp:rw','-v',str(base/'linux-target')+':/evidence/linux-target:ro','--entrypoint',exe,images['solutions'],name,'--exact','--nocapture']);assert f'test {name} ... ok' in out
  file=e/(label+'.stdout');logs[file.name]=hashlib.sha256(file.read_bytes()).hexdigest()
p=w/'rx-platform';snapshot=e/'runtime-source/rx-platform';snapshot.mkdir()
for f in subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=p).decode().split('\0'):
 if f:q=snapshot/f;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p/f,q)
archive=e/'runtime-source.tar.gz'
with tarfile.open(archive,'w:gz') as t:
 for name in ['rx-platform','rx-solutions']:t.add(e/'runtime-source'/name,arcname=name)
(e/'release-evidence.json').write_text(json.dumps({'status':'PASS_FOR_REPORTED_SCOPE','images':images,'archive':{'path':archive.name,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest()},'logs_sha256':logs,'scope':'existing recovery tests on selected image, plus adapter runtime scenes recorded separately; physical qualification not performed'},indent=2))
print(json.dumps(images))
