"""Explicit isolated SIM provisioning using configuration artifacts and installed binaries."""
import copy
import hashlib
import json
import os
import shutil
import time
from pathlib import Path
from commands import ROOT, ARTIFACTS, IMAGES, command, installed, read, write
from sign import key

os.umask(0o077)
SITE = ROOT/'site'
PREFIX = 'rx-f2-s1d'


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def docker(args, label, check=True): return command(['docker', *args], label, 'setup', check=check).stdout.strip()


def put(volume, directory, label):
    name = PREFIX+'-copy-'+label
    docker(['create', '--name', name, '--network', 'none', '--user', '0', '-v', volume+':/copy',
            '--entrypoint', '/bin/true', IMAGES['solutions']], label+'-holder')
    docker(['cp', str(directory)+'/.', name+':/copy/'], label+'-copy')
    docker(['rm', name], label+'-remove-holder')


def owner(volumes, label):
    mounts = [item for index, volume in enumerate(volumes) for item in ['-v', volume+':/owned/'+str(index)]]
    docker(['run', '--rm', '--network', 'none', '--user', '0', *mounts, '--entrypoint', '/bin/sh',
            IMAGES['solutions'], '-c', 'chown -R 10001:10001 /owned'], label+'-permissions')


def binary(role, binary, args, mounts, label):
    return docker(['run', '--rm', '--network', 'none', '--user', '10001:10001',
                   *[arg for mount in mounts for arg in ['-v', mount]], '--entrypoint', binary,
                   IMAGES[role], *args], label)


def start(role, label, alias, binary, args, mounts, network, ports=()):
    name = PREFIX+'-'+label
    docker(['create', '--name', name, '--network', network,
            *(['--network-alias', alias] if network != 'bridge' else []),
            '--user', '10001:10001', '--read-only', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges',
            '--tmpfs', '/tmp:rw,uid=10001,gid=10001,mode=700',
            *[arg for mount in mounts for arg in ['-v', mount]],
            *[arg for port in ports for arg in ['-p', port]], '--entrypoint', binary, IMAGES[role], *args], label+'-create')
    docker(['start', name], label+'-start')
    return name


def cli(args, label, who='engineer', check=True):
    return command(['python3', str(ROOT/'installed-client/rx'), *args], label, check=check)


if __name__ == '__main__':
    # All configuration below was exported from an installed SIM site, not source code.
    config = SITE/'p-config'
    catalog = read(config/'catalog.json')
    cell = next(item for item in catalog['cells'] if item['id'] == 'cell/a')
    prototype = copy.deepcopy(cell['steps'][0]); cell['steps'] = []
    templates = read(ROOT/'robot-package/execution-template-catalog.json')['templates']
    templates.update(read(ROOT/'s1-package/execution-template-catalog.json')['templates'])
    for node in [step['id'] for step in read(ROOT/'workflow.json')['spec']['steps']]:
        template = templates[node]; step = copy.deepcopy(prototype)
        step.update(id='step/'+node, host=template['action']['host'], intent=template['action']['intent'], predecessors=[])
        step['completion']['schema'] = step['intent']['completion_rule']
        for test in step['conditions']+step['completion']['postconditions']:
            test['fact'] = 'sim/ready' if step['host'] == 'host/sim-b' else 'ready'
        cell['steps'].append(step)
    sensor = copy.deepcopy(next(f for f in cell['fact_specs'] if f['host'] == 'host/sim-b'))
    sensor['id'] = 'chuck.clamped'; cell['fact_specs'] = [f for f in cell['fact_specs'] if f['id'] != 'chuck.clamped']; cell['fact_specs'].append(sensor)
    write(config/'catalog.json', catalog); write(SITE/'initial-cell.json', cell)
    write(ROOT/'templates.json', templates)
    policy = read(config/'package-policy.json')
    _, public = key('package')
    manifests = [read(ROOT/(name+'-package/manifest.json')) for name in ['robot', 's1']]
    permissions = {json.dumps(item, sort_keys=True): item for manifest in manifests for item in manifest['permissions']}
    for i in range(1, 12):
        item = {'kind': 'OPERATION_SUBMIT', 'operation': 'skill/'+str(i)}
        permissions[json.dumps(item, sort_keys=True)] = item
    policy['keys'] = [{'id': 'f2-package-signer', 'publisher': 'f2-author', 'verifying_key': public,
                       'kinds': ['DEVICE', 'PROCESS'], 'permissions': list(permissions.values())}]
    assets = {item['reference']['sha256']: item for item in policy['assets']}
    for label, manifest in zip(['robot', 's1'], manifests):
        package = ROOT/(label+'-package')
        files = {sha(file): file for file in package.rglob('*') if file.is_file()}
        for artifact in manifest['assets']:
            target = config/'assets'/(artifact['sha256']+'.bin'); shutil.copyfile(files[artifact['sha256']], target)
            assets[artifact['sha256']] = {'reference': artifact, 'path': '/config/assets/'+target.name}
    policy['assets'] = list(assets.values()); write(config/'package-policy.json', policy)
    review = read(config/'review-authority.json'); _, public = key('review')
    validator = json.loads(installed('/opt/rx/bin/rx-process-package', ['validator-identity'], 'process-validator').stdout)['validator_digest']
    review['keys'] = [{'id': 'f2-review-signer', 'public_key': public, 'validators': [validator]}]
    write(config/'review-authority.json', review)
    qualification = read(config/'qualification-policy.json'); _, public = key('qualification')
    qualification['keys'][0].update(id='f2-qualification-signer', public_key=public)
    write(config/'qualification-policy.json', qualification)
    startup = read(config/'startup.json'); startup['https']['origin'] = 'https://127.0.0.1:8462'
    startup['catalog']['sha256'] = sha(config/'catalog.json')
    for entry in startup['package_intake'].values():
        if isinstance(entry, dict) and 'path' in entry:
            entry['sha256'] = sha(config/Path(entry['path']).name)
    write(config/'startup.json', startup)
    imports = SITE/'imports'; imports.mkdir(exist_ok=True)
    for name in ['robot', 's1']: shutil.copytree(ROOT/(name+'-package'), imports/(name+'-package'))
    volumes = {name: PREFIX+'-'+name for name in ['p-config', 'p-data', 'imports']}
    for volume in volumes.values(): docker(['volume', 'create', volume], volume+'-create')
    put(volumes['p-config'], config, 'p-config'); put(volumes['imports'], imports, 'imports')
    owner(list(volumes.values()), 'p')
    mounts = [volumes['p-config']+':/config:ro', volumes['p-data']+':/data', volumes['imports']+':/import:ro']
    docker(['run','--rm','--network','none','--user','0','-v',volumes['p-data']+':/data','--entrypoint','/bin/sh',IMAGES['platform'],'-c','mkdir -p /data/runtime && chown 10001:10001 /data/runtime'],'p-runtime-directory')
    binary('platform', '/usr/local/bin/rx-platformd', ['init', '/config/startup.json'], mounts, 'p-init')
    network = PREFIX+'-network'; front = 'bridge'
    docker(['network', 'create', '--internal', '--subnet', '10.254.251.0/24', network], 'internal-network')
    container = start('platform', 'p', 'p', '/usr/local/bin/rx-platformd', ['run', '/config/startup.json'], mounts, front, ['127.0.0.1:8462:8443'])
    docker(['network', 'connect', '--alias', 'p', network, container], 'p-internal-network')
    write(SITE/'installation.json', {'platform': container, 'network': network, 'front': front, 'volumes': volumes, 'platform_mounts': mounts})
    # Reuse explicitly provided installed terminal identity artifacts in this isolated SIM copy.
    provided = ROOT.parent/'framework-f2-two-host/live3'
    connection_dir = SITE/'connections'; connection_dir.mkdir(exist_ok=True)
    for who in ['installer', 'engineer', 'verifier', 'release', 'operator']:
        connection = read(provided/(who+'.json')); connection['origin'] = 'https://127.0.0.1:8462'
        for field in ['ca', 'certificate', 'private_key', 'password_file']:
            source = Path(connection[field]); target = connection_dir/(who+'-'+field)
            shutil.copyfile(source, target); target.chmod(0o600)
            connection[field] = str(target)
        write(connection_dir/(who+'.json'), connection)
    print('Fresh isolated SIM P installed from configuration artifacts. No qualification or Run.')
