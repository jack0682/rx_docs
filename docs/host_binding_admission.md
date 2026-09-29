# Host binding 교체의 P 진행 조건 설계

2026-09-29. 대상은 SIMULATION Host의 process-configuration binding 교체다. 이 문서는 [교체 확인 계약](host_binding_commit_observation.md)과 [Python 장비 스킬 초안](python_device_skill_draft.md)의 남은 연결을 단계별 조건으로 고정한다. 이 문서의 조건이 구현됐다고 해서 공정 적용, 자격 또는 실행 허가가 생기지는 않는다.

## 전체 순서

| 단계 | 행위자 | P가 요구하는 조건 | 상태 |
|---|---|---|---|
| S0 요청 발급 | ReleaseManager | STAGED 변경, 전체 Host 계획, 원 요청 ID 고정 | 구현 |
| S1 기준 수집 | P worker | 등록된 현재 Host 세대의 bounded read, 교체 전 cohort·설치 identity·두 저널 | 구현 |
| S2 준비·fence | ReleaseManager | 모든 계획 Host가 **BaselineCurrent**(기준이 현재 등록 세대의 것) 또는 **CommitCurrent** | 이번 구현 |
| S3 Host 정지·commit | Host 운영자 | fence 확인 뒤 정상 정지, 같은 요청 ID로 commit, 제안 구성으로 재기동 | 실제 이미지 시험 통과 |
| S4 교체 확인 | P worker | ReleaseManager의 binding 재수용 승인 → 새 boot가 변경 후 구성으로 link → 새 boot, 같은 두 저널, commit 요청/계획/구성/설치 identity 일치 → MetadataMatched | 실제 이미지 시험 통과 |
| S5 준비 갱신 | ReleaseManager | 재기동 뒤 이전 fence 확인은 옛 boot의 것이므로 refresh로 새 세대에 다시 fence | 실제 이미지 시험 통과 |
| S6 구성 전달 | P | 모든 계획 Host가 **CommitCurrent**, 확인이 현재 P runtime·현재 등록 세션의 것, 최종 재검증 | 실제 이미지 시험 통과 |
| S7 적용 | ReleaseManager | 기존 적용 조건 + Host의 정확한 commit 대상 수신 확인 | 미구현 |

## Standing

P는 변경마다 계획 Host별 standing을 원장과 현재 Host 등록에서 계산한다. 저장된 값이 아니라 조회 시점의 파생값이다.

- **BaselineRequired**: 이 P runtime에서 요청이 없거나 기준이 없다.
- **BaselineCurrent**: 기준의 host boot·delivery 저널이 모든 요청 셀에 현재 등록된 세대와 같고, 교체 확인은 없다.
- **CommitUnconfirmed**: 기준은 있으나 현재 등록 세대가 기준과 다르고, 현재 세대의 교체 확인이 없다. Host가 재기동 중이거나, 교체 없이 재시작했거나, 확인 전이다.
- **CommitCurrent**: MetadataMatched 관측의 boot·저널과 관측 세션이 현재 등록과 같다.

세대 판정은 요청의 모든 셀에서 같은 (session, boot, journal)을 요구한다. 셀마다 다르거나 등록이 없으면 현재 세대가 없다고 본다.

## 불변식

1. fence는 기준을 잡은 바로 그 Host 세대 또는 교체가 확인된 현재 세대에만 보낸다. 기준 없이 fence한 뒤 Host가 교체되면, 교체 전 상태를 P가 본 적이 없으므로 before 비교가 성립하지 않는다.
2. 교체 확인은 적용 허가가 아니다. S6 전까지 `HOST_BINDING_CHANGE_REQUIRED`와 구성 전달 barrier를 유지한다.
3. 옛 boot의 fence 확인·교체 확인은 새 boot의 증거가 아니다. Host가 다시 재기동하면 CommitCurrent는 CommitUnconfirmed로 내려간다.
4. transport 실패·거절은 기준이나 확인을 만들지 않고 이유를 기록한다.
5. 사용자 업로드 JSON은 어느 단계의 증거도 아니다.

## 변경 상세의 차단 항목

binding 계획이 있는 변경에는 `HOST_BINDING_CHANGE_REQUIRED`(적용 경로 미구현)를 계속 표시한다. 여기에 Host별로 `HOST_BINDING_BASELINE_REQUIRED` 또는 `HOST_BINDING_COMMIT_UNCONFIRMED`를 추가해 무엇이 빠졌는지 보인다. CommitCurrent인 Host에는 추가 항목이 없다.

## P 재시작 인수 (설계만)

현재 정책은 요청의 runtime_boot와 읽기 시점의 P runtime이 다르면 RuntimeChanged로 거절한다. 따라서 P가 재시작하면 기존 요청은 영구히 진행하지 못한다. 원 요청 ID를 바꾸지 않는 인수 규칙을 다음과 같이 제안한다.

- 인수는 ReleaseManager의 명시적 요청으로만 한다. 자동 인수하지 않는다.
- Host가 아직 교체되지 않았으면(현재 boot = 기준 boot, 같은 두 저널, 해당 요청의 commit 관측 없음) 새 runtime에서 기준을 다시 잡는다. 이전 기준은 이력으로 보존한다.
- Host가 이미 교체됐으면 기준을 새로 만들 수 없다. 원 기준과 현재 관측의 저널·설치 identity 연속성만으로 확인하며, 두 시점이 같은 clock 영역일 때만 시간 순서를 비교한다. 비교할 수 없으면 확인하지 않고 운영자 판단 항목으로 남긴다.
- 인수 전의 준비·fence는 PreparationStale이므로 refresh가 필요하다.

## 반례 시험 목록

- 기준 없이 준비 요청 → 거절, 준비 없음. (구현 시험)
- 기준 수집 뒤 준비 → fence가 현재 Host에 도달하고 확인됨, `HOST_BINDING_COMMIT_UNCONFIRMED` 표시, 구성 전달 거절. (구현 시험)
- 기준 수집 뒤 Host를 교체 없이 재시작 → CommitUnconfirmed, 준비 refresh 거절.
- commit 뒤 재기동 → MetadataMatched, CommitCurrent, refresh 허용, 구성 전달은 S6 전까지 거절.
- commit 확인 뒤 Host 재시작 → CommitUnconfirmed로 하강.
- P 재시작 → RuntimeChanged, 명시적 인수 전까지 진행 불가.

## S4 차단 원인과 결정 (2026-09-29)

S3–S5 실시간 시험을 준비하며 코드로 확인한 사실이다.

- P는 재기동한 Host(새 boot)를 같은 셀에 다시 등록하는 경로가 없다. host link 준비(`prepare_host_link`)와 등록 저장(`engine/configuration.rs`)은 기존 등록과 boot·세션이 다르면 `CONTINUITY_UNPROVEN`으로 거절한다("Do not silently turn a restarted Host into a prepared one"). 명시적 Host recovery도 같은 boot의 P↔Host 통신 복구만 다룬다. 이는 [핵심 미결](implementation/critical_open_items.md) O04(명시적 재개·새 운전 등록)의 현재 형태다.
- 재기동한 Host는 binding commit 뒤 변경 후 definition을 가지므로, 셀의 현재 구성과 같은 definition을 요구하는 등록 조건도 통과하지 못한다.
- 교체 확인(`observe_host_binding_intent`)은 현재 등록 세션을 요구하므로, 등록이 없으면 새 boot를 읽을 수 없다. 설계 표의 S4 조건은 이 전제를 빠뜨렸다.

사용자 결정: **전이 등록** 방향을 택했다. staged 변경의 변경 후 definition과 P가 발급한 요청과 일치하는 binding commit을 가진 Host만, 작업 권한 없이 등록한다. 기존 등록 규칙은 일반 경로에서 그대로 유지한다.

조사 결과 이 결정은 단독으로 구현할 수 없고 O04의 일부를 요구한다. 전이 등록이 되려면 먼저 "새 boot Host를 명시적 승인과 저널 연속성 증거로 재수용하는" 경로가 있어야 하며, binding 전이는 그 경로에서 definition 조건만 staged 변경의 변경 후 값으로 바꾼 변형이다. 또 S5(새 boot fence)와 S6(구성 전달)가 등록을 요구하므로 전이 등록은 관측 전용일 수 없고 fence와 구성 수신까지는 허용하되 작업 전달은 막아야 한다.

제안 순서: (1) 재기동 Host 재수용의 최소 규칙 정의 — ReleaseManager 승인, Host StopSeal과 delivery·evidence 저널 연속성, 이전 boot의 미결 작업 없음, 셀은 차단 유지 (2) 그 변형으로 binding 전이 등록 (3) S3–S5 실시간 시험.

## 재수용 구현과 남은 Host 쪽 차단 (2026-09-29)

- 재기동 Host 재수용(rx-platform 241c833): ReleaseManager가 교체될 세대(boot·delivery·evidence 저널)를 명시해 승인하면, 두 저널을 유지한 새 boot의 다음 link 하나가 셀마다 한 번 등록을 대체한다. 실행 중 Run이나 미결 작업이 있으면 승인하지 않는다. grant·Arm·자격·Run은 복구하지 않고 재기동 차단은 유지된다. `POST /api/v1/hosts/readmission`.
- binding 전이 등록(85d0218): 승인에 기준이 정확히 그 세대를 가리키는 binding intent를 묶으면, 새 boot는 staged 변경의 변경 후 구성을 제시할 수 있다. 증거 셀 협상·link 준비와 commit·grant 갱신이 그 구성과 대조하며, 변경이 staged를 벗어나면 현재 구성으로 돌아간다.
- standing은 등록이 Host의 현재 producer 세션·boot일 때만 현재로 본다. 이후 재기동은 이전 교체 확인을 하강시킨다.
- 엔진 시험 3개(승인 없는 재기동 거절, 역할·세대·저널 반례, 1회 소비, 같은 sequence 재사용 충돌, 없는 intent 거절)와 워크스페이스 437개 통과. binding 변형의 엔진 수준 시험은 없다(binding 계획이 있는 변경을 만드는 엔진 fixture가 없음).

실제 이미지 `--binding-commit` 시험의 첫 시도는 Host의 `prepare-binding-change`에서 멈췄다. 이때 "하위 디렉터리 적재 실패"와 "파일 수 8 제한"을 원인으로 추정했으나 **둘 다 틀렸다**(정정). 같은 이미지·볼륨에서 `rx-device-package verify`는 같은 package를 통과시켰고, 파일 수 검사는 manifest·서명을 제외하고 8개를 허용해 실제 package(8개)와 맞는다. 실제 원인은 다음 둘이었다.

1. 서명된 package의 profile이 Python 환경을 절대 경로(`/fixture/environment`)로 고정하는데, Host 컨테이너에 그 경로가 없었다. 설치 요구이며 시험 도구가 그 경로에 환경을 마운트한다. P 검증 정책의 asset 절대 경로도 같은 방식으로 Host 볼륨에 둔다.
2. 연결된 Host가 재기동하면 P 전체가 종료됐다. 새 producer 세션 때문에 link worker가 인증 거절을 받으면 service 실패로 처리됐다. 이제 producer 세션 교체를 구별해 오래된 worker만 내리고 재수용이 필요한 link 단계로 돌아간다(rx-platform cb45bb4). 다른 worker 실패는 여전히 runtime을 멈춘다.

이후 S3–S5와 재기동 반례가 실제 이미지에서 통과했다([검증 기록](../references/host_binding_commit_live_2026-09-29/README.md)).

## S6·S7 연결 (2026-09-29)

구성 전달과 적용의 차단을 "binding 계획이 있으면 거절"에서 "모든 계획 Host가 CommitCurrent가 아니면 거절"로 바꿨다(rx-platform 8eae0f1). CommitCurrent에서는 `HOST_BINDING_CHANGE_REQUIRED`도 사라진다. 적용 결과는 기존과 같이 APPLIED_UNQUALIFIED이며 자격은 별도다.

실패하거나 모순되는 읽기가 확인된 교체 기록을 BASELINE_RECORDED로 되돌리던 동작을 없앴다. 이유만 기록하고, standing은 transport 유실 외의 모순이면 확인을 철회한다. 이 되돌림 때문에 확인 뒤 재기동한 Host의 재수용이 간헐적으로 409로 실패했다(수정 전 3회 중 1회 관측). 재수용은 확인된 commit 세대도 교체 대상으로 받는다.

실제 이미지에서 확인 → 재기동 하강(refresh `CONTINUITY_UNPROVEN`, configure `CAPABILITY_MISSING`) → 확인된 세대 재수용 → 재확인 → refresh·fence → configure-hosts(Host `APPLIED_UNQUALIFIED`) → apply(`APPLIED_UNQUALIFIED`, 셀 구성 = 변경 후 구성, 남은 blocker `REQUALIFICATION_REQUIRED`)를 5회 연속 통과했다. [검증 기록](../references/host_binding_apply_live_2026-09-29/README.md).

남은 것: P 재시작 뒤 요청 인수(현재는 RUNTIME_CHANGED로 진행 불가), 자격 활성화와 Python 스킬 실행 연결, commit 전 교체 없는 재시작의 단독 시험.
