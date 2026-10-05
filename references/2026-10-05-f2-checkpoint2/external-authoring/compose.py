"""Compose the external scenario from exported workflow/template artifacts only."""
import copy
import hashlib
import json
import uuid
from commands import ROOT, ARTIFACTS, read, write

base = ARTIFACTS / 'public-inputs'
workflow = read(base/'workflow.json')
workflow.update(id=str(uuid.uuid4()), expected=None, label='S2 + external chuck SIM; operation-order support only')
tasks = workflow['spec']['tasks']
acquire = copy.deepcopy(tasks['unload'])
acquire['label'] = 'Acquire support · SIM operation order, no fresh sensor'
acquire['skills'][0]['primitive'] = 'acquire-support'
acquire['done'].update(observation='gripper.part_held', property={'$ref': 'observation.part_held'})
withdraw = copy.deepcopy(tasks['unload'])
withdraw['label'] = 'Withdraw after external unclamp'
withdraw['skills'][0]['primitive'] = 'withdraw'
unclamp = copy.deepcopy(tasks['clamp'])
unclamp.update(label='External chuck unclamp after same-Part support operation', contexts=['machine'],
               properties={'timeout': copy.deepcopy(tasks['clamp']['properties']['timeout'])}, constraints=[])
unclamp['skills'][0].update(primitive='unclamp', parameters={'timeout_s': 'timeout'})
unclamp['done']['equals']['data']['value'] = False
tasks.update({'acquire-support': acquire, 'withdraw': withdraw, 'unclamp': unclamp})
workflow['spec']['steps'] = [item for step in workflow['spec']['steps'] for item in (
    [{'id': key, 'task': key} for key in ['acquire-support', 'unclamp', 'withdraw']]
    if step['id'] == 'unload' else [step])]
write(ROOT/'workflow.json', workflow)

catalog = read(base/'a-execution-template-catalog.json')
catalog['templates'].update(read(base/'b-execution-template-catalog.json')['templates'])
robot = copy.deepcopy(catalog)
robot['templates'].pop('clamp')
old = robot['templates'].pop('unload')
for key in ['acquire-support', 'withdraw']:
    node = copy.deepcopy(old)
    node['contract']['primitive'] = key
    node['action']['intent']['target'] = 'device/s2/' + key
    robot['templates'][key] = node
environment = read(ARTIFACTS/'s2/environment/environment.json')
raw = (ARTIFACTS/'s2/environment/environment.json').read_bytes()
program_ref = {'schema_id': 'rx.python-environment.v1', 'sha256': hashlib.sha256(raw).hexdigest(), 'size_bytes': str(len(raw))}
profile = {'schema': 'rx.python-execution-profile.v2', 'environment': '/artifact/s2/environment',
           'environment_digest': environment['environment_digest'], 'program': program_ref}
for node in robot['templates'].values():
    node['action']['host'] = 'host/sim'
    node['action']['intent']['body']['program']['program'] = program_ref
write(ROOT/'robot-assembly.json', {'schema': 'rx.python-execution-assembly.v2', 'profile': profile, 'catalog': robot})

chuck = copy.deepcopy(catalog)
chuck['templates'] = {'clamp': copy.deepcopy(catalog['templates']['clamp'])}
node = copy.deepcopy(chuck['templates']['clamp'])
node['contract']['primitive'] = 'unclamp'
node['contract']['parameters'] = {'timeout_s': copy.deepcopy(node['contract']['parameters']['timeout_s'])}
node['action']['intent']['target'] = 'device/s1/unclamp'
chuck['templates']['unclamp'] = node
program = read(ROOT/'s1/program.json')
program_ref = read(ROOT/'logs/program-pin.stdout')['reference']
for node in chuck['templates'].values():
    node['action']['host'] = 'host/sim-b'
    node['action']['intent']['completion_rule'] = 'rx.simulation.chuck-completed.v1'
    node['action']['intent']['body']['program']['program'] = program_ref
profile = {'schema': 'rx.external-process-profile.v1', 'protocol': 'rx.external-process-channel.v1',
           'program': program_ref, 'commands': {key: node['contract'] for key, node in chuck['templates'].items()},
           'observations': {key: {'schema': 'boolean/v1', 'unit': 'unitless', 'value_type': 'BOOLEAN',
                                 'maximum_age_ns': '1000000000', 'maximum_uncertainty_ns': '0'}
                            for key in ['sim/ready', 'chuck.clamped']},
           'conditions': {'sim/ready': 'sim/ready'}}
outcomes = {'schema': 'rx.native-outcome-table.v1', 'profile_digest': '00'*32,
            'completion_rule': 'rx.simulation.chuck-completed.v1',
            'cases': [{'status_schema': 'rx.simulation.chuck-completed.v1', 'statuses': ['0'], 'conclusion': 'SUCCEEDED'}]}
write(ROOT/'s1/assembly.json', {'schema': 'rx.external-process-assembly.v1', 'profile': profile,
                               'program': program, 'catalog': chuck, 'outcomes': outcomes})
for key in ['robot', 's1']:
    write(ROOT/(key+'-recipe.json'), {'schema': 'rx.device-package-recipe.v1', 'package': 'f2/'+key,
                                    'publisher': 'f2-author', 'version': '2.0.0',
                                    'targets': [{'architecture': 'ARM64', 'os': 'LINUX', 'ros_distribution': None}]})
write(ROOT/'scope.json', {'environment': 'SIMULATION', 'workflow_nodes': 11, 'model_order': ['ECC_51', 'ECC_99', 'ECC_51'],
                         'support_basis': 'SAME_PART_ACQUIRE_SUPPORT_SETTLED_SUCCEEDED_ORDER',
                         'fresh_support_observation': False, 'core_sources_referenced': False})
