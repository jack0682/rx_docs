import hashlib,json,shutil,uuid
from types import SimpleNamespace
from commands import ROOT,ARTIFACTS,IMAGES,command,installed,read,write
from installation import SITE,put,owner,docker
from api import get,mutation
from commission_process import OUT,INFO,wait,cell
from normal_evidence import build
from sign import sign
job=read(OUT/'qualification-job.json');review=job['request']['id']
detail=read(OUT/'qualification-fenced.json')
overview=read(ROOT/'logs/qualification-overview.stdout');main=cell(overview)
host_status={name:read(ROOT/'logs'/(name+'-status.stdout')) for name in ['ha','hb']}
journals={name:read(ROOT/'logs'/(name+'-journal.stdout')) for name in ['ha','hb']}
effects=(ROOT/'logs/effects-before-run.stdout').read_text()
blocked=read(ROOT/'logs/physical-negative-start-context.stdout')
denied=SimpleNamespace(returncode=1,stderr=(ROOT/'logs/physical-negative-start.stderr').read_text())
role_denied=SimpleNamespace(returncode=1,stderr=(ROOT/'logs/operator-intake-denied.stderr').read_text())
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
