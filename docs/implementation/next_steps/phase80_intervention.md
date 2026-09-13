# Phase80 / P03 — native capture 회수 후 남은 UNKNOWN의 조사·처분·개입 연결

2026-09-13. 읽기 전용 규범/소스 조사. 이 문서만 새로 작성했다. 제품 코드 변경·빌드·시험·서버 기동·DB 쓰기는 하지 않았다.

조사 기준 P commit: `61759fcb59f00123a2c1cac705ad764b95c28505`; 문서 저장소 commit: `707c85f8c037f84b334b1625d36c12b53e58eb7d`. Host operating rebind와 Executor 복구 구현은 다른 검토 범위이며 여기서는 그 완료를 가정하지 않는다. 실물 셀은 NOT_COMMISSIONED다.

## 1. 결론과 현재 상태의 정확한 의미

Phase79의 실제 경계는 H의 원래 native success capture를 회수·영속 publication했지만, 원 permit 이후 epoch/scopes/제한이 바뀌고 completion의 ready 후조건 연속성을 입증하지 못해 P Work가 `RECONCILING / UNKNOWN / NONE / QUARANTINED`로 남은 경우다. evidence 저장과 전체 작업의 성공 결론은 다르다. 사람의 ACK·다시 읽은 ready=true·새 qualification으로 과거 후조건 연속성을 복원했다고 처리하면 안 된다.

기존 규범은 세 경계를 구별한다.

1. **조사 포기 처분**: 운영 책임자가 조사 근거와 명시적 의도를 남겨 원 operation을 `SETTLED / UNRESOLVED / QUARANTINED`로 기록할 수 있다. 성공이나 자원 해제가 아니다.
2. **비운전 Case 종료**: 검증된 현재 억제·격리/인원·인수 근거가 있으면 `REMAIN_OUT_OF_SERVICE`로 Case만 닫고 OUT_OF_SERVICE 제한을 남길 수 있다. 원 Work와 resource quarantine은 그대로다. 첫 처분이 선행되어야만 가능한 경로도 아니다.
3. **후속 생산 또는 명시적 재개**: 과거 불명에 대한 처분, 현재 소재·장비 상태, 잔류 native 명령·제어·지지 인계, 해당 절차·자격·case/외부 제한, 새로운 시작 경계가 모두 필요하다. 옛 operation/permit/mandate의 재전송 또는 부활은 허용되지 않는다.

현재 제품 P는 Case/ACK/절차 보고 API와 core 비운전 Close를 갖는다. 그러나 실제 procedure/close 정책을 검증·공급하는 제품 authority, 첫 T5 조사 처분, T5 자원 인계, RecoveryPlan/RestartRun은 연결되어 있지 않다. 따라서 지금 제품에서 사람에게 **새 명령 없이 사실을 읽고 Case/ACK/보고를 보존하는 것**과 **실제 종료/운전 허용을 발급하는 것**을 구분해서 보여야 한다.

## 2. 규범 근거

| 근거 | 이 상황에 적용되는 내용 |
|---|---|
| [base 01 §5, 94행](/Users/ojaehong/RX_automation/rx_ws/rx_docs/docs/contracts/v1.0/01_responsibility_and_semantics.md:94) | 조사 후 결과를 더 알 수 없고 운영 책임자가 포기하면 SETTLED/UNRESOLVED. 성공 분기 금지·격리 유지. 후발 모순은 이전 결과를 덮어쓰지 않고 DISPUTED. |
| [base 01 §6–7, 107·114·116행](/Users/ojaehong/RX_automation/rx_ws/rx_docs/docs/contracts/v1.0/01_responsibility_and_semantics.md:107) | 사람 확인은 actor/scope/시점/절차 revision을 가진 HUMAN_ATTESTATION. 자원 RELEASED는 잔류 명령 배제·제어권·필요 지지 인계가 별도 조건. UNRESOLVED 자원도 검증된 복구 절차와 새 RecoveryDisposition으로만 해제하며 다음 생산은 새 activation. |
| [base 02 T5](/Users/ojaehong/RX_automation/rx_ws/rx_docs/docs/contracts/v1.0/02_identity_durability_recovery.md:36) | 조사 근거·actor·이전 결과 참조·자원 해제 조건·새 admission 조건·사건을 같은 transaction에 기록. |
| [base 03 RecoveryDisposition](/Users/ojaehong/RX_automation/rx_ws/rx_docs/docs/contracts/v1.0/03_data_and_protocol.md:106) | operation ID, expected revision, evidence IDs, procedure digest, disposition, reason. caller가 outcome을 직접 쓰지 않는다. 현재 인증/접근권 → 같은 key/전체 body → 새 요청 CAS/적격성 순서. reason.detail은 진단용이므로 문자열로 처분 의미를 결정하지 않는다. |
| [cell 03 §2–5](/Users/ojaehong/RX_automation/rx_ws/rx_docs/docs/cell_operations/v1.0/03_intervention_recovery_change.md:15) | 접근·연속성 상실 시 FAULT_RECOVERY/latch, 외부 진입 근거 전 PROCEDURE_ACTIVE 금지. 참여자 종료/인수 후 REVALIDATING. 과거 불명을 성공으로 바꾸지 않으며 현재 상태·소재 처분을 별도로 검증. |
| [cell 03 §8](/Users/ojaehong/RX_automation/rx_ws/rx_docs/docs/cell_operations/v1.0/03_intervention_recovery_change.md:93) | PrepareClose는 run/restart plan 없이 REMAIN_OUT_OF_SERVICE clearance를 만들며, CloseWithoutRestart는 소비+대상 case 종료+별도 latch를 원자 기록하고 Arm하지 않는다. |
| [cell 04 재시작 순서](/Users/ojaehong/RX_automation/rx_ws/rx_docs/docs/cell_operations/v1.0/04_protocol_integration_ui.md:118) | REVALIDATING → PrepareRestart → 새 epoch/Fence → 현재 상태·잔류 작업·인원/절차 재확인 → 해당 epoch clearance/READY → Operator RestartRun → 같은 epoch Arm → 새 mandate/clearance 소비/case 종료/run 원자 commit. |

현재 `CompletionRule::Native`의 success+비어 있지 않은 postconditions는 [evidence.rs:342](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/evidence.rs:342)의 epoch/scopes/빈 block 연속성이 있어야 성공 판정한다. 이 조건이 깨진 Phase79에서 native 성공 상태를 회수해도 UNKNOWN/NONE을 남긴 것은 의도된 동작이다.

## 3. 가장 좁은 첫 T5는 전체 물리 procedure admission 없이 가능한가

**규범 해석: 가능하다.** 단, 아래의 좁은 조사 처분 검증을 실제로 구현해야 한다. 현재 코드에서 이미 실행 가능하다는 뜻은 아니다.

base 01의 조사 포기→UNRESOLVED 조건과, 그 다음 §7의 검증된 복구 절차→자원 해제 조건은 서로 다르다. 격리를 유지하는 첫 처분에 PROCEDURE_ACTIVE, 현장 작업 참여, personnel/handover, current support PASS 또는 Close policy를 선행시킬 문언상 요구는 없다. 실제 접근하지 않았는데 그 경로를 통과하려고 WorkStarted/WorkFinished나 사람 명단을 만들면 안 된다. 필요한 H 통신이 없다는 이유만으로 이미 저장된 조사 근거에 대한 보수적 포기 의도조차 만들지 못하게 할 근거도 이 좁은 처분에는 없다.

다만 다음은 첫 T5에서도 생략할 수 없다.

| 검증 대상 | 좁은 첫 처분에서 필요한 확인 | 현재 빈자리 |
|---|---|---|
| 사람의 의도/권한 | 현재 유효한 사람 세션과 설치·작업 셀 접근권, 운영 책임자의 명시적 조사 포기. native success가 전체 작업 성공을 입증하지 못한다는 조사 결론과 연결한다. 서비스 peer/Host/Executor의 자동 요청이나 일반 알림 ACK를 포기 의도로 해석하지 않는다. | norm은 운영 책임자라고 규정한다. 현재 Case의 RecoveryLead는 가까운 기존 역할이지만 T5의 구체 역할/단말 binding은 아직 구현되지 않았다. ReleaseManager의 Host recovery 승인이 이 역할까지 자동 부여하지 않는다. |
| 원 operation의 현재 절단면 | 원 ID·invocation·intent/profile·permit/Run/part·현재 revision과 UNKNOWN/NONE·격리 상태, 기존 근거를 대조한다. 이미 다른 결론이 있는 작업을 조용히 UNRESOLVED로 바꾸지 않는다. | domain `conclude`는 있으나 운영자용 검증 transaction이 없다. 기존 terminal 결과와 충돌하는 후발 증거는 별도 조사/무결성 처리 대상이다. |
| evidence IDs의 실제 원문 | ID 목록만으로 승인하지 않는다. P가 보존한 불변 native/receipt/source-prefix 근거 및 조사 attestation의 원문·schema·소유/source·작업/인자 상관·중복/충돌을 읽고 기록한다. 원래 성공 capture, 후조건이 끊긴 현재 epoch/scopes/block 근거, 조사 포기 attestation을 서로 구별한다. | `evidence/<id>`의 native 근거는 존재한다. generic Attestation intake/T5 검증은 없다. Case ACK/ProcedureRecord ID는 native Evidence ID와 다른 저장 경로이므로 무검증으로 같은 종류처럼 취급할 수 없다. |
| `procedure_digest` | 실제 버전이 고정된 조사 절차/적용범위를 식별해야 한다. 대상 artifact 원문을 로컬 내용 주소/신뢰된 release 자료로 확인하고 해당 조사 처분에 적용되는지 검사한다. 임의 32-byte 값, URI 또는 caller supplied PASS는 근거가 아니다. | 기존 `verify_procedure`는 현장 단계 정책용이며 제품에서는 false다. 별도 좁은 조사 artifact/attestation의 신뢰 연결은 없다. 이 연결을 구현할 필요가 있지만, 물리 단계 전체 policy/서명 workflow를 자동 필수로 확장할 이유는 없다. |
| 요청 의미·원자성 | frozen 입력에 outcome은 없다. `QUARANTINED` disposition만 보고 모든 요청을 포기로 간주하거나 reason.detail을 파싱하지 않는다. 내용이 고정된 절차/명시적 attestation이 포기 의미를 증명해야 한다. 현재 권한→같은 key/body 회수→새 요청 CAS 순서를 지키고 처분 원문/참조·operation 전이·event·원래 응답을 함께 commit한다. | Recovery.RecordDisposition core/runtime/HTTP/gRPC 경로가 없다. 새 필드·정책 이름을 이 문서에서 규범으로 만들어 넣지 않는다. |
| 처분의 한계 | domain은 검증 후 `SETTLED/UNRESOLVED/UNKNOWN/QUARANTINED`를 도출한다. holder/quarantine, 옛 permit/mandate, Run/part/budget, cell blocks/qualification을 복원·해제·진행시키지 않는다. 새 dispatch/Fence/Arm/lookup도 이 처분의 부수효과가 아니다. | 구현 시 기존 invariants와 명시적 시험이 필요한 경계다. |

오래된 원 native capture는 조사 이력으로 유효하다. 이를 현재 상태의 fresh Fact로 꾸미면 안 된다. 반대로 현재 후조건/지지 인계를 **허가**하지 않는 첫 처분에 모든 과거 근거를 현재 sample age로 거부할 이유도 없다. 현재 조건을 주장하는 evidence를 사용할 때만 그 source/generation/clock/quality/age 의미를 원래대로 검증한다.

첫 T5의 `procedure_digest` 검증에 기존 전체 procedure/close signature admission을 반드시 재사용하라는 규범은 없다. 그러나 실제 신뢰 자료가 없는데 hash 존재만 검사하는 것도 충분하지 않다. **제품에 조사 절차/명시적 attestation을 공급·검증하는 좁은 연결이 필요하다**는 것이 현재 결론이다. 구체 assertion ID, 책임자 허용 집합, 조사 절차 문구/인증 방식은 아직 있는 정책처럼 가정하지 않는다.

## 4. 현재 사용 가능한 Case/보고 API와 actor

모두 기존 `{request_key, command}` mutation envelope와 같은 요청의 동일 body/key 회수를 사용한다. 실제 사람이 쓰는 경로는 직접 HTTPS 사용자 세션이다. 현재 인간 보고를 Host/Executor 계정의 role 추가로 대신할 수 없다.

| 동작 | 실제 HTTP / 주요 입력 | 현재 처리와 권한 |
|---|---|---|
| 조회 | GET `/api/v1/overview`, `/api/v1/cases?cell=…`, `/api/v1/case?cell=…&id=…` | 현재 셀 접근권. 원 Work/Run/제한과 Case/procedure records를 읽는다. 성공 capture와 전체 결론을 구별해 표시한다. |
| Case 열기 | POST `/api/v1/cases/open`: cell, optional expected_cell, kind, scopes, procedure ArtifactRef, lead, 원 operation_ids/material_ids | 현재 Operator/RecoveryLead/Host/Executor의 셀 접근권. lead는 실제 active RecoveryLead이며 전체 영향 셀 접근권이 필요하다. operation은 실제 영향 셀 소속이어야 한다. |
| 알림 확인 | POST `/api/v1/cases/acknowledge`: cell, case, expected_case, occurred_at | notification 기록만 추가. 성공·접근·reset·종료·자원 인계·재시작 조건을 만들지 않는다. |
| 외부 사실 보고 | POST `/api/v1/cases/procedure`: cell, expected_cell, expected_case, Record + inline Assertions/그 ref | 인증된 Operator/RecoveryLead. actor와 source가 실제 사람 identity와 일치. source-event/step/UTC/scope/절차 digest/원문 hash/IDs와 값이 결합된다. WorkStarted/Finished는 해당 actor 자신의 보고다. |
| 비운전 준비/소비 | POST `/api/v1/cases/close-preparations`, `/api/v1/cases/close-without-restart` | RecoveryLead, 모든 대상 case의 현재 lead, 전체 영향 셀 접근권. 아래 추가 정책/근거가 실제로 검증돼야 한다. |

관련 소스: [intervention.rs:90](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/intervention.rs:90), [procedure.rs:129](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/procedure.rs:129), [HTTP routes:787](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-api/src/routes.rs:787).

이 시나리오에서 단순 DIAGNOSTIC_ONLY 종료로 옛 mandate를 계속 쓰는 예외는 맞지 않는다. 그 규범 예외는 generation/authority/물리 연속성 상실이 없을 때만 가능하다. 이미 P restart와 제한·옛 permit 세대가 있는 경우에는 FAULT_RECOVERY와 기존 latch 보존을 기준으로 본다. 실제 접근이 없었다는 사실은 그대로 기록하되 가짜 현장 작업을 만들지 않는다.

`OpenCase(FAULT_RECOVERY)`는 셀/공유 자원 closure의 새 epoch·Fence·permit 봉인·mandate 철회를 원자적으로 남긴다. 요청한 좁은 scope보다 현재 cell 단위 closure가 실제 범위다. 미확인 소재 참조/알 수 없는 scope는 scope_uncertain이며 허용 근거가 아니다. Case 생성이 기존 Phase79 recovery context의 cell CAS를 바꾸므로 **이전에 받은 recovery ACK/읽기는 새 case의 현재 Fence/조건 근거로 재사용할 수 없다**. 필요한 후속 Host 통신은 다시 현재 경계를 통과해야 한다. operating rebind 설계는 별도다.

`RecordProcedure`는 실제 외부 변화 사실을 stale CAS에도 보존하고 필요한 latch를 남긴 뒤 승격만 거부한다. HTTP 409/422라도 `facts_recorded`, record ID, transition_error를 읽어야 한다. 같은 fact를 새 key로 보내 과거 단계를 재실행하지 않는다. 알려지지 않은 procedure policy에서는 사실이 남을 수 있으나 상태 승격은 UnsupportedSchema/ESCALATED다. 기록 성공을 절차 승인으로 표시하면 안 된다.

## 5. 절차 수행 후 비운전 종료: 구현된 core 조건과 제품의 선행 빈자리

실제 외부 절차를 수행할 경우 허용된 순서는 다음이다. 이것은 물리 문·격리·토크 조작 지시가 아니라 기록/검증 순서다.

1. 신뢰된 release/package verifier가 **실제 외부 절차 artifact/의존 근거**에 묶인 `procedure::Policy`를 검증·admit한다. Engineer 역할만으로 PASS가 되지 않는다. cell/definition/envelope, case types, entry conditions, 유한 steps/actors, required source evidence, 최대 age가 고정돼야 한다.
2. Case lead가 `ENTRY_CONDITIONS_REPORTED`를 제출한다. 전체 영향 scope, admitted policy, 현재 Host boot/journal/epoch/scopes Fence ACK, 실제 fresh Fact 근거와 entry conditions가 모두 필요하다. 성공 시 PROCEDURE_ACTIVE다.
3. 실제 참여자가 각자 `WORK_STARTED`와 `WORK_FINISHED`를 보고한다. 외부 변화는 옛 personnel/handover를 무효화하고 latch를 추가한다. 이력을 생략할 수 없다.
4. 현재 lead가 정확한 전체 비어 있지 않은 참여자 집합에 대해 `PERSONNEL_ACCOUNTED`와 `HANDOVER_ACCEPTED`를 보고한다. 모든 개인의 종료·비활동·인원 확인·인수가 갖춰지면 REVALIDATING이다. 빈 명단이나 한 명의 종료로 나머지를 추정하지 않는다.
5. 신뢰된 `closure::Policy`가 같은 procedure와 전체 영향 셀의 정의/envelope, 실제 억제·격리·남길 제한 조건에 묶여 있어야 한다. `PrepareClose`는 current cell/case revisions와 **실제 personnel/handover record ID + 평가에 쓰인 Fact evidence ID의 정확한 집합**을 받는다. 임의 ID 추가/누락은 거부한다.
6. clearance 유효시간은 정책 TTL·현재 세션·보고 최대 age/valid_until·조건 evidence 만료의 최솟값이다. 마지막 외부 변화 이후의 관측이며 취득 uncertainty까지 고려한다. 준비는 case/운전 허용을 확대하지 않는다.
7. 같은 현재 lead가 `CloseWithoutRestart`로 소비한다. 권한·CAS·시간·policy·인원·Fence·조건·같은 evidence/context를 재검사한 뒤 대상 Case CLOSED + clearance 1회 소비 + OUT_OF_SERVICE latch + receipt/event를 원자 기록한다. 다른 case/RuntimeRestart 제한, 원 Work UNKNOWN/UNRESOLVED, resource holder/quarantine은 보존한다. Arm하지 않는다.

근거: [procedure advance:475](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/procedure.rs:475), [current Fence 검사:709](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/procedure.rs:709), [closure verify:88](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/closure.rs:88), [prepare/consume:349](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/closure.rs:349).

**제품 선행 빈자리:** `QualificationAuthority::verify_procedure`와 `verify_close_policy`는 기본 false이고 [platformd:16](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-platformd/src/lib.rs:16)는 UnconnectedQualification을 사용한다. 실제 requalification 서명/Host activation 경로가 있다고 이 두 authority까지 구현된 것은 아니다. runtime의 AdmitProcedure/AdmitClosePolicy 명령과 core는 있지만 제품 정책 intake/검증 worker·서명 신뢰 연결이 없다. 실제 제품에서 위 절차 승격/Close 성공을 지금 제공한다고 말할 수 없다.

**무진입 상황의 빈자리:** core Close는 실제 참가자가 비어 있으면 거부한다. 현재 DIAGNOSTIC_ONLY의 무진입 종료 또는 비어 있는 인원 집합에 대한 명시적 외부 부재 확인 경로는 미구현이다. Phase79에서 사람이 장비에 들어가지 않았으므로, close 성공 시험을 만들기 위해 가짜 참여자/작업 사실을 넣으면 안 된다. 좁은 첫 T5 조사 포기는 이 물리 참여자 단계와 분리해야 한다.

core [non_operating_close_preserves_unknown_effect_and_does_not_release_resources:5456](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/tests/transactions.rs:5456)는 UNKNOWN/Run RECOVERY_REQUIRED/resource holder+quarantine 보존을 명시적으로 검증한다. 이 시험의 authority는 테스트 전용 SimulationAuthority이며 제품의 실물 또는 서명 admission 성공 근거가 아니다.

## 6. 자원 인계와 명시적 재개는 별도 후속

현재 일반 `release_resources`는 사람의 Case 승인 API가 아니다. 현재 **Host** identity/session과 등록의 일치, cell ready, 원 permit과 같은 epoch/scopes, 같은 Host boot, `SETTLED + VALID`, operation에 결합된 native evidence가 필요하다. 이어 원 operation/invocation/profile/device_session/Host boot에 상관된 `no-pending`, `control`, `support` 세 GOOD/fresh/true 관측을 검증하고 자원 holder와 quarantine을 해제한다. 각 관측은 native capture 이후이며 원 age/uncertainty 조건을 만족해야 한다. [handover.rs:6](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/handover.rs:6)

따라서 H의 RESULT_CAPTURED 또는 `FileDevice.can_handover=true`만으로 Phase79의 옛 epoch operation을 일반 release에 넣을 수 없다. Host operating rebind가 나중에 해결되어도 원 permit epoch와 blocked cell 조건이 남으므로 그것만으로 해제되는 구조가 아니다. `Case.HANDOVER_ACCEPTED`는 사람/절차 인수 기록이고, 일반 Resource.Release의 세 native handover 관측 또는 T5 자원 해제 transaction과 동일하지 않다.

규범상 후속 T5 자원 해제는 검증된 복구 절차로 현재 상태·잔류 명령·제어권·필요 지지 인계 및 새 admission 조건을 확인하고 **과거 UNRESOLVED를 보존한 새 RecoveryDisposition**을 기록해야 한다. 현재 core에는 이 경로가 없다. 첫 T5에서 이를 흉내 내지 않는다.

규범상 재개 준비는 REVALIDATING 이후 `SetRecoveryPlan`의 검증된 유한 step/actor/guard/visit와 처분, `PrepareRestart`의 새로운 epoch/Fence와 현재 상태 재확인, 그 epoch에 묶인 Clearance/READY, Operator `RestartRun`, 동일 epoch Arm 전체 ACK와 새 mandate/Case 종료/clearance 소비/Run commit 순서다. Case revision 집합은 다른 열린 case/외부 제한을 누락할 수 없다. 원 budget·part/material·operation 이력과 새 activation/continuation 연결은 restart plan이 명시해야 한다. CONTINUE_CORRELATED는 실제 continuation token/지점과 현재 잔류·소재 근거가 있어야 하며 보통의 원 operation 재전송으로 대체하지 않는다. NO_RESUME/RESTART_FROM_ENTRY 의미도 profile의 검증된 선언을 따른다.

현재 P의 [cell_negotiation.rs:492](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-api/src/grpc/cell_negotiation.rs:492)는 SetRecoveryPlan, PrepareRestart, GetRestartPreparation, RestartRun을 명시적으로 Unimplemented로 반환한다. core/runtime의 대응 handler도 없다. HTTP 일반 StartRun은 [operator_start.rs:43](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/operator_start.rs:43)에서 PREPARED Run만 받으므로 PAUSED/RECOVERY_REQUIRED를 재개하는 우회가 아니다. frozen Workflow.AbandonRun도 현재 [grpc/workflow.rs:103](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-api/src/grpc/workflow.rs:103)에서 미구현이다. Case Close를 Run Abandoned로 표시하면 안 된다.

또한 현재 process-change와 qualification activation의 quiescence 검사는 기존 Work의 NONE/UNRESOLVED와 held/quarantined resource를 차단한다. 첫 T5가 생겨도 즉시 requalification으로 재개할 수 없다는 뜻이다. 후속 T5의 검증된 처분/인계를 이 검사와 연결하는 일은 별도 필요하다. 과거 UNRESOLVED 값을 일반적으로 무시하는 완화는 규범상 근거가 없다. [process_change.rs:895](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/process_change.rs:895), [qualification_activation/mod.rs:264](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/qualification_activation/mod.rs:264)

## 7. P03의 검토 가능한 최소 범위와 검증 경계

우선 기존 규범의 **조사 포기만 기록하는 첫 T5**를 구현 범위로 고정할 수 있다. 위 3절의 사람/원문/절차 적용범위·상관·현재 revision 검증과 `UNRESOLVED + QUARANTINED` 원자 기록까지만 필요하다. 전체 물리 절차 admission, 무진입 Close, 자원 RELEASE, Host operating rebind, E 복구, RecoveryPlan/RestartRun을 성공 조건으로 묶지 않는다. 이것은 구현 범위 제안이며 아직 존재하는 제품 기능이나 새 규범 정책 선언이 아니다.

최소 시험에서 확인할 구체 반례는 다음이다.

- Phase79 원본 success capture 및 P publication evidence를 읽은 사람이 명시적으로 조사 포기할 때만 UNRESOLVED를 만든다. capture/ACK만 있는 자동 경로는 그대로 NONE이다.
- evidence 원문 누락, 다른 operation/invocation/profile/설치 소유, 임의 procedure digest, 잘못된 assertion 의미, service identity/역할 철회, stale operation revision은 처분 거부다. 잘못된 요청으로 원 불명 상태를 지우지 않는다.
- 저장 실패는 처분 전체 rollback, commit 응답 유실은 현재 권한을 다시 검사한 같은 key/body로 원래 처분을 회수한다. 다른 key/body나 후발 상충 근거가 과거 결론을 조용히 대체하지 않는다.
- 처분 후 원 Work의 불명/원 native 이력을 보존하고, resource holder/quarantine·permit/mandate·Run/part/budget·cell blocks/qualification·native calls/effects는 그대로다. result에 '운전 재개 가능', '접근 가능', '자원 해제'를 표시하지 않는다.
- 현재 구현된 비운전 Close 시험과 별도로 취급한다. Close는 UNKNOWN/자원 격리를 남기는 Case 종료이며, 첫 T5는 원 operation의 조사 처분이다. 둘을 같은 버튼의 암묵 효과로 합치지 않는다.

검토 중 실제 제품/테스트 코드는 변경하지 않았다. 이 문서는 규범 문언, 현재 구현, 그 사이의 연결 필요 사항을 구별하기 위한 자료다.
