"""Configure the two providers from installed artifacts; no source/test-fixture imports."""
import copy
import hashlib
import json
import shutil
import time
from commands import ROOT, ARTIFACTS, IMAGES, command, installed, read, write
from installation import SITE, PREFIX, docker, put, owner, binary, start, sha
from normal_evidence import encoded, references
from api import get

info = read(SITE/'installation.json'); volumes = info['volumes']; initial = read(SITE/'initial-cell.json')
materials = ROOT/'qualification'; materials.mkdir(exist_ok=True)
pool = materials/'artifacts'; shutil.copytree(ROOT/'base-qualification/artifacts', pool, dirs_exist_ok=True)


def add(raw, schema):
    ref = {'schema_id': schema, 'sha256': hashlib.sha256(raw).hexdigest(), 'size_bytes': str(len(raw))}
    (pool/(ref['sha256']+'.bin')).write_bytes(raw)
    return ref


for file in (SITE/'p-config/assets').iterdir():
    if file.is_file(): shutil.copyfile(file, pool/file.name)
for label in ['robot', 's1']:
    for file in (ROOT/(label+'-package')).rglob('*'):
        if file.is_file(): (pool/(sha(file)+'.bin')).write_bytes(file.read_bytes())
material = read(ROOT/'authoring/material/host-material.json')
known = []
for item in material.values():
    raw = b''.join(__import__('pathlib').Path(part['path']).read_bytes() for part in item['parts'])
    known.append(add(raw, item['reference']['schema_id']))
publication = read(ROOT/'authoring/publication.json')
pubref = add(encoded(publication), 'rx.workflow-publication.v2')
target = read(ROOT/'process/target.json'); configuration = read(ROOT/'process/configuration.json')['configuration']
if add(encoded(target), 'rx.cell-configuration.v2') != configuration: raise ValueError('configuration bytes differ')
add((ROOT/'process/plan.json').read_bytes(), 'rx.execution-plan.v2')
policy = read(SITE/'p-config/qualification-policy.json'); profile = policy['profiles'][0]
profile.update(configuration=configuration, definition=target['definition'], envelope=target['envelope'])
plan = read(pool/(profile['acceptance_plan']['sha256']+'.bin'))
plan.update(configuration=configuration, scope='F2 normal mixed-model SIM; ordering only, no fresh support observation; CP3 failure recovery not yet exercised')
profile['acceptance_plan'] = add(encoded(plan), plan['schema'])
dependency_refs = [target['definition'], target['envelope'], target['recipe'], publication['policy'], pubref, *known]
for package in publication['packages'].values(): dependency_refs += package['dependencies']
for label in ['robot', 's1']: dependency_refs += read(ROOT/(label+'-package/manifest.json'))['assets']
dependency_refs += [ref for ref in profile['dependencies'] if ref['sha256'] == target['site_config_digest']]
unique = {(ref['sha256'], ref['schema_id']): ref for ref in dependency_refs}
profile['dependencies'] = sorted(unique.values(), key=lambda ref: (ref['sha256'], ref['schema_id']))
policy['keys'][0]['validators'] = [sha(ROOT/'normal_evidence.py')]
for ref in references(policy):
    raw = (pool/(ref['sha256']+'.bin')).read_bytes()
    if hashlib.sha256(raw).hexdigest() != ref['sha256'] or len(raw) != int(ref['size_bytes']): raise ValueError('policy material mismatch')
# Preserve the canonical policy bytes used by P's existing policy digest.
(materials/'policy.json').write_bytes(encoded(policy)); (SITE/'p-config/qualification-policy.json').write_bytes(encoded(policy))
write(materials/'identity.json', {'validator': sha(ROOT/'normal_evidence.py'),
      'policy_digest': hashlib.sha256(b'RX-REQUALIFICATION-POLICY-v1\n'+encoded(policy)).hexdigest()})
startup = read(SITE/'p-config/startup.json'); startup['package_intake']['qualification_policy']['sha256'] = sha(SITE/'p-config/qualification-policy.json')
write(SITE/'p-config/startup.json', startup)
shutil.copytree(ROOT/'process/package', SITE/'imports/process-package')
docker(['stop', '--timeout', '20', info['platform']], 'p-stop-for-policy')
put(volumes['p-config'], SITE/'p-config', 'policy-config'); put(volumes['imports'], SITE/'imports', 'process-import')
owner([volumes['p-config'], volumes['imports']], 'updated-p-config')
docker(['start', info['platform']], 'p-start-with-policy')
time.sleep(.3)
overview = get('/api/v1/overview', 'p-after-policy')

# Only public runtime closure files are mounted into Host; private signing keys remain outside.
runtime = ROOT/'runtime-public'; runtime.mkdir(exist_ok=True)
shutil.copytree(ROOT/'s1', runtime/'s1')
shutil.copytree(ROOT/'s1-package', runtime/'s1-package')
s1_policy = read(ROOT/'s1-policy.json')
files = {sha(file): file for file in (runtime/'s1-package').rglob('*') if file.is_file()}
for item in s1_policy['assets']: item['path'] = '/author/'+str(files[item['reference']['sha256']].relative_to(runtime))
write(runtime/'s1-policy.json', s1_policy)
registry = read(ROOT/'registry.json'); registry['entries']['example/pneumatic-chuck']['policy']['sha256'] = sha(runtime/'s1-policy.json')
write(runtime/'registry.json', registry)
for name in ['artifact', 'author-public', 'simulation']:
    volumes[name] = PREFIX+'-'+name; docker(['volume', 'create', volumes[name]], name+'-volume')
artifact_runtime = ROOT/'artifact-runtime'; artifact_runtime.mkdir(exist_ok=True)
shutil.copytree(ARTIFACTS/'s2-source', artifact_runtime/'s2-source')
shutil.copytree(ARTIFACTS/'s2', artifact_runtime/'s2', symlinks=True)
put(volumes['artifact'], artifact_runtime, 'artifact-runtime'); put(volumes['author-public'], runtime, 'public-runtime')
owner([volumes['artifact'], volumes['author-public'], volumes['simulation']], 'runtime-materials')
verified = binary('solutions', 'python3', ['/opt/rx/client/rx','skill','verify-environment','/artifact/s2/environment','--digest','8286c983cf9405193b8a40a56df1644271326274bb77f652d1ac325c7ada23c0'], [volumes['artifact']+':/artifact:ro'], 'verify-installed-robot-environment')
write(ROOT/'site/verified-robot-environment.json', json.loads(verified))
hosts = {}
for label, alias, host_name, package_label in [('ha', 's', 'host/sim', 'robot'), ('hb', 'sb', 'host/sim-b', 's1')]:
    folder = SITE/(label+'-config'); config = read(folder/'startup.json')
    bindings = read(folder/'bindings.json'); bindings[0]['allowed_intents'] = [step['intent'] for step in initial['steps'] if step['host'] == host_name]
    write(folder/'bindings.json', bindings); config['bindings']['sha256'] = sha(folder/'bindings.json')
    config['publisher']['store_generation'] = overview['installation']['store_generation']
    if label == 'ha':
        shutil.rmtree(folder/'templates'); shutil.copytree(ROOT/'robot-package', folder/'templates')
        hp = read(ROOT/'robot-policy.json')
        for item in hp['assets']:
            source = ROOT/item['path'].removeprefix('/author/'); file = folder/'assets'/(item['reference']['sha256']+'.bin')
            shutil.copyfile(source, file); item['path'] = '/config/host/assets/'+file.name
        write(folder/'package-policy.json', hp)
        config['backend'] = {'kind': 'PYTHON_EXECUTION_PACKAGE', 'directory': '/config/host/templates',
                             'manifest_digest': sha(ROOT/'robot-package/manifest.json'),
                             'policy': {'path': '/config/host/package-policy.json', 'sha256': sha(folder/'package-policy.json')}}
    else:
        config['backend'] = {'kind': 'EXTERNAL_PROCESS_PACKAGE', 'adapter': 'example/pneumatic-chuck',
                             'registry': {'path': '/author/registry.json', 'sha256': sha(runtime/'registry.json')}}
    shutil.copytree(ROOT/'authoring/material', folder/'material', dirs_exist_ok=True)
    loaded = copy.deepcopy(material)
    for item in loaded.values():
        for part in item['parts']: part['path'] = '/config/host/material/'+__import__('pathlib').Path(part['path']).name
    config['execution_materials'] = [loaded]; write(folder/'startup.json', config)
    for suffix in ['config', 'data', 'runtime']:
        volumes[label+'-'+suffix] = PREFIX+'-'+label+'-'+suffix; docker(['volume', 'create', volumes[label+'-'+suffix]], label+'-'+suffix+'-volume')
    put(volumes[label+'-config'], folder, label+'-config'); owner([volumes[label+'-config'], volumes[label+'-data'], volumes[label+'-runtime']], label)
    mounts = [volumes[label+'-config']+':/config/host:ro', volumes[label+'-data']+':/data', volumes[label+'-runtime']+':/run/rx-host',
              volumes['artifact']+':/artifact:ro', volumes['author-public']+':/author:ro', volumes['simulation']+':/data/workflow-simulation']
    binary('solutions', '/opt/rx/bin/rx-hostd', ['inspect', '/config/host/startup.json'], mounts, label+'-inspect')
    binary('solutions', '/opt/rx/bin/rx-hostd', ['init', '/config/host/startup.json'], mounts, label+'-init')
    hosts[label] = start('solutions', label, alias, '/opt/rx/bin/rx-hostd', ['run', '/config/host/startup.json'], mounts, info['network'])
    info.update(volumes=volumes, hosts=hosts); write(SITE/'installation.json', info)
for suffix in ['config', 'data']:
    volumes['e-'+suffix] = PREFIX+'-e-'+suffix; docker(['volume', 'create', volumes['e-'+suffix]], 'e-'+suffix+'-volume')
executor = read(SITE/'e-config/cell.json'); executor['expected_service']['scope']['store_generation'] = overview['installation']['store_generation']
write(SITE/'e-config/cell.json', executor); put(volumes['e-config'], SITE/'e-config', 'executor-config'); owner([volumes['e-config'], volumes['e-data']], 'executor')
mounts = [volumes['e-config']+':/config/executor:ro', volumes['e-data']+':/data']
binary('solutions', '/opt/rx/bin/rx-executor-service', ['cell', 'init', '/config/executor/cell.json'], mounts, 'executor-init')
info['executor'] = start('solutions', 'e', 'e', '/opt/rx/bin/rx-executor-service', ['cell', 'run', '/config/executor/cell.json'], mounts, info['network'])
info['volumes'] = volumes; write(SITE/'installation.json', info)
print('Builtin robot Host + external chuck Host + existing Executor started; not yet qualified.')
