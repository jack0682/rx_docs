from commission_process import *
change=read(OUT/'change-created.json')
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
