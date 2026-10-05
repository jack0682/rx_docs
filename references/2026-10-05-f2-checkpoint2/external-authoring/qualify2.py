"""Qualify the normal SIM path with measured evidence via installed commands, not a test signer."""
import hashlib
import json
import shutil
import uuid
from commands import ROOT, ARTIFACTS, IMAGES, command, installed, read, write
from installation import SITE, put, owner, docker
from api import get, mutation
from commission_process import OUT, INFO, wait, cell
from normal_evidence import build
from sign import sign

change = read(OUT/'applied.json')['change']
restrictions = get('/api/v1/runtime-restrictions', 'requalification-restrictions', 'release', cell='cell/a')
current = get('/api/v1/cell', 'requalification-cell', 'release', id='cell/a')
request = {'id':str(uuid.uuid4()), 'cell':'cell/a', 'change':change['id'], 'expected_change':change['revision'],
           'expected_cells':{'cell/a':current['revision']}, 'policy_digest':read(ROOT/'qualification/identity.json')['policy_digest'],
           'runtime_restrictions':{item['block']['id']:item['origin_digest'] for item in restrictions['restrictions']}}
job = mutation('/api/v1/qualification-reviews', request, 'qualification-review-2', 'release')
write(OUT/'qualification-job.json', job)
review = job['request']['id']
detail = wait(lambda:get('/api/v1/qualification-review', 'qualification-fence', 'release', cell='cell/a', id=review),
              lambda value:value['context_current'] and value['fences_confirmed'], 'qualification-fences')
write(OUT/'qualification-fenced.json', detail)
overview = get('/api/v1/overview', 'qualification-overview')
main = cell(overview)
host_status = {name:json.loads(docker(['exec',container,'cat','/run/rx-host/host-status.json'], name+'-status'))
               for name,container in INFO['hosts'].items()}
journals = {name:json.loads(docker(['exec',container,'cat','/data/host/installation.json'], name+'-journal'))
            for name,container in INFO['hosts'].items()}
effects = docker(['exec',INFO['hosts']['hb'],'/bin/sh','-c',
                  'if test -f /data/workflow-simulation/effects.jsonl; then cat /data/workflow-simulation/effects.jsonl; fi'], 'effects-before-run')
negative = get('/api/v1/cell', 'physical-negative-context', 'operator', id='cell/physical-unconfigured')
config = negative['value']['configuration']
negative_run = mutation('/api/v1/runs', {'cell':config['id'], 'recipe_digest':config['recipe']['sha256'],
                        'site_config_digest':config['site_config_digest'], 'expected_cell':negative['revision']}, 'physical-negative-create-2', 'operator')
blocked = get('/api/v1/run/start-context', 'physical-negative-start-context', 'operator',
              cell=config['id'], run=negative_run['id'], purpose='PRODUCTION', budget_limit='1')
denial_body = {'request_key':str(uuid.uuid4()), 'command':blocked['request']}
write(OUT/'physical-negative-start.json', denial_body)
denied = command(['python3',str(ROOT/'installed-client/rx'),'api','--connection',str(SITE/'connections/operator.json'),
                  '--state-dir',str(SITE/'api-client'),'post','/api/v1/runs/start','--body',str(OUT/'physical-negative-start.json')], 'physical-negative-start', check=False)
role_denied = command(['python3',str(ROOT/'installed-client/rx'),'api','--connection',str(SITE/'connections/operator.json'),
                       'get','/api/v1/package-intake-context?cell=cell%2Fa'], 'operator-intake-denied', check=False)
identities = {role:get('/api/v1/overview','role-'+role,role)['user']['principal'] for role in ['engineer','verifier','release']}
recovery = {}
for file in ['host-recovery.log','executor-recovery.log','executor-identity.log','external-process.log']:
    result = installed('cat',['/opt/rx/bin/'+file], 'sealed-'+file)
    recovery[file] = {'sha256':hashlib.sha256(result.stdout.encode()).hexdigest(),'text':result.stdout}
software = read(OUT/'software-result.json'); applied = read(OUT/'applied.json')
limitations = ['Automated distinct-role SIM normal-path precheck, not independent human acceptance.',
               'No fresh gripper support observation; unclamp uses same-Part settled/successful acquire-support ordering only.',
               'CP3 external adapter failure/restart and negative pre-completion kill have not been exercised.',
               'Sealed recovery logs establish the named generic core controls, not S1 fault-run qualification or physical safety.']
observations = {
 'SOFTWARE':{'assertions':{'actual_signed_compile_review_passed':software['compiler_checks_passed'],
              'exact_target_applied':applied['change']['after']==read(ROOT/'process/configuration.json')['configuration']},
              'observations':{'compiler':software,'application':applied['change']['application']},'limitations':limitations},
 'EQUIPMENT':{'assertions':{'two_hosts':len(host_status)==2,'unarmed':all(s['phase']=='SOFTWARE_READY_UNARMED' for s in host_status.values()),
               'sources_current':bool(main['diagnostics']['sources']) and all(s['usable'] for s in main['diagnostics']['sources']),
               'same_clock':all(s['clock_id']==overview['installation']['clock_id'] for s in host_status.values())},
               'observations':{'hosts':host_status,'journals':journals,'diagnostics':main['diagnostics']},'limitations':limitations},
 'CELL_INTEGRATION':{'assertions':{'applied_unqualified':applied['change']['state']=='APPLIED_UNQUALIFIED',
                     'two_host_proofs':len(applied['change']['application']['host_proofs'])==2,
                     'configuration_acked':read(OUT/'before-apply.json')['host_configuration']['all_hosts_acknowledged'],
                     'current_fences':detail['context_current'] and detail['fences_confirmed']},
                     'observations':{'application':applied['change']['application'],'review':detail},'limitations':limitations},
 'RECOVERY':{'assertions':{'exact_sealed_controls_passed':all('1 passed; 0 failed' in item['text'] for item in recovery.values()),
              'journals_available':len(journals)==2},'observations':{'sealed_logs':recovery,'b1':read(ARTIFACTS/'B1.json'),'journals':journals},'limitations':limitations},
 'PROTECTION':{'assertions':{'unconfigured_physical_denied':not blocked['can_request'] and blocked['blocking_reason']=='NOT_COMMISSIONED',
                'actual_start_denied':denied.returncode==1 and 'P rejected request' in denied.stderr},
                'observations':{'context':blocked,'denial':denied.stderr},'limitations':limitations},
 'OPERATIONS':{'assertions':{'separate_role_principals':len(set(identities.values()))==3,
                'operator_denied':role_denied.returncode==1 and 'HTTP 403' in role_denied.stderr,
                'zero_main_runs':not main['runs'],'zero_native_effects':not effects.strip()},
                'observations':{'principals':identities,'operator_denial':role_denied.stderr,'main_runs':main['runs'],'effects':effects},'limitations':limitations},
}
write(OUT/'normal-observations.json', observations)
report = OUT/'qualification-report'
build(job, observations, ROOT/'qualification/artifacts', report)
installed('/usr/local/bin/rx-package-store', ['qualification-signing-request','/author/commission/qualification-report/qualification.json',
          'f2-qualification-signer','/author/commission/qualification-signing.json'], 'qualification-signing-request', role='platform')
sign(OUT/'qualification-signing.json', report/'qualification.sig.json', 'qualification')
upload = OUT/'qualification-upload'; upload.mkdir(); shutil.copytree(report,upload/'qualification-report')
put(INFO['volumes']['imports'],upload,'qualification-upload');owner([INFO['volumes']['imports']],'qualification-upload')
request_digest = read(OUT/'qualification-signing.json')['report_digest']
mutation('/api/v1/qualification-review/reports', {'cell':'cell/a','review':review,'directory':'qualification-report','expected':None,
         'report_digest':request_digest}, 'qualification-report')
detail = get('/api/v1/qualification-review','qualification-report-detail','verifier',cell='cell/a',id=review)
write(OUT/'qualification-report-detail.json',detail)
print('Measured report imported; review/activation remain separate.')
