"""Existing distinct-role qualification approval and activation; no direct ledger writes."""
from commands import ROOT, read, write
from api import get, mutation
from commission_process import OUT, wait, cell

detail = read(OUT/'qualification-report-detail.json')
version = detail['version']; review = version['review']
if not version['ready_for_review'] or not detail['context_current'] or not detail['fences_confirmed']:
    raise ValueError('report not current/ready')
decision = mutation('/api/v1/qualification-review/decisions', {'cell':'cell/a','review':review,
                    'report_revision':version['revision'],'report_digest':version['digest'],'expected':None,
                    'choice':'APPROVE','note':'Automated distinct-role SIM normal-path review only; no fresh gripper support or CP3 recovery claim.'},
                    'qualification-approve','verifier')
write(OUT/'qualification-decision.json', decision)
current = get('/api/v1/cell','activate-cell','release',id='cell/a')
overview = get('/api/v1/overview','activation-overview','release')
if cell(overview)['runs']: raise ValueError('unexpected main Run before initial activation')
allowed = {'RUNTIME_RESTART','AUTHORITY_REVOKED','CONFIGURATION_CHANGE'}
if any(block['reason'] not in allowed for block in current['value']['blocks']):
    raise ValueError('unreviewed restriction present; do not clear it')
batch = mutation('/api/v1/qualification-activations', {'cell':'cell/a','review':review,
                 'report_revision':version['revision'],'report_digest':version['digest'],'decision_revision':decision['revision'],
                 'expected_cells':{'cell/a':current['revision']},'clear_blocks':{'cell/a':[block['id'] for block in current['value']['blocks']]}},
                 'qualification-issue','release')
write(OUT/'activation-issued.json',batch)
accepted = wait(lambda:get('/api/v1/qualification-activation','activation-status','release',cell='cell/a',id=batch['id']),
                lambda value:value['current'] and not value['mixed'] and not value['outcome_unknown']
                and value['accepted_hosts']==len(value['hosts']) and len(value['hosts'])==2,'qualification-ack',120)
write(OUT/'activation-accepted.json',accepted)
current = get('/api/v1/cell','activate-current-cell','release',id='cell/a')
active = mutation('/api/v1/qualification-activation/activate', {'cell':'cell/a','batch':batch['id'],
                  'expected':accepted['batch']['revision'],'expected_cells':{'cell/a':current['revision']}},
                  'qualification-activate','release')
write(OUT/'active.json',active)
if active['state'] != 'ACTIVE': raise ValueError('activation incomplete')
print('Both Hosts acknowledged the same approved v2 domain; P activation ACTIVE. No main Run yet.')
