# phase75 검토 — 셀 단위 영속 Executor 배정 서비스

검토 기준: 2026-09-13 현재 workspace의 `rx-solutions/runtime/rx-executor`, P의 executor/production binding 및 writer 구현. phase74 service-root ownership 변경을 포함해 읽었으며, 이번 작업은 제품 소스·계약 수정이나 빌드·시험 실행을 하지 않았다. 아래 타입명과 상태명은 구현 제안이며 확정된 wire 계약이 아니다.

## 1. 최소 제품 경로와 범위

기존 `RunService` 위에 **한 service root의 영속 실행 연결을 관리하는 CellService**를 둔다. 제품의 직렬 생산 모드에서는 고정 `config.run/visit`을 없애고, 현재 인증된 P의 셀 조회에서 발견한 run을 검증한 뒤 기존 `SerialProduction`에 연결한다. 서비스 프로세스는 run 완료 후에도 같은 peer boot/session으로 다음 배정을 기다린다. S가 StartRun·RunMandate·operation 결과를 생성하거나 P DB를 직접 읽는 경로는 추가하지 않는다.

이 단계의 “하나”는 **한 S service root가 동시에 소유하는 RunService 인스턴스 하나**다. 플랫폼 전체의 한 셀 한 Run 불변조건이나 여러 run/scope의 동시성 제한이 아니다. 새 배정 조회는 기존 `Run.executor_session`, mandate, StartAttempt의 실제 관계를 읽는 기능이다. 읽기 응답으로 새 exclusive assignment를 만들거나 미래의 독점성을 보장하지 않는다.

현재 frozen base I05는 동일 충돌 자원의 command owner 최대 하나를 규정한다. cell 규범은 의존 관계가 입증된 다른 run/scope를 국소 사건만으로 중단하지 않는다고 명시한다. P StartRun도 다른 purpose의 EXECUTING run만 거부한다. 따라서 전역 단일 Run 정책을 몰래 추가해서는 안 된다. 기존 A가 실행 중인 뒤 최신 cell revision으로 같은-purpose B를 Start하는 경우는 현 구조에서 금지되지 않는다. 동일 cut의 경쟁 ARMING은 첫 Arm 완료가 cell revision을 올려 상대 attempt를 거부하지만 이 순차 사례까지 막지는 않는다.

근거: [base I05](/Users/ojaehong/RX_automation/rx_ws/rx-platform/spec/contracts/v1.0/01_responsibility_and_semantics.md:124), [cell scope 규범](/Users/ojaehong/RX_automation/rx_ws/rx-platform/spec/cell_operations/v1.0/02_authorization_invalidation.md:9), [StartRun 목적 검사](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/workflow.rs:113), [Arm 완료](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/workflow.rs:267).

## 2. 재사용할 코드와 현재 빠진 경계

| 현재 코드 | 재사용 및 필요한 변경 |
|---|---|
| `src/bin/service.rs` Config/run | 현재는 run/visit을 설정에서 읽고 한 번만 연결한다. 셀 서비스 모드에서는 journal root·서비스 원장 identity·PeerPin·고정 engine pin으로 대체한다. 기존 수동 visit 모드는 별도 명시 모드로 유지할 수 있다. |
| `service_owner::ServiceOwner` | Session.Open 전 root 잠금과 Drop unlock을 그대로 재사용한다. 서로 다른 root의 정상 서비스는 독립적이다. 셀 원장 필수 재열기까지 접속 전에 끝내야, 손상된 root의 기동 실패가 기존 P peer를 먼저 철회하지 않는다. |
| `RunService` | BT context·통신 grace·일반 요청 동결·stop lifecycle을 유지한다. `run(self) -> Report`가 Worker/Client를 소비하므로 내부 실행 완료 시 Client와 planner factory를 돌려주는 경계를 추가한다. 다음 run마다 새 Client::connect/peer 등록을 하지 않는다. 기존 run-only API는 wrapper로 유지 가능하다. |
| `Worker::coordinate` | 기존 IN_PROGRESS part 회수, BeginPart/CompletePart journal, P frontier 확인과 CompletedVisit retire를 재사용한다. 직렬 서비스가 여러 IN_PROGRESS part를 받으면 `.find(first)`로 고르지 않고 Attention을 반환한다. 이는 S 직렬 모드의 지원 범위 검사이며 P의 part 동시성을 제한하지 않는다. |
| `Client::production_view`, `snapshot`, `restore` | hash/size/schema, caller/installation/store/runtime, 시계·sequence·유효기간, checkpoint/resolved 공정 검증을 재사용한다. 조회 성공은 권한이 아니며 worker는 계속 현재 admission/mandate를 검사한다. |
| `Journal::Scope`, stop journal | run/resolved/installation/store/principal/release/cell/definition의 불변 결합을 유지한다. 기존 원장의 scope를 다음 run에 맞춰 다시 쓰지 않는다. stop intent는 첫 기록 보존 원칙을 유지한다. |

현재 `Cell.Inspect`는 셀 문맥만 반환하고 run ID를 공급하지 않는다. `Production.Inspect`는 `InspectRun { context, run_id, binding_hash }`이고 반환 `production::View`는 이미 알고 있는 run의 완전한 part 목록과 현재 control cut이다. `ExecutorRead.GetSnapshot`도 run과 visit이 필요하다. 따라서 이들만 연결해서는 새 StartRun을 발견할 수 없다.

근거: [CLI](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/runtime/rx-executor/src/bin/service.rs:19), [RunService](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/runtime/rx-executor/src/service.rs:188), [직렬 part 회수](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/runtime/rx-executor/src/worker/production.rs:81), [Client 검증](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/runtime/rx-executor/src/client/production.rs:88), [Scope](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/runtime/rx-executor/src/journal.rs:14), [실제 production proto](/Users/ojaehong/RX_automation/rx_ws/rx-platform/proto/rx/executor/production/v1/production.proto:8).

## 3. 필요한 P API 계약 — 조회 하나로 먼저 제한

기존 frozen base/cell 메시지를 바꾸지 않고, 별도 선택 binding에 `InspectCellAssignment` 읽기를 추가하는 안을 권고한다. 기존 production v1의 hash를 조용히 바꾸지 않는다. 새 version/hash와 생성 proto·shared DTO·SDK 사본을 같은 변경으로 검증한다.

요청은 `CallContext + cell_id + assignment binding_hash`다. request_key와 expected revision은 받지 않으며, run ID·visit·임의 파일 경로·callback URL·실행 명령은 받지 않는다. mTLS 인증, 현재 executor session, 셀 협상, `CellConfiguration.executor` 배정 검사는 기존 `validated_executor_identity`와 `executor_scope`를 재사용한다.

응답은 canonical ReadPayload이며 다음을 같은 `transact_at_control_cut`에서 만든다.

- 공통 cut: schema, installation, store_generation, runtime_boot, sequence, caller_session, cell, definition, configured executor, cell revision/epoch/scope epochs, checked_at, valid_until. 유효기간은 기존 production read와 동일한 최대 100ms 검증을 재사용한다.
- 결과: `NONE`, `SINGLE`, `AMBIGUOUS`를 명시한다. NONE/SINGLE은 후보 검사가 완전했음을 요구한다. 두 번째 후보가 발견되면 확인된 서로 다른 두 run witness로 AMBIGUOUS를 반환할 수 있다. 응답/scan 한도를 넘겼는데 완전성을 확인하지 못하면 RESOURCE_EXHAUSTED이고 NONE으로 바꾸지 않는다.
- SINGLE: run ID/revision/state/purpose, run의 resolved ArtifactRef, 현재 executor_session/mandate, 필요한 StartAttempt ID/status/owner session, 현재 configuration과의 일치 여부. run 전체 checkpoint/part는 중복해서 넣지 않고 다음 기존 Production.Inspect로 읽는다. 두 읽기 사이에 context가 바뀌면 새 상태를 다시 읽고 연결을 보류한다.

**후보 정의를 구현 전에 명시해야 한다.** 첫 보수적 규칙은 해당 셀에서 미완료인, 실제 시작 관계가 존재하는 run이다: pending StartAttempt가 있는 PREPARED, EXECUTING, 이미 시작했던 PAUSED/RECOVERY_REQUIRED를 포함한다. 아직 Start를 요청하지 않은 단순 PREPARED는 실행 배정이 아니다. 과거 session·만료 attempt·바뀐 공정·상실된 admission을 후보에서 숨기지 말고 조회/복구 대상임을 표시한다. 그렇지 않으면 재시작 후 옛 run이 보이지 않아 S가 새 run을 자동 선택할 수 있다. COMPLETED/ABANDONED 같은 종료 run은 신규 후보에서 제외하되, S가 보유한 기존 연결은 해당 ID의 직접 조회로 별도 정리한다. ABANDONED라는 표지만으로 미결 효과/자원 인계 완료를 만들지 않는다.

새 조회는 **선택 권위가 아니라 발견 근거**다. 미연결 root는 SINGLE인 production run만 실제 공정·원장과 대조해 연결한다. ARMING은 관측 대기이고 EXECUTING+현재 session+유효 admission 전에는 part/BT를 시작하지 않는다. AMBIGUOUS이면 최신 revision·UUID 순서·남은 예산·첫 목록 항목으로 고르지 않는다. 모호한 셀의 자동 분배가 필요해지면 별도의 P 소유 배정 정책/명시 선택 transaction이 후속이며, 이번 단계에 임의 전역 단일 Run 정책을 넣지 않는다.

반대로 이미 root가 A에 영속 연결된 상태에서 독립 B가 생겼다는 이유만으로 A/B를 일괄 pause하지 않는다. 기존 연결 A는 직접 읽은 현재 권한·공정·scope가 유효하면 계속 처리하고, 새 run 선택은 하지 않는다. S root 잠금은 P의 자원 reservation/fence를 대체하지 않는다.

근거: [P executor_scope](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/executor_peer.rs:220), [기존 control-cut read](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/production.rs:6), [production binding](/Users/ojaehong/RX_automation/rx_ws/rx-platform/spec/production/v1/README.md).

## 4. S 영속 연결과 원장 누락 처리

셀 서비스 root에는 서비스 원장 header와 `current attachment`를 둔다. header는 로컬 service journal identity, installation/store generation, principal/release, cell/definition에 고정한다. run별 기존 원장은 root 하위의 검증된 UUID 기반 경로에 보존한다. 파일 경로를 P 응답에서 받지 않는다. 연결 기록에는 run, 불변 Scope, per-run journal의 식별/예상 위치, 최초 P cut, 현재 처리 단계와 종료 근거를 남긴다. 매 poll을 원장에 적지 않고 연결/상태 전이만 기록한다.

서비스 원장은 사전 초기화 후 `run`에서 필수 재열기한다. 전체 root/header 유실을 새 설치와 구별하려면 배포 설정에 예상 service journal identity를 고정해야 한다. 파일이 없다는 이유로 서비스 기동 때 자동 새 header를 만들면 전체 원장 유실을 탐지할 수 없다. 기존 수동 run 원장은 확인된 Scope를 읽어 명시적 전환 절차로 등록하며, migration을 자동 운전 허가로 사용하지 않는다.

최초 run 연결은 `Preparing` 예약을 셀 원장에 먼저 기록하고, 고정 Scope의 새 run 원장을 준비한 뒤 `Attached`를 commit한다. **Attached commit 전에는 remote mutation/BT request를 내보내지 않는다.** 두 SQLite 원장을 하나의 transaction이라고 주장하지 않는다. Preparing 재기동은 정확한 예약과 staged header만 회수하고, 다른 파일을 덮어쓰지 않는다. Attached 이후 run 원장 누락·빈 header·다른 Scope·손상은 Attention으로 남긴다. 현재 `Journal::open`은 header가 없으면 생성하므로, 재열기 경로에서 이를 그대로 호출하지 말고 initialize/required-open을 구분해야 한다.

P SINGLE=A를 다시 읽어도 Attached=A면 같은 원장으로 돌아간다. 같은 run에 새 path·새 operation key·새 part ID를 만들지 않는다. P에서 후보가 NONE이거나 다른 run만 보이더라도 기존 A 연결을 지우지 않고 A의 상태/미결 요청을 직접 확인한다. 특히 current pointer나 stop intent를 삭제해서 다음 run을 받는 복구는 제공하지 않는다.

## 5. 재접속·정상 완료·pause·재시작의 처리

| 상황 | 처리 |
|---|---|
| 배정 없음, 기존 연결 없음 | 같은 인증 session으로 bounded polling. planner/part/StartRun 0회. 서비스 종료도 가짜 run stop을 만들지 않는다. |
| 동일 프로세스의 transport 단절 | peer_boot를 유지한다. 같은 session이면 기존 key/body와 연결을 회수한다. grace 동안 새 frame을 만들지 않는다. Session.Open을 run마다 반복하지 않는다. |
| P runtime 또는 executor session 변경 | 새 channel/handshake를 구성하더라도 기존 context의 권한을 새 값으로 교체하지 않는다. active planner를 동결하고 원래 연결·미응답 요청을 회수한다. P의 권한 철회와 RECOVERY_REQUIRED를 유지한다. |
| E 프로세스 재시작 | phase74 root 소유권 → 필수 원장 확인 → 새로운 peer_boot 등록 순서. 이전 boot 재사용 금지. 저장된 Attached/stop를 먼저 회수하며 조회 성공만으로 BT를 재기동하지 않는다. |
| 정상 part 완료 | 기존 CompletedVisit proof로 정확한 run/session/recipe/visit/epoch의 planner를 retire한다. 중간 part 전환에는 PauseRun을 만들지 않는다. |
| 정상 run 완료 | P COMPLETED, 기존 part 완료/인계 검증, planner 종료 확인, 연결 종료 기록을 보존한 뒤 current pointer를 비운다. 같은 Client/session을 반환받아 다음 배정을 기다린다. |
| 명시 pause·서비스 종료·장애 | 기존 stop intent와 요청 history를 보존한다. PENDING/ATTENTION이면 새 배정으로 도망가지 않는다. 정상 service stop과 새 process start는 같은 run의 재시작 허가가 아니다. |
| PAUSED/RECOVERY_REQUIRED 또는 다른 owner | 같은 run을 조회/표시만 한다. 새 세대/mandate의 명시 restart/rebind와 기존 stop의 이력 보존 전이가 구현되기 전에는 재운전하지 않는다. 이전 owner의 stop을 새 owner에게 전송하지 않는다. |

현재 `PauseObserved`는 PAUSED, RECOVERY_REQUIRED, COMPLETED, ABANDONED 모두에 사용된다. 따라서 Report.phase만 보고 current attachment를 해제하면 안 된다. P의 구체 run 상태·StopReason·원래 연결 identity와 planner 정리 결과를 확인해야 한다. 현재 RunService는 planner close 오류를 last_error에 남긴 뒤 stop 결과를 반환하므로, 외부 CellService가 그것을 무시하고 다음 planner를 여는 경로도 막아야 한다. 단순 최근 통신 오류와 미확인 planner 종료를 구별할 구조화된 종료 결과가 필요하다.

근거: [stop 조회 및 owner 확인](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/runtime/rx-executor/src/worker/lifecycle.rs:65), [첫 stop 보존](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/runtime/rx-executor/src/journal/lifecycle.rs:22), [P peer 전이](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/executor_peer.rs:32), [현재 미구현 RestartRun](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-api/src/grpc/cell_negotiation.rs:528).

## 6. 구현 순서와 bounded acceptance

구현 순서는 (1) P의 조회-only 새 binding/DTO와 권한·후보 검증, (2) S Client의 validated assignment read, (3) 서비스 원장 init/required-open·Preparing/Attached 복원, (4) RunService의 Client 반환과 cell loop, (5) 제품 CLI에서 직렬 모드 run/visit 제거 및 구조화된 상태 표시다. executable은 기존 release pin만 사용한다. 임의 shell/site executable이나 S의 P 내부 import는 추가하지 않는다. phase74 owner/helper를 다시 일반화할 필요는 없다.

최초 인수는 한 root·한 셀·고정된 공정, 각 2개 part인 A/B 두 run으로 제한한다. 기존 manual/service 시험을 유지하면서 다음을 확인한다.

1. NONE에서 실제 planner/part 0회. 작업자의 별도 StartRun과 Host Arm 완료 후 A를 발견하고, A의 P 완료/retire 후 같은 E 프로세스/session이 B를 발견한다. A/B 합계 part/예산 소비/작업 효과는 각각 4개다.
2. StartRun 직후 조회에서 ARMING/SINGLE을 봐도 part 0개. 조회와 실제 연결 사이 epoch/session/recipe가 바뀌면 원장 연결 또는 dispatch를 거부한다.
3. 미연결 root에서 같은-purpose A/B 후보는 AMBIGUOUS, planner 0회. 이미 A에 연결된 root에서는 합법적인 독립 B만 추가됐다는 이유로 A/B를 일괄 철회하지 않는다. P의 기존 scope/resource 경쟁 시험을 유지한다.
4. 첫 Begin/Complete 응답 유실 후 동일 part ID/원래 key가 회수되고 소비는 증가하지 않는다. 복수 IN_PROGRESS part를 S 직렬 worker가 임의 선택하지 않는다.
5. Preparing commit 후, run 원장 생성 후, Attached commit 후 각각 프로세스를 종료하고 재열어 추가 part/operation이 생기지 않음을 확인한다. Attached 원장 및 service header 각각의 삭제/빈 파일/다른 Scope는 연결 전 Attention이며 새 header로 대체하지 않는다.
6. 짧은 transport 재접속은 같은 boot/session/원장으로 계속한다. P/E restart와 PAUSED/RECOVERY_REQUIRED에서는 새 planner/part 0회, stop·미응답 요청 이력 보존. 같은 Run의 명시 재운전은 아직 지원하지 않는 것으로 응답한다.
7. 활성 run 중 서비스 종료는 stop을 보존하고 PENDING을 숨기지 않는다. P COMPLETED라도 planner 종료 확인 실패 시 다음 planner 0회. idle 종료는 P PauseRun 0회.
8. phase74의 root 중복/alias/특수파일/정상 반납 및 Linux 실제 CLI before-connect probe를 유지한다. 새 binding의 다른 cell/principal/session, 시간 만료, sequence 역행, 잘못된 witness/cardinality, payload/scan 한도 초과도 거부한다.

이 단계의 완료는 새 작업자 StartRun을 설정 파일 수정 없이 발견해 정상 run 두 개를 연속 처리하고, 모호함·권한 변경·원장 유실을 안전하게 표시하는 데까지다. full scheduler, 범용 할당 mutation, 같은 run의 복구 재시작, 다중 활성 Run의 자동 분배는 이 구현에 섞지 않는다.
