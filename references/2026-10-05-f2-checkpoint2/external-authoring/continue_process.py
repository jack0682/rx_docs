from commission_process import *
review = read(OUT/'process-job.json')['request']['id']
detail = get('/api/v1/process-review', 'process-review-resume', cell='cell/a', id=review)
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
identifier = change['plan']['id']
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
