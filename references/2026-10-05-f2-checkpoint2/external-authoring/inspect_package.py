"""Product rx-hostd inspection/refusal checks with installed artifacts, no repository mount."""
import copy
import hashlib
import json
import shutil
from commands import ROOT, ARTIFACTS, command, read, write

OUT = ROOT/'inspection'; OUT.mkdir(exist_ok=True)
for name in ['startup.json', 'bindings.json']:
    result = command(['docker', 'exec', 'rx-f2-twohost-hb', 'cat', '/config/host/'+name], 'export-'+name, 'artifact')
    (OUT/name).write_text(result.stdout)
config = read(OUT/'startup.json')
bindings = read(OUT/'bindings.json')
catalog = read(ROOT/'s1-package/execution-template-catalog.json')
bindings[0]['allowed_intents'] = [node['action']['intent'] for node in catalog['templates'].values()]
write(OUT/'bindings.json', bindings)
config['bindings'] = {'path': '/author/inspection/bindings.json', 'sha256': hashlib.sha256((OUT/'bindings.json').read_bytes()).hexdigest()}
config['execution_materials'] = []
config['backend'] = {'kind': 'EXTERNAL_PROCESS_PACKAGE',
                     'registry': {'path': '/author/registry.json', 'sha256': hashlib.sha256((ROOT/'registry.json').read_bytes()).hexdigest()},
                     'adapter': 'example/pneumatic-chuck'}
write(OUT/'positive.json', config)
cases = {'positive': config}
missing = copy.deepcopy(config); missing['backend']['adapter'] = 'unregistered/chuck'
cases['unregistered'] = missing
shutil.copytree(ROOT/'s1-package', ROOT/'s1-tampered')
with (ROOT/'s1-tampered/program.json').open('a') as stream: stream.write(' ')
for label, directory in [('unsigned', '/author/s1-candidate'), ('tampered', '/author/s1-tampered')]:
    registry = read(ROOT/'registry.json')
    registry['entries']['example/pneumatic-chuck']['directory'] = directory
    write(OUT/(label+'-registry.json'), registry)
    changed = copy.deepcopy(config)
    changed['backend']['registry'] = {'path': '/author/inspection/'+label+'-registry.json',
                                      'sha256': hashlib.sha256((OUT/(label+'-registry.json')).read_bytes()).hexdigest()}
    cases[label] = changed
results = {}
for label, configuration in cases.items():
    write(OUT/(label+'.json'), configuration)
    argv = ['docker', 'run', '--rm', '--network', 'none', '--user', '0', '--volumes-from', 'rx-f2-twohost-hb:ro',
            '-v', str(ROOT)+':/author:ro', '-v', str(ARTIFACTS)+':/artifact:ro',
            '--entrypoint', '/opt/rx/bin/rx-hostd', 'rx-f2-solutions:b1', 'inspect', '/author/inspection/'+label+'.json']
    result = command(argv, 'host-inspect-'+label, check=False)
    expected = 0 if label == 'positive' else 1
    if result.returncode != expected: raise RuntimeError(label+': '+result.stderr)
    results[label] = {'rc': result.returncode, 'stderr': result.stderr,
                      'inspection': json.loads(result.stdout) if label == 'positive' else None}
write(OUT/'results.json', results)
print(json.dumps({key: value['rc'] for key, value in results.items()}))
