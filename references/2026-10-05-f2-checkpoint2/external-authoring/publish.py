import copy
import hashlib
import json
import shutil
import uuid
from commands import ROOT, ARTIFACTS, command, installed, read, write
from api import get, post, mutation
from sign import sign

OUT = ROOT/'authoring'; bindings = {}
for label in ['robot', 's1']:
    context = get('/api/v1/package-intake-context', label+'-intake-context', cell='cell/a')
    package = ROOT/(label+'-package')
    request_file = ROOT/'site/api-requests'/(label+'-intake.json')
    body = read(request_file)['command'] if request_file.exists() else {
        'id': str(uuid.uuid4()), 'cell': 'cell/a', 'title': 'F2 '+label+' SIM templates', 'relative_path': label+'-package',
        'object': {'manifest': hashlib.sha256((package/'manifest.json').read_bytes()).hexdigest(),
                   'signature': hashlib.sha256((package/'manifest.sig.json').read_bytes()).hexdigest()},
        'configuration_digest': context['configuration_digest'], 'policy_generation': context['registration']['generation']}
    receipt = mutation('/api/v1/package-intakes', body, label+'-intake')
    write(OUT/(label+'-intake.json'), receipt)
    for node in read(package/'execution-template-catalog.json')['templates']:
        bindings[node] = {'intake': body['id'], 'template': node}
publication = {'id': str(uuid.uuid4()), 'preview': read(OUT/'preview.json')['reference'], 'cell': 'cell/a', 'bindings': bindings}
write(OUT/'publication-input.json', publication)
result = command(['python3', str(ROOT/'installed-client/rx'), 'execution', '--connection', str(ROOT/'site/connections/engineer.json'),
                  '--state-dir', str(OUT/'client'), 'publish', str(OUT/'publication-input.json'), '--output', str(OUT/'publication.json')], 'publish')
process = ROOT/'process'; process.mkdir(exist_ok=True)
recipe = read(ARTIFACTS/'public-inputs/process-recipe.json')
recipe.update(package='f2/s2-chuck-process', publisher='f2-author')
assets = {}
for binding in read(OUT/'compile-input.json')['bindings'].values():
    for ref in binding['intent']['body']['program'].values(): assets[(ref['sha256'], ref['schema_id'])] = ref
recipe['assets'] = list(assets.values()); write(process/'recipe.json', recipe)
installed('/opt/rx/bin/rx-process-package', ['assemble', '/author/authoring/compile-input.json', '/author/process/recipe.json', '/author/process/candidate'], 'process-assemble')
installed('/opt/rx/bin/rx-process-package', ['request', '/author/process/candidate', 'f2-package-signer', '/author/process/signing.json'], 'process-signing-request')
sign(process/'signing.json', process/'signature.json', 'package')
policy = read(ROOT/'site/p-config/package-policy.json')
for asset in policy['assets']: asset['path'] = '/author/site/p-config/assets/'+asset['reference']['sha256']+'.bin'
write(process/'policy.json', policy)
installed('/opt/rx/bin/rx-process-package', ['seal', '/author/process/candidate', '/author/process/signature.json', '/author/process/policy.json', '/author/process/package'], 'process-seal')
installed('/opt/rx/bin/rx-process-package', ['compile', '/author/process/package', '/author/process/policy.json', '/author/process/compiled'], 'process-compile')
resolved = read(process/'compiled/resolved.json')
publication = read(OUT/'publication.json')
steps = read(OUT/'resolution-ECC_51.json')['report']['steps']
children = resolved['root']['body']['children']
if len(children) != len(steps) or len(steps) != 11: raise ValueError('eleven-step composition differs')
binding = {'schema': 'rx.workflow-execution-binding.v2', 'publication': publication['reference'], 'policy': publication['policy'],
           'nodes': {node['id']: step['node'] for node, step in zip(children, steps)}}
plan = {'schema': 'rx.execution-plan.v2', 'binding': binding, 'process': resolved}
raw = json.dumps(plan, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
(process/'plan.json').write_bytes(raw)
initial = read(ROOT/'site/initial-cell.json'); target = copy.deepcopy(initial)
target.update(process=resolved, execution=binding, recipe={'schema_id': 'rx.execution-plan.v2', 'sha256': hashlib.sha256(raw).hexdigest(), 'size_bytes': str(len(raw))}, steps=[])
for node in children:
    action = resolved['bindings'][node['body']['binding']]
    step = copy.deepcopy(next(item for item in initial['steps'] if item['host'] == action['host'] and item['intent'] == action['intent']))
    step.update(id=node['id'], predecessors=[]); target['steps'].append(step)
write(process/'target.json', target)
receipt = post('/api/v1/workflow-executions/configuration', target, 'prepare-configuration')
write(process/'configuration.json', receipt)
print('Signed eleven-step publication/Plan prepared by installed tools; no apply, qualification or Run.')
