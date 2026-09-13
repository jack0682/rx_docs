# Phase80 / P03 — RECOVERY_ONLY에서 명시적인 운전 Host 등록 재연결

phase79 완료 후의 읽기 전용 검토다. 이 파일은 구현 제안이며 새 규범을 확정하지 않는다. 제품 소스·규범을 수정하지 않았고 빌드·시험·서버·장비를 실행하지 않았다. 전체 R01–R30 목표는 유지하며, 여기서는 **현재 P runtime + 같은 Host baseline에서 새 운전 등록을 만드는 하위 경계**만 정의한다.

## 1. 판단과 완료 범위

`RECOVERY_ONLY → 기존 registration.session 교체`는 적법한 최소 구현이 아니다. 기존 registration의 grant는 옛 P→H caller session에 속하고, P의 새 producer session과 H의 새 platform session은 서로 다른 축이다. 새 등록에는 **새 명시 승인, 새 resource fence·grant 요청, 실제 H의 인계 검사, 전체 대상 등록의 원자 교체와 이전 원문 보존**이 필요하다. 정상 등록 rebind의 결과는 `BOUND_UNQUALIFIED`(제안 명칭)이며, 자격 발급·block 해제·Arm·Run/mandate/permit 재발급과 구별한다.

P03 성공은 현재 session을 쓰는 새 HostRegistration/Plan/lease를 실제 서비스가 소유하고, 조건·원래 evidence·메타데이터 전달을 재개할 수 있다는 뜻이다. 관련 UNKNOWN/QUARANTINE, 열린 case, E의 기존 Run attachment와 PENDING stop intent를 없애지 않는다. 회수한 native SUCCEEDED가 전체 작업의 후조건 연속성을 입증하지 못하면 기존 NONE/UNKNOWN도 유지한다.

**첫 양성 인수 후보**는 같은 H가 살아 있고 대상 자원에 미결 작업/격리가 없는 P-only restart다. 대상 resource를 보유한 미확정 작업은 RecoveryOnly 조회/명시 처분 경로에 남긴다. 이 제한은 P03 새 명령권 획득의 선행조건이며 다른 셀·자원의 독립 실행이나 전체 복구 목표를 금지하는 전역 불변식이 아니다.

## 2. 규범과 제안의 구분

아래 경로의 앞부분은 `/Users/ojaehong/RX_automation/rx_ws/rx_docs/docs/`다.

| 규범 근거 | 이 경계에 적용되는 확정 의미 |
|---|---|
| [base 02 §1·§2, 16–40행](/Users/ojaehong/RX_automation/rx_ws/rx_docs/docs/contracts/v1.0/02_identity_durability_recovery.md:16) | resource fence는 durable 증가값. T4에 권한/fence 변경·사건·전달 대기를 같이 저장한다. NEW/EMIT_ENTERED/VOIDED를 구별하고 원래 key/ID로 유실 응답을 회수한다. P/H 두 DB의 commit을 하나의 분산 원자로 주장하지 않는다. |
| [base 02 §3, 50–64행](/Users/ojaehong/RX_automation/rx_ws/rx_docs/docs/contracts/v1.0/02_identity_durability_recovery.md:50) | native 제출 진입과 gate/CAS를 직렬화한다. SEND_ENTERED는 조회/조정이며 자동 native 재전송 금지. PREPARED의 후속 전달도 새 grant와 현 상태 검사를 요구한다. 이것이 P03에서 옛 permit를 자동 재사용할 권한은 아니다. |
| [base 02 §4, 68–79행](/Users/ojaehong/RX_automation/rx_ws/rx_docs/docs/contracts/v1.0/02_identity_durability_recovery.md:68) | 이전 owner의 대기 요청·native queue/channel·소재 지지 인계가 필요하다. lease 만료만으로 이전 자원을 넘기지 않는다. 자원 묶음은 부분 획득 대기 없이 함께 예약하고 fence=max(저장 최대)+1을 원자 저장한다. 새 grant에 equal fence 재사용 불가. |
| [base 02 §5·§7, 81–118행](/Users/ojaehong/RX_automation/rx_ws/rx_docs/docs/contracts/v1.0/02_identity_durability_recovery.md:81) | grant expiry는 H monotonic 시간으로 판단한다. duplicate renew_seq는 expiry를 연장하지 않는다. 같은 Linux boot/CLOCK_BOOTTIME을 검증하며 source age를 retry 시각으로 바꾸지 않는다. P-only restart는 receipt/evidence/fence 재조정이며 자동 Run 재개가 아니다. |
| [base 01 §7, 110–116행](/Users/ojaehong/RX_automation/rx_ws/rx_docs/docs/contracts/v1.0/01_responsibility_and_semantics.md:110) | RELEASED에는 잔류 명령 배제·제어 상태·필요 지지 인계 근거가 필요하다. UNRESOLVED는 별도 RecoveryDisposition으로 현재 자원을 처분할 수 있으나 과거 성공으로 바꾸지 않는다. |
| [base 03 §5, 120·133–152행](/Users/ojaehong/RX_automation/rx_ws/rx_docs/docs/contracts/v1.0/03_data_and_protocol.md:120) | Session.Open은 motion 권한이 없다. AcquireGrant는 이전 owner 인계가 필요한 권한 mutation이다. RevokeGrant/CloseControlSession과 결과 조회는 별도 경계다. |
| [cell 02 §1–§3, 7–48행](/Users/ojaehong/RX_automation/rx_ws/rx_docs/docs/cell_operations/v1.0/02_authorization_invalidation.md:7) | READY 파생 표시·qualification·block·mandate는 독립이다. REVOKED mandate를 ACTIVE로 되돌리지 않는다. P/H/E restart와 owner 변경은 latched 철회이며 단순 transient 회복이 아니다. 정상 UI 창 닫힘과 생산 mandate 자동 철회도 구별한다. |
| [cell 02 §5–§7, 62–94행](/Users/ojaehong/RX_automation/rx_ws/rx_docs/docs/cell_operations/v1.0/02_authorization_invalidation.md:62) | H 최종 gate에서 current epoch/grant/permit/조건을 검사한다. 모든 필요한 Fence ACK 전 새 epoch를 운전 활성화하지 않으며 ACK가 native 종료/접근 허가는 아니다. cell/run/case/권한 변경은 같은 P transaction에 저장한다. |
| [cell 03 §2·§4–§6](/Users/ojaehong/RX_automation/rx_ws/rx_docs/docs/cell_operations/v1.0/03_intervention_recovery_change.md:13) | 알려지지 않은 물리 변화·세대 상실은 DIAGNOSTIC_ONLY의 자동 continuation으로 낮출 수 없다. 복구 step은 승인된 절차와 근거를 요구하고 새로운 RestartRun 의도와 구별한다. |
| [cell 04 §5–§8, 112–160행](/Users/ojaehong/RX_automation/rx_ws/rx_docs/docs/cell_operations/v1.0/04_protocol_integration_ui.md:112) | Fence/Arm receipt는 RX gate 사실. grant/등록과 새 qualification/Arm/Start를 합치지 않는다. body에 적힌 actor/session을 인증 증거로 쓰지 않는다. |

[06 계약·신뢰성 §8–§9](/Users/ojaehong/RX_automation/rx_ws/rx_docs/docs/06_contracts_and_reliability.md:95)는 위 저장/물리 경계의 선행 설계 설명이다. [phase75 rebind 계획](/Users/ojaehong/RX_automation/rx_ws/rx_docs/docs/implementation/next_steps/host_rebind.md:49)은 구현 제안이며 phase78/79 이전 원인 설명 중 producer DeviceRestart·조회 공백은 이미 바뀌었다. 이를 현재 규범으로 승격하지 않는다.

규범에는 `HostRegistrationRebind`, `BOUND_UNQUALIFIED`, 이 기능의 정확한 ReleaseManager route/DTO가 정의돼 있지 않다. 아래의 역할 배정·상태/record 이름은 **기존 의미를 지키는 제품 설계 제안**이며 승인 경계 선택은 root가 확정할 사항이다.

## 3. 현재 소스에서 확인한 재사용점과 연결 결함

P 소스 앞부분은 `/Users/ojaehong/RX_automation/rx_ws/rx-platform/`, S 소스는 `/Users/ojaehong/RX_automation/rx_ws/rx-solutions/`다.

| 구현 근거 | 현재 동작과 P03 판단 |
|---|---|
| [P host_link.rs:125](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/host_link.rs:125), [139](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/host_link.rs:139), [384](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/host_link.rs:384) | normal prepare는 H pending을 거부하고 기존 registration.session==current producer를 요구한다. normal commit도 같은 mismatch를 거부한다. 기존 경로의 비교 삭제/예외 flag 대신 별도 승인된 rebind transaction이 필요하다. |
| [P host_link.rs:188](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/host_link.rs:188), [342](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/host_link.rs:342) | max(P/H resource fence)+1 및 원래 send time 기반 보수적 P grant expiry 계산을 재사용할 수 있다. 현재 per-cell bootstrap의 100ms 준비 유효기간을 사람의 승인 대기 시간과 혼용하지 않는다. |
| [S grants.rs:41](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/runtime/rx-host/src/gate/grants.rs:41), [52](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/runtime/rx-host/src/gate/grants.rs:52), [90](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/runtime/rx-host/src/gate/grants.rs:90) | 동일 grant 요청은 원래 결과를 반환한다. 새 요청은 native.can_handover와 겹치는 SEND_ENTERED/NativeAccepted를 검사하고 resource maxima+grant+request receipt를 H transaction에 저장한다. P snapshot의 빈 pending/Ready 값으로 이 최종 검사를 대체하지 않는다. |
| [S native.rs:43](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/runtime/rx-host/src/native.rs:43), [JTC adapter.rs:359](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/runtime/rx-host/src/ros_jtc/adapter.rs:359) | can_handover 계약은 잔류 native 명령·물리 지지/인계를 확인하는 것이다. JTC는 실제 handover_snapshot의 no_pending/control/support를 검사한다. 이 profile/현장 근거가 없는 physical 구성에 임의 true를 공급할 수 없다. P에 반환되는 일반 Grant에는 해당 상세 관측 원문이 없다. |
| [P recovery/reads.rs:248](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/host_recovery/reads.rs:248) | 현재 RecoveryOnly read는 H resource maximum == 현재 P host-link-fence를 요구한다. **P가 새 최대를 먼저 예약하면, H가 아직 옛 최대인 정상 과도 상태를 자기 검증기가 거부한다.** P03의 before/reserved/confirmed cut을 별도로 검증해야 한다. |
| [P recovery/context.rs:347](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/host_recovery/context.rs:347), [366](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/host_recovery/context.rs:366) | RecoveryOnly는 cell/registration/Plan 현재 revision을 고정한다. rebind commit 자체가 그 등록을 바꾸므로 완료 뒤 old recovery를 계속 current로 표시하면 안 된다. 원문은 보존하고 새 rebind receipt로 연결한다. |
| [P host_link.rs:488](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/host_link.rs:488), [S grants.rs:145](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/runtime/rx-host/src/gate/grants.rs:145) | 현재 renewal sequence는 per-link Plan, H sequence는 per-grant다. **하나의 union grant를 여러 cell Plan에 복사하고 기존 각각의 renew worker를 돌리면 같은 renew_seq를 독립 발급한다.** 두 번째 중복 응답을 더 늦은 P sent_at으로 계산하면 expiry가 잘못 연장될 수 있다. shared grant는 한 renewal owner/sequence가 필요하다. |
| [P ConnectionService:326](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-host-client/src/connection.rs:326), [410](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-host-client/src/connection.rs:410) | initial connection loop는 성공 뒤에야 bound worker/renewal을 시작한다. rebind commit 뒤 이 loop가 일반 bootstrap을 다시 호출하게 방치하지 않는다. 새로 commit한 plan의 **회수·인수** 전용 경계가 필요하다. TTL보다 늦게 발견했다면 만료된 grant를 새 bootstrap key로 자동 재획득하지 않는다. |
| [P recovery/transport.rs:5](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-host-client/src/recovery/transport.rs:5) | RestrictedHost는 grant/native 쓰기 메서드를 노출하지 않는다. 이를 unrestricted로 바꾸지 않고, 별도 rebind worker의 typed GrantTask만 AcquireGrant를 부를 수 있게 한다. |
| [S rpc/host_service.rs:214](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/runtime/rx-host/src/rpc/host_service.rs:214) | 규범에 있는 RevokeGrant/CloseControlSession은 현재 미지원 응답이다. Grant request 전용 read-only Lookup도 확인하지 못했다. 발급 뒤 실패의 정리/영수증 회수 능력을 있다고 가정하면 안 된다. |
| [P executor_peer.rs:70](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/executor_peer.rs:70) | 새 current E session 생성은 AuthorityRevoked closure를 추가해 epoch/block/cell revision을 바꾼다. 읽기 단계가 아니다. E 세션 등록은 Host fresh recovery/rebind 승인보다 먼저 배치해야 한다. 늦게 발생하면 옛 승인 CAS를 거부하고 이미 받은 ACK/Grant 사실을 보존한다. |

## 4. 권고하는 최소 독립 구현 단위

### A. 시작점·선행조건

1. 필요한 E current session 등록을 먼저 명시 수행한다. E Run/attachment 회수·재개는 별도 절차다. 이후 현재 P cut으로 Host RecoveryOnly를 refresh/명시 승인한다. E/Host/다른 관리 등록이 그 뒤 바뀌면 자동 최신 epoch 채택 대신 현재 작업을 stale/Attention으로 남긴다.
2. 호출자는 등록 terminal의 ReleaseManager로 제안한다(제품 정책 후보). 전체 Host 소속 셀 및 기존 resource/scope/Host 영향 closure 접근권을 검사한다. 외부 body는 recovery ID, expected revision/digests, 이유/CAS만 받고 endpoint/certificate/snapshot/actor/ttl/실행파일을 입력받지 않는다.
3. 현재 serving runtime/store/clock, producer revision/session·협상된 cells, actual platform session, baseline 안정 신원/transport/source와 현재 config proof를 다시 확인한다. 최초 baseline context=None은 허용하되 현재 config가 바뀌었으면 저장된 Change.application·Host task/receipt·실제 applied context로 증명한다. 최초 whole Registration/Plan digest를 현재와 같게 요구하지 않는다.
4. 대상 command resource에 미결 native entry/control session, 아직 보유/격리된 P resource, 처리되지 않은 H pending permit/operation, 설명되지 않는 외부 mode/owner/지지 변화가 있으면 새 grant 단계로 가지 않는다. 원래 UNKNOWN/UNRESOLVED 및 격리 이력은 유지하고 RecoveryOnly로 계속 조사한다. P03가 새 RecoveryDisposition이나 material 판정을 만들지 않는다.
5. 명령권 이동을 금지하는 관련 case/외부 격리 조건은 해소 근거가 필요하다. 반면 RuntimeRestart/AuthorityRevoked/OperatorHold 같은 block이 존재한다는 이유만으로 모든 비운전 등록을 일률 금지하면 재검증 worker를 열기 위한 순환 대기가 된다. **새 grant를 허용할 block/case 조합은 명시 정책으로 확정할 항목**이며, block은 P03 성공에도 제거하지 않는다.

### B. 최소 record·전이 제안

새 `HostRebind` record는 phase79 `RecoveryBinding`을 수정해서 격상시키지 않고 그 ID/digest와 baseline ID 집합을 참조한다. immutable 부분은 다음으로 한정한다.

- 현재 installation/store/runtime/clock·producer/platform session·transport pin, 대상 Host/cohort와 영향 cell/config/epoch/scopes/blocks/CAS.
- **제안 당시 현재** old registration/Plan/lease 원문 digest·revision, 기존 baseline/현재 applied proof 참조. baseline 최초 감사 원문과 current CAS를 구별한다.
- resource 집합, 각 P/H `before_maximum`, 예약할 resource fence, release 설정에서 고정한 TTL, 각 Fence/Grant request ID·정규 body digest.
- 승인 행위자 기록, 승인 key/body/digest. 저장된 actor는 인증 주장이 아니며 진행 때 현재 권한을 재확인한다.

최소 상태 후보는 `PROPOSED → AUTHORIZED → GRANT_SEND_ENTERED → REGISTRATION_COMMITTED`, 실패/혼합/만료는 `ATTENTION`이다. 여러 grant group을 허용하면 group별 SendEntered/receipt를 저장하되 전체 registration commit은 하나다. 세션 만료 후 적법한 새 담당자가 같은 record/ID/body를 명시 재승인할 수 있어야 하며, 새 scope/key를 오류 처리기가 자동 만들어서는 안 된다.

### C. 원자 저장과 네트워크 순서

| 경계 | 같은 P transaction | 그 뒤 가능한 일 |
|---|---|---|
| 제안/승인 | 실제 preflight evidence 참조, old/current CAS, 원래 요청 상관과 proposal digest, 승인 actor | 아직 grant 없음. 같은 key lookup은 H offline이어도 원래 record 회수. |
| 권한 계획 T4 | 모든 대상 resource의 새 최대=max(P/H before)+1, exact Fence/Grant IDs/body, 승인/currentness, rebind 계획 소유 slot·기존 resource 보유 조건 | fresh current cell Fence 확인. **기존 work holder/quarantine을 고쳐 쓰거나 해제하지 않는다.** 예약 최대를 실패 때 낮추지 않는다. |
| 전송 진입 | group의 GrantSendEntered, 원래 conservative `sent_at`/TTL, 현재 승인·source/config/P cut | 이 task 하나의 AcquireGrant만 호출. 네트워크 I/O는 writer transaction 밖. |
| receipt 저장 | exact request/body·Host boot·resource set/fence/owner/TTL의 원문 Grant와 correlation, 원 send time, 과거/현재 상태 | 늦은 receipt는 actor/CAS가 바뀌어도 사실로 보존. stale/만료면 registration 승격은 금지. |
| 전체 등록 commit | 모든 receipt 및 fresh post-read 재검증; 이전 current registration/Plan을 history로 보존; 새 registration/Plan/current pointers, 새 baseline+원문 sidecar, rebind lineage/receipt, 서비스 인수 대기 상태 | 원자적으로 새 등록을 조회 가능. 기존 qualification/blocks/Run/mandate/permit/UNKNOWN/resource 처분은 변경하지 않음. |
| 실제 서비스 인수 | current committed plan/producer/platform session·lease owner 검증, 진단 owner 상관 | grant 재발급 없이 해당 등록을 사용하는 worker/renewal 시작. 인수 실패·expiry면 Attention. |

`before/reserved/confirmed`는 임의 max 허용이 아니다. 전송 전 actual H resource maxima는 계획에 고정한 before 값, P는 예약값이어야 한다. 해당 grant receipt 이후 H/P 모두 예약값과 같아야 한다. 계획 밖 전진·후퇴·다른 grant는 거부한다. cell/scope epoch는 P03가 convenience로 다시 올리지 않고, 현재 승인된 Runtime/추가 철회의 vector·latched block 전체를 정확히 H에 확인한다.

H AcquireGrant의 can_handover·native pending 검사와 H 원자 resource/grant 저장은 최종 판단으로 그대로 유지한다. 이 RPC의 성공을 P가 물리 정지/인원 안전성 검증으로 확대하지 않는다. 필요한 상세 물리 인계 근거를 P 감사에 남기는 방식은 아래 미확정 항목이다.

### D. grant 묶음의 첫 범위 후보 — root 선택 필요

- **후보 1: scope0 단일 Host/단일 cell부터.** Host가 복수 cell에 등록돼 있으면 부분 등록 대신 명시 Unsupported/Attention으로 거부한다. 기존 per-plan renewal을 사용할 수 있어 가장 작은 독립 구현이다. 이는 아직 지원하지 않는 조합의 표시이며 전체 다중 셀 목표를 삭제하는 결정이 아니다.
- **후보 2: 복수 cell의 서로 겹치지 않는 grant resource set.** cohort 전체를 계획/원자 commit하고 grant는 각 집합별 독립 ID/renewal sequence다. 어느 H 발급이 실패해도 일부 cell만 새 operating 등록으로 commit하지 않는다. 겹치는 집합은 명시 거부한다.
- **후보 3: 겹치는 자원을 합친 Host/grant 그룹.** 그룹별 grant 하나와 **단일 lease/renewal owner·sequence**를 만들고 cell registrations는 이를 참조한다. 기존 per-cell renew loop를 그대로 쓰지 않는다. 동일 grant의 중복 renewal 시각을 더 늦은 P sent_at으로 재계산하지 않는 별도 시험이 필요하다. 이 후보는 필요한 기존 타입/서비스 변경이 더 크다.

## 5. 부족한 API·구현 접점

1. P `host_rebind` typed model/engine: context/propose/authorize/progress/get/list, cached receipt 조회, before/reserved/confirmed validator, T4 reservation, immutable GrantTask/receipt 및 whole-cohort commit. exact route/이름은 제안이며 규범 route를 변경한 것으로 간주하지 않는다.
2. P `host_recovery`의 안정 신원·현재 설정/source 검증을 제한된 내부 helper로 재사용한다. 기존 RecoveryOnly `read resource maximum == P maximum` 검사를 보편적인 bypass flag로 완화하지 않는다. rebind 중 계획된 불일치와 완료 뒤 새로운 generation을 명시적으로 구별한다.
3. P `host_link`의 저장 로직을 좁게 재사용하되 normal prepare/commit에서 old session mismatch를 계속 거부한다. rebind 전용 승인 증명 없이는 그 비교를 통과할 수 없다. 새 Plan에는 새 BoundReceipt와 baseline/source sidecar를 함께 만들어야 다음 P restart에서 `BaselineMissing`으로 막히지 않는다.
4. `rx-host-client`에 typed rebind worker와 `adopt_committed_link` 성격의 entrypoint가 필요하다. 기존 RestrictedHost에 Acquire/Arm을 추가하지 않는다. `rx-runtime`은 writer 명령과 실제 worker service를 연결하고, terminal API는 actor/CAS만 전달한다. post-commit 발견 지연을 일반 bootstrap/새 key로 보정하지 않는다.
5. UNKNOWN/QUARANTINE 선행 처분은 아직 별도 공백이다. 현재 [handover.rs:46](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/handover.rs:46)는 ready·원래 permit epoch/session을 요구한다. [qualification quiet():236](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/qualification_activation/mod.rs:236)도 미종료 Run/UNKNOWN/held resource를 거부한다. P03는 이 순환을 강제로 해제하지 않고 관련 사례를 별도 T5/Restart 준비 과제로 남긴다.
6. 등록 교체 뒤 **새** qualification Issue는 [issuance.rs:246](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/qualification_activation/issuance.rs:246)의 current registration tuple을 사용할 수 있다. 기존 task의 [generation():409](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/qualification_activation/mod.rs:409)는 old session이 달라져 stale여야 한다. 과거 task.session을 고치거나 이전 qualification을 다시 active로 만들지 않는다. 기존 receipt Lookup과 새 명시 발급/활성화는 구별한다.
7. Grant response 유실 뒤 같은 Acquire 재호출은 **순수 조회가 아니다**: H에 원래 요청이 없으면 grant를 만들 수 있다. 승인/expiry가 더 이상 유효하지 않으면 이를 lookup으로 호출하지 않는다. 현재 Grant 전용 Lookup·실제 RevokeGrant가 부족하므로 이때는 Attention·예약 최대/원래 ID·늦은 receipt를 보존한다. 별도 read binding 또는 명시 superseding 절차의 선택 없이 자동 성공/완전 cleanup을 주장하지 않는다.

## 6. 최소 독립 시험 묶음

1. **정상 제품 경계:** 실제 baseline→정상 공정 Apply/renewal→P-only restart→필요 E 선등록→fresh RecoveryOnly→새 RM rebind 승인→새 grant 1회→registration/service 인수. old registration/grant/원문은 history에 남고 blocks·qualification·Run/permit/mandate·native effects는 회복 구간에 바뀌지 않음. 새 발급/Arm/Start를 호출하지 않는다.
2. **자신이 만든 중간 fence:** P 최대 예약 직후 H는 before 최대인 상태가 올바른 해당 GrantTask에서는 허용되고, 계획 밖 H 최대·다른 예약값·후퇴는 거부된다. 성공 후 새 값이 exact 일치해야 등록한다. 예약 실패/rollback 응답 유실로 최대를 낮추지 않는다.
3. **UNKNOWN/QUARANTINE:** 원래 SEND_ENTERED/UNKNOWN이나 대상 held resource가 있으면 grant 발급0·등록 전환0이며 RecoveryOnly의 원래 receipt/lookup은 유지된다. 다른 독립 셀/자원까지 새 전역 한-Run 규칙으로 막지 않는다. H can_handover=false/native pending이면 P 관측이 좋아도 grant 거부.
4. **권한·source·등록 경쟁:** prepare/authorize/GrantSendEntered/receipt/commit 사이 E OpenExecutorPeer, actor/terminal revoke, producer/Host boot/journal/pin/source/config/epoch 변경을 각각 넣는다. 새 권한 없이 old plan을 현재에 맞춰 고치지 않고 stale/Attention·원래 facts/IDs를 보존한다. E를 Host 승인 전에 등록한 정상 순서도 대조한다.
5. **유실·만료:** T4 commit 전/후, H Acquire commit 후 reply 유실, P receipt commit 후 reply 유실, 전체 registration commit reply 유실. 같은 key/body/request/send time만 회수한다. TTL 만료/approval revoke 뒤에는 Acquire를 조회인 척 호출하거나 새 key/renewal로 숨기지 않는다. 늦은 Grant는 사실 보존하지만 현재 등록으로 승격하지 않음.
6. **cohort/renewal:** 선택한 scope0/다중 셀 정책대로 partial commit0. shared grant 후보를 택하면 두 cell의 renew_seq 충돌·더 늦은 P sent_at으로 expiry 연장되는 반례를 반드시 닫는다. 첫 작은 후보는 해당 공유 조합을 명시 거부하는 시험을 둔다.
7. **등록 인수와 재부팅:** commit된 Plan을 실제 서비스가 grant 재발급 없이 인수한다. 인수 지연으로 lease가 만료되면 자동 bootstrap acquire0. 다음 P restart에서도 새 baseline/rebind lineage가 남으며 이전 originalPlan/RecoveryBinding은 역사로 조회된다.
8. **후속 권한 음성 시험:** rebind 완료만으로 old qualification task/old Arm/old permit/old E attachment가 현재가 되지 않는다. 열린 case·다른 block·미확정 소재는 유지한다. 새 재검증 보고/독립 승인/Host qualification ACK/activation 및 별도 Start/Restart 없이는 native submit0.

이 시험은 코드·실제 P/H FILE_SIMULATION 인수로 나눠 수행해야 한다. 성공한 mock 인계나 UI 문구를 실제 모델의 잔류 명령/지지 증거로 대체하지 않는다.

## 7. 구현 전 root가 결정할 항목

1. 위 scope0 / disjoint cohort / shared grant+single renewal 중 첫 구현 범위. 복수 cell을 지원하지 않는다면 UI/API가 명시 거부해야 하며 몰래 첫/최신 cell을 선택하지 않는다.
2. ReleaseManager의 transport/grant 전환 승인과 RecoveryLead의 현장/자원 처분 책임 연결. 규범의 역할 구분은 확정이나 이 관리 action의 구체 permission은 새 제품 정책이다.
3. 대상 자원에 어떤 case/latched block이 있을 때 새 비운전 grant를 허용하는지. 임의 `ignore_guard`, 단순 operator acknowledge 또는 전체 block 해제는 선택지가 아니다.
4. response-unknown/만료 grant의 읽기 전용 receipt 회수·취소 능력. 첫 범위에서 Attention으로 남길 실패 상태와 후속 S binding/API가 필요한 상태를 구별한다.
5. H can_handover가 제공한 물리 근거를 P 감사에 어떻게 남길지. 현재 bool gate와 일반 Grant만으로 상세 source/time/support evidence를 저장했다고 주장하지 않는다. 실제 physical profile에는 해당 근거/보호 경로 검증이 필요하다.

이 문서는 여기서 마친다. P03 밖의 전체 RecoveryDisposition/RestartRun·E attachment 처분·qualification/현장 복원 설계를 대신 확정하지 않는다. 해당 후속 범위는 미완료로 명시하며 전체 R01–R30 목표에서 제거하지 않는다.
