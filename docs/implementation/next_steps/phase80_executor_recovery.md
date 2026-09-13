# phase80 / P03 — Executor 미완료 기록의 명시적 회수 경계

2026-09-13 읽기 전용 설계. 이 문서만 작성하며 제품·시험 소스 수정, 빌드, 시험, 서버 기동은 하지 않았다. 아래 모듈·명령 이름은 제안이다.

## 먼저 확정할 결론

가장 작은 다음 단위는 **원래 attachment/stop/request 원장을 고치지 않고, 명시적으로 등록한 현재 E 세션으로 원래 Run의 제한 상태와 기존 mapping을 읽어 별도 검토 기록에 보존하는 기능**이다. CellService의 실행 복구나 같은 Run 재개가 아니다.

두 행위를 반드시 나눈다.

1. **로컬 검토:** ServiceOwner 아래 required-open한 S 원장·원래 stop/request를 읽는다. Session.Open을 하지 않으므로 P 상태 변경이 없다.
2. **현재 등록 후 회수:** 명시적인 새 E 세션 등록을 한 뒤, 이미 있는 P 읽기 API로 원래 Run을 조회한다. 조회는 읽기이지만 **등록은 P mutation**이다. 현재 `OpenExecutorPeer`는 이전 peer/session이 있으면 AUTHORITY_REVOKED closure를 기록하므로 cell revision/epoch/block이 바뀐다. 이 사실을 숨기는 `inspect` 자동 handshake는 제공하지 않는다.

phase79의 `old session UNAUTHENTICATED → PENDING stop 보존 → ATTENTION/exit 1`은 정상의도이며 그대로 둔다. 새 기능의 성공은 “현재 관측과 원래 기록의 대조를 저장함”이다. 원래 stop이 성공했고 planner 정리가 증명됐으며 다음 Run을 받을 수 있다는 뜻이 아니다.

## 실제 기준 사례

[phase79 known-query 결과](/Users/ojaehong/RX_automation/rx_ws/references/implementation/phase79-host-recovery-known-attention/result.json)는 다음을 보존한다.

- E attachment와 원래 Run ID가 남고 `completed_runs=0`, 최종 CellService=ATTENTION이다.
- stop은 WORKER_FAULT/PENDING, `attempts=[]`, `observation=null`, durability fault 없음, last_error는 UNAUTHENTICATED다. 실제 P PauseRun 진입 전에 인증 읽기가 실패했다.
- E exit=1이다. Host의 원 invocation 결과는 회수됐지만 signed process의 후조건·permit/cell 연속성 상실 때문에 P 전체 operation은 UNKNOWN/NONE을 유지한다.

따라서 native capture 존재를 근거로 CompletePart, Run COMPLETED, stop Reply, 정상 attachment close를 만들어서는 안 된다.

## 기존 규범과 현재 구현

| 근거 | 요구와 설계 결과 |
|---|---|
| [base 영속성 §2](/Users/ojaehong/RX_automation/rx_ws/rx-platform/spec/contracts/v1.0/02_identity_durability_recovery.md:42) | 멈춘 Run의 기존 key/결과 회수는 허용하지만 미사용 slot을 새 operation으로 만들지 않는다. Pause는 진입한 native 작업 취소가 아니다. |
| [base executor 세대](/Users/ojaehong/RX_automation/rx_ws/rx-platform/spec/contracts/v1.0/02_identity_durability_recovery.md:44) | Run의 executor Session이 실행 권한 세대다. 새 세션 자체로 기존 Run을 재개하지 않는다. |
| [base 재시작 표](/Users/ojaehong/RX_automation/rx_ws/rx-platform/spec/contracts/v1.0/02_identity_durability_recovery.md:109) | P restart 후 원 operation ID·checkpoint·activation-slot을 회수한다. E의 메모리 tick/promise를 복원하거나 새 ID로 재발행하지 않는다. |
| [cell 권한 철회](/Users/ojaehong/RX_automation/rx_ws/rx-platform/spec/cell_operations/v1.0/02_authorization_invalidation.md:35) | P/H/E restart와 owner 변경은 일반 transient 복원이 아니다. LATCHED 제한·무효 permit/mandate를 조건 회복만으로 살리지 않는다. |
| [cell 읽기 경계](/Users/ojaehong/RX_automation/rx_ws/rx-platform/spec/cell_operations/v1.0/02_authorization_invalidation.md:100) | 읽기는 motion permit를 요구하지 않지만 접근권은 검사한다. 이 기능은 여기까지다. |
| [cell Restart 준비/새 시작](/Users/ojaehong/RX_automation/rx_ws/rx-platform/spec/cell_operations/v1.0/02_authorization_invalidation.md:17), [restart sequence](/Users/ojaehong/RX_automation/rx_ws/rx-platform/spec/cell_operations/v1.0/04_protocol_integration_ui.md:118) | 정상 재개는 별도 PrepareRestart·현재 조건/clearance·OPERATOR 새 의도·같은 epoch Arm ACK·새 mandate commit을 요구한다. 검토 기록으로 이를 대체하지 않는다. |
| [복구/비운전 종료](/Users/ojaehong/RX_automation/rx_ws/rx-platform/spec/cell_operations/v1.0/03_intervention_recovery_change.md:40), [종료 구별](/Users/ojaehong/RX_automation/rx_ws/rx-platform/spec/cell_operations/v1.0/03_intervention_recovery_change.md:88) | 원 invocation 결과 조회, 실제 복구 operation, case 비운전 종료, 생산 재개는 서로 다르다. 본 기능은 현장 처분/접근/clearance를 발급하지 않는다. |

현재 빈자리는 주로 S에 있다.

- [P executor_scope](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/executor_peer.rs:220)는 현재 인증 peer/셀 협상/설정된 executor를 확인한다. 읽기에서 과거 Run의 executor_session과 caller 일치를 요구하지 않는다.
- [Production.Inspect](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/production.rs:6)는 같은 cut의 current caller/runtime/epoch/Run/part/checkpoint를 반환하며, 실행 권한이 없으면 admission=false로 읽을 수 있다. [Workflow.GetRun](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-api/src/grpc/workflow.rs:4)과 [ExecutorWork/Operation.Get](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/executor_requests.rs:193)도 기존 자료 회수에 쓸 수 있다.
- S [Client::production_view](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/runtime/rx-executor/src/client/production.rs:80)는 새 Client의 현재 P cut을 검증할 수 있다. 그러나 [CellService::poll](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/runtime/rx-executor/src/cell_service.rs:173)과 [check_existing](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/runtime/rx-executor/src/cell_service/policy.rs:182)은 실행용 경계라서 원래 세션/runtime/epoch와 현재 EXECUTING admission을 요구한다. 이 검사를 완화해서 회수에 쓰면 안 된다.
- [Worker::stop_once](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/runtime/rx-executor/src/worker/lifecycle.rs:65)는 restricted Run을 먼저 관측하면 PauseObserved로 기록할 수 있다. 그러나 이것은 기존 stop 서비스 경로이고, [stop journal](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/runtime/rx-executor/src/journal/lifecycle.rs:138)은 원 id/reason/session/history와 terminal stop의 불변성을 지킨다. 새 recovery reader가 old stop을 새 세션의 정상 성공처럼 덮어쓰지 않는다.
- [AssignmentJournal required-open](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/runtime/rx-executor/src/assignment_journal/run_store.rs:33)은 기존 header/creation entry를 검증한다. `attach()`는 Preparing을 Attached로 올리므로 회수 조회에서 호출하지 않는다. 일반 `Journal::open`의 header 자동 초기화도 회수 경로에 사용하지 않는다.
- Journal의 전체 attempt 열람은 현재 `test_attempts`가 test-harness에만 있다. 제품용 bounded audit API가 필요하다. 기존 Entry의 key/body/context/send/resolution을 그대로 읽어야 한다.
- [Operation.Lookup](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-api/src/grpc/operation.rs:46)은 이 binding에서 미구현이다. BeginPart/CompletePart/Pause 등 모든 mutation의 exact saved response를 읽는 전용 API도 없다. 현재 mapping 관측을 원 RPC Reply로 바꾸면 안 된다.

## Session.Open은 검토 조회와 다른 변경이다

[OpenExecutorPeer](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/executor_peer.rs:53)는 이전 활성 세션을 retire하고, 이전 peer가 있으면 구성된 관련 셀을 AUTHORITY_REVOKED로 invalidate한다. 새 session은 Run.executor_session을 새 값으로 덮어쓰지 않지만, cell cut은 바뀔 수 있다.

따라서 초기 최소 지원은 **확인된 이전 E 프로세스 종료 + 한 service root + 동일 배포 principal/credential/release/definition/installation/store + 같은 kernel clock의 P-only restart**로 한정한다. ServiceOwner는 로컬 동시 소유를 막지만 같은 principal을 쓰는 다른 root를 P 전체에서 배제하지 않는다. 다른 현재 E owner/배포가 있거나 교체 영향이 불명확하면 등록하지 않고 별도 조정으로 남긴다. 현재 Session.Open에 expected-old-session CAS가 없으므로 이를 전역 non-preemption 보장이라고 쓰면 안 된다.

순서는 `old E exit/원장 검토 → 명시 새 E 등록 → 현재 P cut 재조회 → 필요한 Host recovery/revalidation 검토·승인`이다. E 등록을 기존 HostRecovery 승인 뒤에 하면 epoch/block/cell revision이 달라져 승인 binding이 stale해질 수 있다. 기존 승인을 자동 adopt하거나 그 불일치를 무시하지 않는다. E용 AUTHORITY_REVOKED를 P-only라며 자동 생략하는 변경도 이 단위에 넣지 않는다.

한 실행 중 reader는 같은 Client/session을 유지한다. UNAUTHENTICATED/P runtime 재변경이면 종료하여 Attention을 남기며 자동 Session.Open loop를 돌리지 않는다. 매 조회마다 새 peer boot/session을 만들지 않는다. 새 프로세스는 과거 boot를 재사용하지 않는다.

## 최소 모듈과 CLI 제안

| 파일/모듈 제안 | 최소 책임 |
|---|---|
| S `runtime/rx-executor/src/recovery.rs` | 이미 현재인 Client를 받는 별도 RecoveryReader. 원래 current attachment 하나만 대상으로 P 자료를 수집하고 대조한다. PlannerFactory/EngineProcess/Worker/RunService/PendingRequests를 갖지 않는다. |
| S `src/journal/recovery.rs` + required-open helper | 기존 Scope/header/attempt/index/stop의 bounded read/audit. 생성·prepare·enter·reply 함수를 호출하지 않는다. |
| S `src/assignment_journal/recovery.rs` | `recovery-review/...` 별도 namespace의 idempotent 검토 기록. 원 Preparing/Attached/current pointer/creation-entered/stop/request를 바꾸지 않는다. |
| S `src/client/recovery.rs` | 필요한 기존 읽기 RPC만 감싼 좁은 facade. Client::emit, PauseRun, CompletePart, Operation.Reconcile 등을 노출하지 않는다. immutable process를 검증용으로 읽을 수 있지만 BT XML/plan frame 생성이나 tick은 없다. |
| S `src/bin/service/recovery_cli.rs` | 아래 명령과 root owner/배포 파일 검증·명시 session 등록을 조합한다. 기존 `cell run`과 old CONFIG 동작은 유지한다. |

제안 명령은 두 가지다(아직 존재하지 않음).

- `rx-executor-service cell recovery-inspect CONFIG`: 네트워크 없이 current attachment, required files, 원 stop/attempt의 digest와 미해결 상태를 출력한다.
- `rx-executor-service cell recovery-collect CONFIG --expected-attachment ID --expected-local-digest DIGEST --review-key UUID`: 위 원장과 expected digest를 다시 검사한 뒤 **새 현재 E 등록을 명시적으로 수행**하고 원 Run 읽기·검토 기록 저장까지만 한다. 이 명령을 “생산 재개/연결 복원 완료”로 표시하지 않는다.

새 Session.Open 전 local required-open 실패를 먼저 처리한다. 손상·누락·다른 Scope면 connect하지 않는다. Preparing에 creation entry가 없고 file도 없으면 그 예약을 그대로 보고할 수 있으나 run file을 생성하지 않는다. creation-entered 뒤 파일/헤더가 없으면 Attention이다.

RecoveryReader의 RPC 허용 목록은 Production.Inspect, Workflow.GetRun, ExecutorRead.GetArtifact/GetSnapshot, 필요한 기존 Operation.Get뿐이다. target Run은 원장의 current preparation에서 정한다. 발견된 새 B를 선택하거나 mutation 재호출로 saved response를 찾지 않는다. BeginPart/CompletePart/ResolveActivation/Submit/Checkpoint/Pause/Operation.Reconcile/Start는 **0회**다.

초기 단위는 P wire/규범 변경 없이 가능하다. exact mutation Reply가 필요한 후속 단계에서는 별도의 read-only key/method/body-bound lookup binding을 검토한다. 그것이 없다는 이유로 같은 mutation을 replay하지 않는다. 새 일반 세션 등록이 다른 현재 owner를 철회하지 않는다는 P 차원의 보장이 필요해지는 경우에도 별도 expected-peer/CAS 등록 경계가 선행해야 한다. 둘 다 이번 최소 회수에 몰래 포함하지 않는다.

## 검토 기록과 대조 기준

별도 `RecoveryReview`에는 다음을 고정한다.

- review key, 원 service journal identity/config digest, attachment ID/revision/Preparation digest, 원 Scope·run journal ID, 원 stop ID/revision/digest 및 원 Entry들의 key/body digest/send/resolution.
- **원 owner:** preparation의 executor_session/runtime/epoch 및 Entry context. 그대로 보존한다.
- **현재 reader:** 새 peer boot/session, pinned principal/credential 설정의 digest, P runtime/cut/checked_at/valid_until. 원 owner와 별도 필드다.
- 원 Run의 현재 state/executor_session/recipe/checkpoint, part ID/ordinal/budget, 원 activation/node/slot/operation의 현재 관측, 해석되지 않은 기록과 이유.
- `execution_authorized=false`, `reattached=false`, `attachment_closed=false`, `original_stop_preserved=true` 및 planner cleanup 근거의 유무.

RunResponse만 저장하면 reader session/runtime/유효기간이 없으므로 fresh 검토 근거가 되지 않는다. fresh Production/Snapshot envelope와 source cut을 함께 저장한다. 여러 read를 하나의 atomic cut이라고 하지 않는다. 공통 run revision/checkpoint가 바뀌면 bounded 재조회하거나 stale review로 실패한다. runtime이 다르면 old/new sequence 숫자를 같은 시간축으로 비교하지 않으며 새 Client 안에서는 기존 단조 검증을 유지한다.

현재 Operation.Get 응답에도 P runtime/sequence/checked_at envelope가 없다. 이를 쓰면 진단 조회로 구별하며 로컬 수신 시각을 P의 source freshness로 포장하지 않는다. 현재 cut이 필요한 원 slot/operation 관계는 기존 검증된 ExecutionSnapshot을 우선 사용한다. Session.Open 응답 유실은 등록이 없었다는 증거가 아니므로 시도/불확실성을 별도 기록하고 자동 재등록으로 감추지 않는다.

현재 mapping에서 원 part/operation을 찾으면 `EFFECT_OR_MAPPING_OBSERVED`라는 별도 관측으로 기록할 수 있다. 해당 원 request의 `Reply` 또는 `EmitEntered` 사실을 다시 쓰지 않는다. 찾지 못하면 NOT_FOUND/UNPROVEN이며 “요청은 전달되지 않았다”라고 추정하지 않는다. branch/wait/checkpoint의 이미 기록된 결정을 재평가하지 않는다.

P Run이 PAUSED/RECOVERY_REQUIRED이면 `CURRENT_RESTRICTION_OBSERVED`를 남긴다. 이는 old Pending Pause가 ACK됐다는 의미가 아니다. COMPLETED/ABANDONED를 읽어도 현재 CellService의 정상 close 규칙을 우회하지 않는다. old stop이 Attention이면 terminal 원문을 그대로 둔다. old stop이 Pending이어도 첫 단위에서는 원문을 보존하고 새 관측만 링크한다. 데이터 조회 성공과 원래 정지 요청의 완료는 서로 다른 축이다.

새 reader는 planner를 생성하지 않으므로 자신의 `NotStarted`를 과거 planner의 cleanup proof로 사용하지 않는다. 기존 process exit는 liveness 관측이며 과거 RunService의 CLOSE/child-exit 확인과 같다고 단정하지 않는다. 필요한 역사적 cleanup 근거가 없으면 “미확인”으로 남긴다.

입력/출력 record 수·byte 상한, 반복 수·RPC deadline을 둔다. 기존 Repository scan이 전체 결과를 materialize하는 구간은 payload 개수 거부만으로 메모리 상한이 증명됐다고 쓰지 않는다. 상한 초과/불완전 audit에서 reviewed-complete를 만들지 않는다. local commit 실패·응답 유실은 같은 review key+같은 immutable body만 회수한다. 이 commit은 S 검토 기록 하나이며 P/H/S의 분산 transaction이 아니다.

## 선택 가능한 후속 처리 — 이번 단위가 하지 않는 일

| 관측/행위 | 이번 회수 결과 | 별도 근거가 필요한 일 |
|---|---|---|
| 현재 P에서 old Run 제한을 확인 | 원 Pending/Attention stop을 보존한 검토 기록 | 원 Pause ACK 여부 확인/역사적 stop 상태 전이 |
| 원 operation 결과·mapping 확인 | 새 ID 없이 기존 사실 표시 | 실제 UNKNOWN 처분·후조건·handover/자원 해제·CompletePart |
| 기존 attachment를 검토함 | current pointer/Preparing/Attached 그대로 | 비운전 attachment retire 또는 다음 Run 수용을 여는 별도 명시적 절차 |
| 새 current E 세션 등록 | 현재 인증 읽기 가능, 이전 권한 철회 유지 | old Run executor owner 변경, 새 mandate/continuation·planner 시작 |
| 정상 운전 재개 | 미구현/허용 안 함 | 규범 PrepareRestart→clearance→OPERATOR RestartRun→Arm ACK→새 mandate, 예산/part/원 activation 연속성 |

현재 [operator Start](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/operator_start.rs:43)는 PREPARED만 받으며 [Cell PrepareRestart/RestartRun gRPC](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-api/src/grpc/cell_negotiation.rs:500)는 미구현이다. base 문서의 “명시 StartRun으로 새 session 연결”을 현재 StartRun에 PAUSED run을 넣어도 된다는 뜻으로 읽지 않는다. 셀 규범의 별도 Restart 계약을 구현해야 한다. 원 run limit/소비/part를 reset하거나 새 Run 생성으로 잔류 제한을 피하지 않는다.

## 최소 실제 인수

1. [현재 known-query driver](/Users/ojaehong/RX_automation/rx_ws/rx-platform/tools/test_host_recovery_known.py:510)의 E ATTENTION/PENDING/exit1을 계속 인수한다. 종료 전에 원 E volume을 보존하고 root/header/attachment/stop/request digest를 수집한다. DB writer seed는 금지한다.
2. 실제 E binary의 `recovery-inspect`를 같은 root에서 실행한다. P peer/session/cell epoch/block, native SUBMIT/LOOKUP, H evidence 수가 모두 안 바뀌는지 확인한다. 손상/누락/다른 identity에서는 Session.Open 0회다.
3. explicit `recovery-collect`를 실행한다. 새 E session 등록의 실제 AUTHORITY_REVOKED/epoch 변경을 별도로 기록하고 old Run executor_session은 바뀌지 않는지 확인한다. 그 뒤 같은 세션의 반복 P 읽기는 새 epoch/세션을 만들지 않아야 한다.
4. 현재 restricted old Run과 원 operation/part/checkpoint를 새 인증 세션으로 읽고 검토 원장에 commit한다. old stop Pending/attempts/원래 reason, request key/body/context, current attachment 원문은 byte-identical이어야 한다. BT spawn/step, 기존 업무 mutation, native submit/lookup은 0회다.
5. duplicate review key 회수, 다른 body 충돌, record commit 전/후 중단, P 재시작/세션변경/시각만료/sequence후퇴/recipe변경을 거부하는 반례를 둔다. 현재 restriction 관측을 old Pause reply나 정상 close로 바꾸지 않는지 검사한다.
6. 원 A 원장과 P의 독립 B/다른 current owner가 있는 반례에서는 B를 선택하거나 자동 등록으로 preempt하지 않는다. 현재 handshake의 전역 CAS 공백 때문에 안전한 배포 소유를 입증할 수 없는 구성은 지원 밖/Attention으로 남긴다.
7. HostRecovery 승인 전후에 E 등록을 교차시킨 실제 시험으로 stale context를 확인한다. E 등록 후 새 Host context 검토/명시 승인을 요구하며 기존 승인을 조용히 갱신하지 않는다.

회수 명령의 성공 출력은 “원래 미완료 기록 검토 저장됨; attachment/stop 보존; 운전 미허가”로 한다. 기존 daemon의 ATTENTION 또는 실패 exit를 소급해 정상 종료로 고치지 않는다. 정상 운전 재개 및 비운전 attachment retire는 다음 명시적 구현 단위로 남긴다.
