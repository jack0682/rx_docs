"""Existing P review/configuration sequence through installed CLI and observed API documents."""
import hashlib
import json
import shutil
import time
import uuid
from commands import ROOT, command, installed, read, write
from installation import SITE, put, owner
from api import get, post, mutation
from sign import sign

OUT = ROOT/'commission'; OUT.mkdir(exist_ok=True)
INFO = read(SITE/'installation.json')


def wait(call, predicate, label, timeout=60):
    deadline = time.monotonic()+timeout
    while True:
        value = call()
        if predicate(value): return value
        if time.monotonic() >= deadline:
            write(OUT/(label+'-last.json'), value)
            raise RuntimeError(label+' did not become ready; original state preserved')
        time.sleep(5)


def cell(overview): return next(row for row in overview['cells'] if row['cell']['value']['id'] == 'cell/a')
def transition(change): return {'cell': 'cell/a', 'change': change['id'], 'expected': change['revision'], 'plan_digest': change['plan_digest']}


if __name__ == '__main__':
    ready = wait(lambda: get('/api/v1/overview', 'ready-overview'),
                 lambda value: len(cell(value)['diagnostics']['hosts']) == 2
                 and all(h['context'] == 'CURRENT' for h in cell(value)['diagnostics']['hosts'])
                 and all(s['usable'] for s in cell(value)['diagnostics']['sources']), 'both-hosts')
    write(OUT/'before.json', ready)
    context = get('/api/v1/package-intake-context', 'process-intake-context', cell='cell/a')
    package = ROOT/'process/package'
    intake_command = {'id': str(uuid.uuid4()), 'cell': 'cell/a', 'title': 'F2 eleven-step mixed-model SIM',
                      'relative_path': 'process-package', 'object': {'manifest': hashlib.sha256((package/'manifest.json').read_bytes()).hexdigest(),
                      'signature': hashlib.sha256((package/'manifest.sig.json').read_bytes()).hexdigest()},
                      'configuration_digest': context['configuration_digest'], 'policy_generation': context['registration']['generation']}
    intake = mutation('/api/v1/package-intakes', intake_command, 'process-intake')
    review = str(uuid.uuid4())
    selections = {'skill/'+str(i): 'step/'+step['id'] for i, step in enumerate(read(ROOT/'workflow.json')['spec']['steps'], 1)}
    request = {'id': review, 'cell': 'cell/a', 'intake': intake_command['id'], 'configuration_digest': context['configuration_digest'],
               'policy_generation': context['registration']['generation'], 'binding_selections': selections, 'device_plans': []}
    job = mutation('/api/v1/process-reviews', request, 'process-review')
    write(OUT/'process-job.json', job); write(OUT/'review-request.json', job['request'])
    result = json.loads(installed('/opt/rx/bin/rx-process-package', ['review', '/author/process/package', '/author/process/policy.json',
                       '/author/commission/review-request.json', '/author/commission/process-review'], 'process-software-review').stdout)
    if not result['compiler_checks_passed'] or result['activation_authorized']: raise ValueError('software review did not pass as non-authority')
    write(OUT/'software-result.json', result)
    installed('/opt/rx/bin/rx-process-package', ['review-signing-request', '/author/commission/process-review/verification.json',
              'f2-review-signer', '/author/commission/review-signing.json'], 'review-signing-request')
    sign(OUT/'review-signing.json', OUT/'process-review/verification.sig.json', 'review')
    upload = OUT/'upload'; upload.mkdir(exist_ok=True); shutil.copytree(OUT/'process-review', upload/'process-review')
    put(INFO['volumes']['imports'], upload, 'review-upload'); owner([INFO['volumes']['imports']], 'review-upload')
    mutation('/api/v1/process-review/reports', {'cell': 'cell/a', 'review': review, 'directory': 'process-review', 'expected': None,
             'report_digest': result['report_digest']}, 'process-report')
    detail = get('/api/v1/process-review', 'process-review-detail', cell='cell/a', id=review)
    write(OUT/'process-review-detail.json', detail)
    report = detail['verification']
    decision = mutation('/api/v1/process-review/decisions', {'cell':'cell/a', 'review':review, 'expected':None,
                        'report_revision': report['revision'], 'review_digest': report['review_digest'], 'choice':'APPROVE',
                        'note':'Automated distinct-role review of actual compiler evidence, SIM only; no fresh support observation.'}, 'process-approve', 'verifier')
    write(OUT/'process-decision.json', decision)
    change = mutation('/api/v1/process-changes', {'id':str(uuid.uuid4()), 'cell':'cell/a', 'mode':'REPLACE',
                      'review':{'id':review, 'revision':report['revision'], 'review_digest':report['review_digest'],
                                'decision_revision':decision['revision']},
                      'execution_configuration':read(ROOT/'process/configuration.json')['configuration'],
                      'reason':'F2 SIM external adapter normal path; qualification and effects remain separate.'}, 'process-change')
    write(OUT/'change-created.json', change)
    identifier = change['id']
    def current(): return get('/api/v1/process-change', 'process-change-detail', 'release', cell='cell/a', id=identifier)
    detail = current()
    mutation('/api/v1/process-change/impact-review', {'target':transition(detail['change']),
             'note':'Exact isolated two-Host SIM scope; no fresh gripper support claim.'}, 'process-impact', 'verifier')
    detail = current(); mutation('/api/v1/process-change/stage', transition(detail['change']), 'process-stage', 'release')
    detail = current(); mutation('/api/v1/process-change/prepare', {'target':transition(detail['change']), 'refresh':False}, 'process-prepare', 'release')
    detail = current(); mutation('/api/v1/process-change/configure-hosts', transition(detail['change']), 'process-hosts', 'release')
    detail = wait(current, lambda value: value['host_configuration']['all_hosts_acknowledged']
                  and not value['host_configuration']['outcome_unknown'] and not value['host_configuration']['mixed_configuration'], 'configuration-ack')
    write(OUT/'before-apply.json', detail)
    mutation('/api/v1/process-change/apply', transition(detail['change']), 'process-apply', 'release')
    detail = current(); write(OUT/'applied.json', detail)
    if detail['change']['state'] != 'APPLIED_UNQUALIFIED': raise ValueError('expected unqualified application')
    print('Two Hosts accepted and applied the signed process configuration; qualification remains separate.')
