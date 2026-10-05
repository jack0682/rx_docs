"""Assemble scoped SIM evidence from actual observations; never manufacture a verdict."""
import hashlib
import json
import shutil
from pathlib import Path


def encoded(value): return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()


def references(value):
    if isinstance(value, dict):
        if set(value) == {'schema_id', 'sha256', 'size_bytes'}: return [value]
        return [ref for item in value.values() for ref in references(item)]
    if isinstance(value, list): return [ref for item in value for ref in references(item)]
    return []


def build(job, observations, pool, output):
    request = job['request']
    output.mkdir(); artifacts = output/'artifacts'; artifacts.mkdir()
    checks = []
    for cell in request['cells']:
        for criterion in cell['profile']['criteria']:
            measured = observations[criterion['area']]
            if not measured['assertions'] or any(type(v) is not bool or not v for v in measured['assertions'].values()):
                raise ValueError('unproven criterion: '+criterion['area'])
            evidence = {'schema': criterion['evidence_schema'], 'cell': cell['profile']['cell'], 'criterion': criterion['id'],
                        'scope': 'F2_CP2_NORMAL_ELEVEN_STEP_SIM_ONLY', **measured}
            raw = encoded(evidence); digest = hashlib.sha256(raw).hexdigest()
            (artifacts/(digest+'.bin')).write_bytes(raw)
            checks.append({'cell': cell['profile']['cell'], 'criterion': criterion['id'], 'verdict': 'PASS',
                           'evidence': [{'schema_id': criterion['evidence_schema'], 'sha256': digest, 'size_bytes': str(len(raw))}],
                           'note': 'Actual scoped software/SIM observations; no fresh gripper support or CP3 failure-recovery claim.'})
    for ref in references(request):
        source = pool/(ref['sha256']+'.bin'); raw = source.read_bytes()
        if hashlib.sha256(raw).hexdigest() != ref['sha256'] or len(raw) != int(ref['size_bytes']):
            raise ValueError('qualification material differs')
        shutil.copyfile(source, artifacts/source.name)
    report = {'schema': 'rx.requalification-report.v1', 'request': request,
              'validator': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'checks': checks}
    (output/'qualification.json').write_bytes(encoded(report))
