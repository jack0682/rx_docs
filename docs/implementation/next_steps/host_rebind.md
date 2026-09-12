# phase75: P 재시작 뒤 Host producer 재연결과 명시적 rebind

검토 기준: `/Users/ojaehong/RX_automation/rx_ws/rx-platform`의 HEAD `1970ab3` 및 진행 중 phase75 작업 트리. Host 측은 같은 workspace의 `rx-solutions` 현재 소스를 읽었다. 이번 작업은 코드·규범·기존 시험의 읽기 검토이며, 제품 수정·빌드·시험 실행·서버 기동·DB 조작·장비 접근은 수행하지 않았다. 아래 API와 상태 이름은 제안이며 현재 구현된 API로 제시하지 않는다.

## 1. 결론

현재 구현은 같은 P runtime 안의 동일 Host 재접속만 자동 회수할 수 있다. P가 재시작하면 H의 boot와 두 journal이 그대로여도 producer의 P session은 새로 발급되지만 `host/` 등록과 `host-link-*` 기록은 이전 session을 계속 가리킨다. 이 불일치를 명시적으로 해소하는 제품 경로가 없다. 등록 검사를 단순히 삭제하거나 DB의 session만 바꾸는 방식은 오래된 grant·source generation·receipt까지 현행 권한으로 오인하게 만든다.

권장 첫 범위는 **동일 Host boot·delivery/evidence journal·source generation이 유지된 P-only restart**에 대한 명시적 rebind다. 인증된 증거 수신, 기존 operation의 조회·재조정, 새 제어 연결 등록을 분리한다. 새 등록 완료 상태도 미자격이며 Run·mandate·permit·Arm·qualification·블록 해제를 복원하지 않는다. H 또는 device 재시작, journal 교체와 인증 주체 변경은 별도의 continuity/gap/인계 절차가 필요하며 이 좁은 경로가 자동 채택하지 않는다.

## 2. 정확한 현재 원인과 도달 경로

1. [engine/mod.rs:111](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/mod.rs:111)에서 P 재개방은 runtime_boot를 새 값으로 바꾼다. 기존 cell은 RuntimeRestart로 invalidation되고 phase75의 origin 기록과 기존 qualification root suspension이 이어진다. `host/`와 producer/link 이력은 보존된다.
2. H publisher가 기존 peer_boot·evidence journal·인증 binding으로 Session.Open을 다시 호출해도 [producer.rs:52](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/producer.rs:52)의 `session.runtime_boot == meta.runtime_boot`가 거짓이다. 이전 session을 inactive로 만들고 새로운 producer session을 저장한다. 새 producer의 negotiated `cells`는 빈 map이므로 Cell.Open도 다시 필요하다. 같은 runtime에서 동일 조건으로 재접속하면 기존 session을 그대로 반환한다.
3. 이때 [producer.rs:66](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/producer.rs:66)는 **session 재발급의 원인을 구별하지 않고** 해당 Host가 등록된 셀에 DeviceRestart invalidation을 추가한다. P-only restart에도 RuntimeRestart 뒤 DeviceRestart 블록·추가 epoch가 생긴다.
4. ConnectionService는 새 producer로 현재 cell을 읽고 pinned P→H TLS를 연 뒤 bootstrap snapshot을 취득한다. [connection.rs:68](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-host-client/src/connection.rs:68)에서 PrepareHostLink를 호출한다. 이전 link는 producer_session/platform_session/epoch 등이 달라 회수 조건을 통과하지 못한다.
5. [host_link.rs:123](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/host_link.rs:123)의 이전 등록 비교가 `previous.session != producer.session`에서 ContinuityUnproven을 반환한다. 같은 Host의 다른 셀 등록도 [host_link.rs:147](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/host_link.rs:147)에서 모두 같은 session이어야 한다. grant의 만료를 기다려도 이 비교는 계속 실패한다.
6. prepare만 우회해도 [host_link.rs:367](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/host_link.rs:367)의 commit 검사와 [configuration.rs:187](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/configuration.rs:187)의 `register_host`가 다시 거부한다. renewal도 [host_link.rs:606](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/host_link.rs:606)과 627행 이후에서 옛 producer/plan/registration의 완전 일치를 요구한다.
7. ConnectionService는 Attention 후 최대 2초 간격으로 초기 연결을 재시도한다. 등록 성공 뒤에야 dispatcher, observation reader, configuration/qualification worker를 만든다([connection.rs:327](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-host-client/src/connection.rs:327)). 따라서 현재 경로는 자동으로 빠져나오지 못한다. 이미 Bound된 서비스도 변경된 incarnation을 채택하거나 replacement grant를 자동 획득하지 않는다(390–397행).

세 식별자를 구별해야 한다. `producer_session`은 H→P evidence 인증 session, `platform_session`은 P→H 제어 RPC 인증 session, `HostRegistration.session`은 첫 번째 producer_session이다. 한 값을 다른 세션의 값으로 채우는 보정은 해결책이 아니다. Host grant 내부에는 다시 P→H caller.session이 결합된다([S grants.rs:76](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/runtime/rx-host/src/gate/grants.rs:76)).

## 3. 복구 경로에 추가로 남는 두 장애물

### 증거 수신은 재등록 없이 가능하지만 조회 worker는 막혀 있다

[evidence.rs:43](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/evidence.rs:43)의 네트워크 Publish는 새 인증 session, 동일 journal, 명시적 cell 협상을 검사하며 현재 HostRegistration.session 일치를 요구하지 않는다. 동일 evidence journal의 retained record는 새 producer session으로 기존 inbox cursor부터 계속 받을 수 있다. 새 session이 생겼다는 이유로 evidence cursor를 0으로 초기화하면 안 된다.

반면 원 operation의 receipt가 P에 없거나 현재 native 상태 확인이 필요한 경우에는 현재 dispatcher가 아직 생성되지 않는다. `plan_reconciliation`도 [reconciliation.rs:111](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/reconciliation.rs:111)에서 옛 등록 session을 요구하고, delivery 계획은 [delivery.rs:123](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/delivery.rs:123)에서 같은 검사로 막힌다. `prepare_host_link` 자체는 pending operation/permit가 하나라도 있으면 Busy다. 그러므로 “pending을 먼저 해결해야 rebind 가능”만 추가하면 **조회에 rebind가 필요하고 rebind에 조회 완료가 필요한 순환 대기**가 생긴다.

안전한 해법은 grant 없는 제한된 복구 조회 경로다. 기존 work의 host·operation·invocation·delivery journal에 결합한 read ticket을 P writer가 만들고 pinned HostClient가 GetReceipt/Reconcile을 실행하도록 한다. 결과는 기존 T2 inbox/receipt 규칙에 넣는다. 이 ticket으로 AcquireGrant, Prepare, Authorize, Arm, 새 cancel invocation, resource release를 호출할 수 없어야 한다. 자동 handover/resource release를 포함하는 기존 dispatcher 전체를 먼저 기동하는 방식도 피해야 한다.

### DeviceRestart 블록은 RuntimeRestart origin 채택만으로 해제되지 않는다

phase75 runtime restriction 조회·채택은 RuntimeRestart와 해당 origin digest에 한정된다. [qualification_activation/mod.rs:310](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/qualification_activation/mod.rs:310)의 owned_clear는 각 블록의 `changeblockowner`를 요구한다. 현재 producer의 DeviceRestart invalidation은 해당 owner를 만들지 않는다([invalidation.rs:228](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/invalidation.rs:228)). 새 rebind가 session만 바꾸면 이 블록은 남으며 자격 활성화가 완결되지 않는다.

P-only restart의 신규 처리에서는 `old.peer_boot/journal/authentication_binding`이 모두 같고 old session의 runtime_boot만 이전 P인 경우를 별도 원인으로 기록해야 한다. 이미 존재하는 RuntimeRestart origin을 참조하고 DeviceRestart를 허위 추가하지 않는 방향이 적절하다. 이것은 운영 권한을 보존하는 예외가 아니다. 새 session과 재협상은 여전히 필요하고 RuntimeRestart 제한·새 fence·재검증은 유지한다. 실제 Host/device/인증 변경은 제한을 계속 생성하되 별도의 명시적 origin·scope·복구 근거를 가져야 한다. 이미 기록된 DeviceRestart 블록을 원인 추정만으로 삭제하거나 RuntimeRestart로 다시 써서는 안 된다.

## 4. 기존 계약상 유지해야 하는 사항

- [base 02 §7](/Users/ojaehong/RX_automation/rx_ws/rx_docs/docs/contracts/v1.0/02_identity_durability_recovery.md:109): P-only restart는 DB·Host receipt·증거 회수와 fence 재조정이며 원 operation ID를 유지하고 자동 Run 재개를 하지 않는다. H restart는 volatile grant/control/sample/validity 복원을 금지한다.
- [base 03:179](/Users/ojaehong/RX_automation/rx_ws/rx_docs/docs/contracts/v1.0/03_data_and_protocol.md:179): NOT_FOUND는 살아 있는 동일 Host journal에서만 의미가 있다. SEND_ENTERED는 조회·조정 대상이며 새 생산 호출로 바꾸지 않는다.
- [base 03:183](/Users/ojaehong/RX_automation/rx_ws/rx_docs/docs/contracts/v1.0/03_data_and_protocol.md:183): delivery journal과 evidence outbox journal의 seq 공간을 섞지 않는다. 같은 evidence seq의 동일 내용은 중복 ACK, 다른 내용은 integrity conflict, 누락은 GAP이다.
- [base 03:282](/Users/ojaehong/RX_automation/rx_ws/rx_docs/docs/contracts/v1.0/03_data_and_protocol.md:282): 역할·권한을 구별하고 인증서 교체도 재협상과 별도 권한 철회를 따른다. 오류 처리기가 새 key·새 명령·해제를 임의 승인하지 않는다.
- [cell 04:112](/Users/ojaehong/RX_automation/rx_ws/rx_docs/docs/cell_operations/v1.0/04_protocol_integration_ui.md:112): 최대 epoch·block을 후퇴시킬 수 없고 FenceReceipt는 RX gate 기록이며 물리 정지·지지·native queue 해소의 증거가 아니다.
- [cell 04:126](/Users/ojaehong/RX_automation/rx_ws/rx_docs/docs/cell_operations/v1.0/04_protocol_integration_ui.md:126): P crash 뒤 mandate/permit를 자동 살리지 않는다. 백업 복원은 P/H 최대 epoch 교차확인과 새로운 epoch가 필요하며 보통의 rebind와 구별한다.
- [cell 03:74](/Users/ojaehong/RX_automation/rx_ws/rx_docs/docs/cell_operations/v1.0/03_intervention_recovery_change.md:74): 현지 보호 반응·지지·잔류 명령을 조사한다. 권한/장비/물리 연속성 상실을 단순 응답 지연으로 낮추지 않는다.

현재 설계는 기본 wire의 grant 의미를 변경할 필요 없이 P 관리 기능과 내부 worker를 추가할 수 있다. 새로운 public RPC를 제공한다면 strict schema, capability 협상, revision/manifest 검토가 별도로 필요하다. 기존 규범을 구현 편의로 완화할 대상은 아니다.

[base 02 §1·§4](/Users/ojaehong/RX_automation/rx_ws/rx_docs/docs/contracts/v1.0/02_identity_durability_recovery.md:16)의 단일 Runtime·durable 최대 fence 전제도 유지한다. 새 연결 발견이나 이전 연결 timeout만으로 이전 P의 소유권 종료를 증명할 수 없다. 복제된 DB·다른 store_generation·병행 P owner는 이 rebind 범위가 아니다. P와 H가 기존 shared monotonic clock 조건을 만족하지 않는 OS/호스트 재시작도 현재 freshness 검사에 맞춰 별도 복구로 분류한다.

## 5. 최소 제품 API·writer·worker 흐름 제안

아래 경로는 UI용 **제안 명칭**이다. 브라우저가 Host endpoint, certificate, snapshot 또는 실제 sender 신원을 임의 제출해서는 안 된다. P 설정의 Host pin/endpoint와 실제 양방향 인증만 사용한다.

1. **조회** — `GET /api/v1/host-rebind-context?host=...`: 현재 producer의 revision/session/Host boot/evidence journal, 이전 전체 Host registration들의 revision/digest, old/new P runtime, current applied Change root, 관련 block origin, 원 operation·retained resource·미완료 link/grant request를 반환한다. 새 snapshot은 내부 pinned reader가 얻어 freshness와 취득 시점을 기록한다. 등록 단말의 Engineer/Verifier/ReleaseManager 중 읽기 권한과 전체 cohort 접근권을 검사한다.
2. **명시적 제안** — `POST /api/v1/host-rebinds`: 새 request key, mode=`P_RESTART_SAME_HOST`, 이전/후보 identity digest, expected registration/cell revision, 이유를 받는다. 서버가 Host 전체 소속 셀과 공유 scope/resource closure를 계산한다. 기존 runtime origin을 결합하고 `PROPOSED` receipt를 저장한다. 이 단계는 snapshot을 수집·비교할 뿐 grant를 만들지 않는다.
3. **검토·승인** — `POST /api/v1/host-rebind/authorize`: 등록 단말의 ReleaseManager가 구체 proposal digest와 expected revision을 선택한다. transport identity 전환과 grant 재획득을 승인하는 의미만 갖는다. 자격·운전·블록 해제 승인이 아니다. 다중 소유 후보·실제 boot/journal/source 변화·missing old authority 근거가 있으면 거부하고 명시적 복구 사건으로 남긴다. 반복 연결 callback이 대신 승인하지 않는다.
4. **필요한 원 기록 조회** — 승인된 동일 Host incarnation에 한해 제한된 read ticket으로 기존 operation의 receipt/evidence를 회수한다. H의 PREPARED tombstone/취소가 필요하면 별도 현재 권한과 기존 취소 계약을 따르는 명시 요청으로 수행한다. SEND_ENTERED/NativeAccepted 또는 P UNKNOWN, retained resource/미해결 사건이 있으면 control binding은 `RECONCILIATION_REQUIRED`로 남긴다. 읽기 결과 없음/timeout은 미실행이나 자원 해제로 판정하지 않는다.
5. **기동 준비와 fence** — 모든 필요한 근거가 준비되면 writer가 `READY_TO_BIND` 계획을 원자적으로 저장한다. 이전 registration revision, producer revision/session, P runtime/store generation, 각 cell config/epoch/scopes/block set, 각 Host journal, source generation, native/ownership 관측, grant TTL과 원 send time을 묶는다. resource fence는 P의 durable 최대와 H snapshot 최대의 max+1이며 새 fence/grant request ID를 외부 호출 전에 저장한다. old producer/session 또는 다른 active rebind가 다시 나타나면 계획을 자동 덮어쓰지 않고 거부한다.
6. **기존 Host gate 호출** — P 내부 worker가 같은 계획의 FenceCell을 전송하고 원 request ID의 정확한 ACK를 회수한다. 이어 AcquireGrant를 호출한다. S의 [grants.rs:52](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/runtime/rx-host/src/gate/grants.rs:52)는 실제 can_handover와 pending native entry를 확인하고 durable 최대 fence보다 큰 값을 요구한다. P의 snapshot만으로 이 검사를 대신하지 않는다. 같은 요청 재시도는 원 expiry/send time을 보존한다.
7. **원자적 등록 전환** — exact 현재 proposal/producer/등록 revision·epoch·두 journal·fence·grant receipt·source generation·freshness를 재확인한 후, 전체 Host cohort의 새 registration과 새 link plan/current pointer·transition receipt를 같은 writer transaction으로 저장한다. 이전 등록/plan/receipt는 append-only 이력으로 남긴다. 현재 등록의 session만 바꾸고 이전 grant/link receipt를 재사용하지 않는다. 여러 셀의 중복 resource grant를 안전하게 한 계획으로 처리하지 못하면 첫 구현은 해당 조합을 거부해야 하며, 셀별로 partial rebind해서는 안 된다.
8. **결과와 후속 작업** — `BOUND_UNQUALIFIED`가 되면 새 등록을 사용하는 관측·메타데이터·증거 작업을 연결한다. 기존 적용 Change root가 현재 구성을 보유하면 재사용한다. compiled bootstrap이고 root가 없을 때만 명시적 REVALIDATE_CURRENT의 독립 영향 검토·stage·fence·Host metadata ACK를 거친다. 그 후 새 재검증 보고서·독립 승인·Host qualification ACK·정확한 owned block 해제·명시적 activation을 완료해야 한다. 새 Run 시작은 그 이후 별도 사용자 동작이다.

API 조회·lookup·cancel도 필요하다. 동일 key/동일 proposal은 최신 영속 상태를 회수하고 의미 변경은 KEY_CONFLICT다. 송신 전 취소와 이미 Fence/Grant가 진입한 후의 취소를 구별한다. 송신 뒤 취소는 “기존 권한 복원”이 될 수 없고 read/receipt reconciliation을 남겨야 한다. 응답 유실 뒤 새 rebind key를 자동 생성하지 않는다.

## 6. 구체 반례와 필요한 인수 시험

| 재현 조건 | 요구 결과 |
|---|---|
| 정상 연결·등록 뒤 P만 재시작, H boot/양 journal/device source 그대로 | producer는 새 P session으로 협상된다. 기존 Run/Arm/permit는 되살아나지 않는다. 명시 승인 전 자동 등록은 없고, 승인 뒤 새 fence/등록만 완료되며 qualification은 미복원이다. |
| 같은 P runtime에서 동일 인증/boot/journal의 Open 응답만 유실 | 동일 producer session을 회수한다. 새 epoch나 rebind proposal을 만들지 않는다. |
| P-only 재시작인데 새 DeviceRestart 블록을 추가하는 현재 분기 | 원인을 분리한 신규 동작은 기존 RuntimeRestart origin에 결합한다. 이미 존재하는 DeviceRestart 기록을 이름 변경·삭제하지 않는다. |
| 등록 Host 하나가 셀 A/B에 걸쳐 있는데 A만 새 session으로 전환 요청 | 전체 cohort 검증/CAS로 거부하거나 전부 함께 전환한다. A의 새 grant와 B의 옛 소유권이 겹치지 않는다. |
| 같은 Host principal로 다른 boot 또는 auth binding 두 후보가 번갈아 접속 | 단순 last-open-wins를 control ownership으로 승격하지 않는다. 후보 교체는 기존 proposal/current producer revision을 stale로 만들고 explicit conflict를 표시한다. 이전 session의 늦은 commit은 거부한다. |
| 같은 H boot인데 delivery 또는 evidence journal이 달라짐 | 잘못된 복원/세대 모순으로 ContinuityUnproven. snapshot이 비어도 일반 rebind로 채택하지 않는다. evidence gap incident와 별도 원장 복원 절차가 필요하다. |
| H 재시작, journal은 보존되나 PREPARED/SEND_ENTERED 작업이 존재 | 원 operation/permit/invocation ID로 읽고 상태를 유지한다. grant 만료나 빈 새 메모리만으로 미실행·새 owner를 인정하지 않는다. |
| P UNKNOWN인데 H는 RESULT_CAPTURED이고 publisher ACK가 유실됨 | 새 session에서 같은 evidence journal/seq를 재전달하여 기존 T2로 회수한다. 결과 사실을 받아도 quarantined resource와 연속성 상실이 자동 해제되지 않는다. |
| H capture는 있지만 P invocation receipt가 없음 | evidence는 correlation-awaiting-receipt로 보존한다. 제한된 GetReceipt 경로로 원 delivery journal의 receipt를 회수해야 하며, new Prepare/Authorize로 receipt를 만들지 않는다. |
| old session의 지연 Publish vs 새 session의 동일 journal 재전달 | old session 요청은 인증 거부. 새 session으로 보내진 원 journal의 동일 seq/동일 bytes는 중복 ACK, 다른 bytes는 dispute. cursor를 초기화하지 않는다. |
| rebind 승인 직후 source generation/epoch/block 또는 producer가 바뀜 | 전송 직전/commit currentness 검사에서 거부. 기존 승인으로 새 generation을 자동 따라가지 않는다. |
| fence/grant native-free RPC 성공 뒤 P commit 응답 유실/재시작 | durable plan의 원 request ID·send time으로 receipt를 회수한다. 새 key/새 fence를 무조건 더 만들거나 TTL을 늦은 회수 시각으로 연장하지 않는다. |
| H snapshot.epoch가 P보다 큼 또는 P backup rollback | 기존 일반 rebind의 StaleEpoch를 유지한다. 임의 max 보정 대신 명시적 복원에서 P/전체 관련 H 최대 epoch와 journal을 확인한다. |
| rebind는 완료되었으나 OperatorHold/open case/UNKNOWN/다른 owner 블록 존재 | 화면은 transport bound와 운전 가능을 구별한다. qualification/Arm/Start는 각각 기존 차단을 유지한다. |

기존 시험은 동일 runtime producer 재접속의 동일 session 회수·재협상·옛 session 거부([transactions.rs:1633](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/tests/transactions.rs:1633)), 최초 bootstrap의 durable plan/commit loss 회수와 readiness 미생성(6068행), 잘못된 incarnation/pending/snapshot 거부(6111행), 동일 boot의 delivery journal 변경 거부(6135행)를 다룬다. 실제 P 재시작→새 producer→기존 등록 rebind→동일 구성 root 재검증→새 qualification까지 완주하는 제품 경로는 이 시험들로 입증되지 않는다. 새 기능은 위 실패 경계를 포함한 제품 P/H 모의 통합시험으로 검증해야 하며 실물 인수로 표현하면 안 된다.
