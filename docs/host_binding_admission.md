# Host binding 교체의 P 진행 조건 설계

2026-09-29. 대상은 SIMULATION Host의 process-configuration binding 교체다. 이 문서는 [교체 확인 계약](host_binding_commit_observation.md)과 [Python 장비 스킬 초안](python_device_skill_draft.md)의 남은 연결을 단계별 조건으로 고정한다. 이 문서의 조건이 구현됐다고 해서 공정 적용, 자격 또는 실행 허가가 생기지는 않는다.

## 전체 순서

| 단계 | 행위자 | P가 요구하는 조건 | 상태 |
|---|---|---|---|
| S0 요청 발급 | ReleaseManager | STAGED 변경, 전체 Host 계획, 원 요청 ID 고정 | 구현 |
| S1 기준 수집 | P worker | 등록된 현재 Host 세대의 bounded read, 교체 전 cohort·설치 identity·두 저널 | 구현 |
| S2 준비·fence | ReleaseManager | 모든 계획 Host가 **BaselineCurrent**(기준이 현재 등록 세대의 것) 또는 **CommitCurrent** | 이번 구현 |
| S3 Host 정지·commit | Host 운영자 | fence 확인 뒤 정상 정지, 같은 요청 ID로 commit, 제안 구성으로 재기동 | Host 구현, P 연동 시험 미완 |
| S4 교체 확인 | P worker | 새 boot, 같은 두 저널, commit 요청/계획/구성/설치 identity 일치 → MetadataMatched | **차단: 재기동 Host 재수용 경로 없음(아래)** |
| S5 준비 갱신 | ReleaseManager | 재기동 뒤 이전 fence 확인은 옛 boot의 것이므로 refresh로 새 세대에 다시 fence | 기존 경로 재사용, 시험 미완 |
| S6 구성 전달 | P | 모든 계획 Host가 **CommitCurrent**, 확인이 현재 P runtime·현재 등록 세션의 것, 최종 재검증 | 미구현 (barrier 유지) |
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
