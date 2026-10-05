"""Run the mixed model scenario through the installed product CLI, not a component fixture."""
import json
import uuid
import threading
import subprocess
import time
from commands import ROOT, command, read, write

OUT = ROOT/'run'; OUT.mkdir(exist_ok=True)
connection = ROOT/'site/connections/operator.json'
client = ['python3',str(ROOT/'installed-client/rx'),'execution','--connection',str(connection),'--state-dir',str(OUT/'client')]
closure = read(ROOT/'authoring/material/inputs-0.json'); patterns = {}
for step in closure['spec']['steps']:
    for prop in closure['spec']['tasks'][step['task']]['properties'].values():
        for source in prop['sources']:
            if source['kind'] == 'PATTERN': patterns[source['slot']] = source['rule']
for slot, rule in patterns.items():
    refs = closure['requests'][0]['contexts'].get(slot, closure['spec']['defaults'][slot])
    if len(refs) != 1: raise ValueError('single resource required')
    path = OUT/('inventory-'+slot+'.json')
    write(path, {'cell':'cell/a','resource':refs[0],'rule':rule,'expected_generation':None,
                 'reason':'Explicit external-adapter SIM stock; no fresh support observation'})
    command(client+['initialize-slots',str(path),'--output',str(OUT/('inventory-'+slot+'-receipt.json'))], 'initialize-'+slot)
request = str(uuid.uuid4());(OUT/'request-id.txt').write_text(request+'\n')
args = client+['run',str(ROOT/'authoring/publication.json'),'--count','3']
for number in range(1,4): args += ['--object',str(ROOT/'authoring'/('precheck-'+str(number)+'.json'))]
args += ['--request-id',request,'--until-unknown','--wait-seconds','180','--output',str(OUT/'product-receipt.json')]
write(OUT/'command.json',{'executor':'Codex','argv':args,'environment':'SIMULATION',
                        'support_basis':'SAME_PART_ACQUIRE_SUPPORT_SETTLED_SUCCEEDED_ORDER','fresh_support_observation':False})
stop = threading.Event()
samples = []
def observe():
    while not stop.wait(4):
        observed_args = ['python3',str(ROOT/'installed-client/rx'),'api','--connection',str(connection),'get','/api/v1/overview']
        started = time.monotonic()
        value = subprocess.run(observed_args,capture_output=True,text=True)
        with (OUT/'observation-commands.jsonl').open('a') as stream:
            stream.write(json.dumps({'argv':observed_args,'rc':value.returncode,'wall_seconds':time.monotonic()-started,'stderr':value.stderr})+'\n')
        if value.returncode == 0:
            overview = json.loads(value.stdout)
            main = next(row for row in overview['cells'] if row['cell']['value']['id']=='cell/a')
            samples.append({'installation':overview['installation'],'diagnostics':main['diagnostics']})
            write(OUT/'source-observations.json',samples)
watch = threading.Thread(target=observe)
watch.start()
try:
    result = command(args,'mixed-n3-run',check=False)
finally:
    stop.set(); watch.join()
print(json.dumps({'rc':result.returncode,'request_id':request,'stderr':result.stderr[-2000:]}))
if (OUT/'product-receipt.json').exists():
    value = read(OUT/'product-receipt.json')
    print(json.dumps({'run':value['binding']['run'],'state':value['result']['run']['value']['state'],
                      'parts':len(value['result']['parts']),'operations':len(value['result']['work'])}))
