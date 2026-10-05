"""Use installed product commands to import exported definitions and author the eleven steps."""
import copy
import json
import uuid
from commands import ROOT, ARTIFACTS, command, read, write

OUT = ROOT/'authoring'; OUT.mkdir(exist_ok=True)
CONNECTION = ROOT/'site/connections/engineer.json'


def call(kind, args, label):
    result = command(['python3', str(ROOT/'installed-client/rx'), kind, '--connection', str(CONNECTION),
                      '--state-dir', str(OUT/'client'), *map(str, args)], label)
    return json.loads(result.stdout)


base = ARTIFACTS/'public-inputs'
closure = read(base/'material/inputs-0.json')
references = read(base/'s2.json')['references']
keys = {value['id']: key for key, value in references.items()}
pending = {item['reference']['id']: item for item in closure['definitions']}


def dependencies(value):
    if isinstance(value, dict):
        if set(value) == {'catalog', 'id', 'revision', 'digest'}: return {value['id']}
        return set().union(*(dependencies(v) for v in value.values()))
    if isinstance(value, list): return set().union(*(dependencies(v) for v in value))
    return set()


def aliases(value):
    if isinstance(value, dict):
        if set(value) == {'catalog', 'id', 'revision', 'digest'}: return {'$ref': keys[value['id']]}
        return {key: aliases(item) for key, item in value.items()}
    if isinstance(value, list): return [aliases(item) for item in value]
    return value


ordered = []; available = set()
while pending:
    ready = [identity for identity, item in pending.items() if dependencies(item['body']) <= available]
    if not ready: raise ValueError('exported dependency closure is incomplete or cyclic')
    for identity in ready:
        item = pending.pop(identity)
        ordered.append({'key': keys[identity], 'id': identity, 'expected': None,
                        'label': item['label'], 'body': aliases(item['body'])})
        available.add(identity)
write(OUT/'definitions.json', {'schema': 'rx.definition-package.v1', 'catalog': closure['workflow']['catalog'],
                               'title': 'Exported SIM baseline for external adapter trial', 'definitions': ordered})
refs = call('definitions', ['apply', OUT/'definitions.json', '--output', OUT/'definitions-receipt.json'], 'definitions-apply')
workflow = call('workflow', ['--references', OUT/'definitions-receipt.json', 'apply', ROOT/'workflow.json',
                            '--output', OUT/'workflow-receipt.json'], 'workflow-apply')
reports = {}
for label in ['ECC_51', 'ECC_99']:
    reports[label] = call('workflow', ['--references', OUT/'definitions-receipt.json', 'resolve',
                                     OUT/'workflow-receipt.json', '--context', 'part=part.rotation-'+label,
                                     '--output', OUT/('resolution-'+label+'.json')], 'resolve-'+label)
templates = read(ROOT/'templates.json')
preview = {'id': str(uuid.uuid4()), 'candidates': [{'key': label,
           'object_model': refs['references']['part.rotation-'+label], 'request': reports[label]['report']['request']}
          for label in reports], 'slots': 24, 'templates': {k:v['action'] for k,v in templates.items()},
          'node_contracts': {k:v['contract'] for k,v in templates.items()}}
write(OUT/'preview-input.json', preview)
call('execution', ['preview', OUT/'preview-input.json', '--output', OUT/'preview.json'], 'preview')
call('execution', ['export', OUT/'preview.json', OUT/'material'], 'export-material')
steps = [step['node'] for step in reports['ECC_51']['report']['steps']]
composed = call('runtime', ['compose', 'external/s2-chuck-SIM', '--cell', 'cell/a']+
                [item for node in steps for item in ['--step', 'step/'+node]], 'compose-process')
write(OUT/'compile-input.json', composed['compile_input'])
objects = {'schema': 'rx.definition-package.v1', 'catalog': closure['workflow']['catalog'],
           'title': 'Mixed actual SIM parts; no fresh support observation', 'definitions': []}
for purpose in ['precheck', 'acceptance']:
    for ordinal, model in enumerate(['ECC_51', 'ECC_99', 'ECC_51'], 1):
        objects['definitions'].append({'key': 'object.'+purpose+'-'+str(ordinal), 'id': str(uuid.uuid4()), 'expected': None,
                                      'label': purpose+' '+model+' SIM', 'body': {'kind':'OBJECT_INSTANCE',
                                      'base': {'$ref': 'part.rotation-'+model}, 'values':{}}})
write(OUT/'objects.json', objects)
result = call('definitions', ['--references', OUT/'definitions-receipt.json', 'apply', OUT/'objects.json',
                             '--output', OUT/'objects-receipt.json'], 'objects-apply')
for name, ref in result['references'].items():
    if name.startswith('object.'):
        write(OUT/(name.removeprefix('object.')+'.json'), ref)
print('Eleven-step mixed-model workflow resolved and previewed through installed CLI. No Run.')
