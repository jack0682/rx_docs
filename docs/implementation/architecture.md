# 구현 경계와 선행 설계 연결

초안 v0.1 마감 기준은 [인계 문서](draft_handoff.md)다. 이 문서는 구현 과정의 선행 결정을 함께 보존하므로 과거 후속 계획과 현재 구현을 구별한다.

## 소유권

| 구성 | 위치 | 의존 규칙 |
|---|---|---|
| rx-domain | platform crate | 순수 타입·정규화·조건·상태 전이. 시간·ID 생성·I/O는 호출자가 제공 |
| rx-ports | platform crate | 동기 원자 transaction 경계·저장용 typed envelope. SQLite 타입 노출 없음 |
| rx-storage | platform crate | 로컬 SQLite·writer 소유 lock·CAS·key/event/outbox·snapshot/backup |
| application/Runtime | platform crate | 요청 인증 후 key 조회→신규 요청의 상태/조건/CAS→단일 commit; 실제 Application Processor/단일 writer thread |
| protocol/API | platform crate | frozen codec·Host mTLS client, 로컬 HTTP BFF를 같은 application에 연결. direct terminal mTLS·HTTP/gRPC 연결. 공개 RPC 전체·SSE는 후속 |
| host 관리 도구 | 계획상 platform 소유, 현재 S Host의 prepare/lookup/cancel·E offline 점검 일부 | 실제 설치 교체·복원·전체 조정은 후속. 생산 권한 없음 |
| Host/native/ROS | solutions | 전달 gate·로컬 journal·실제 장비 의미. whole body outcome 쓰기 금지 |
| 공정 원본·변환·BT | solutions | 원본 의미/단계 ID 보존. native UNKNOWN을 자동 retry로 낮추지 않음 |
| UI | solutions | 시각적 편집·역할별 화면. 승인된 API만 요청; 판정 원장 별도 소유 금지 |

rx-ports의 Document는 저장 adapter를 도메인 schema에서 분리하는 envelope다. 공개 API 입력을 검증 없이 이 envelope에 넣는 경로는 만들지 않는다. application은 구체 typed domain을 먼저 검증해야 한다. 현재 저장 foundation만으로 셀 admission/T1 전체가 구현되었다고 주장하지 않는다.

## 앞선 계획에서 유지할 항목

- D2: 단일 P, 복수 셀, bounded queue·동기 writer, 외부 I/O는 transaction 밖. H native gate는 검사/소비/SEND_ENTERED/native 진입을 fence·취소와 직렬화.
- D3: 제품군 패키지+모델/모드 profile; 재사용 공정 원본·현장 binding·resolved plan·검증 기록 분리. case별 복구/재시작 권한은 재사용 패키지에 넣지 않음.
- D4: 두 image와 종료/지지 경계는 유지한다. 선행 systemd/s6 배치안과 별도로, 실제 검증된 초안 composition은 Rust rx-solutionsd supervisor의 기동·관측·역순 협력 종료다. 전체 호스트 agent/설치 교체는 후속이다.
- D5: LAN/현장 자체 계정/등록 단말. React 시각 편집은 RX 원본 작성; native capability는 Host 소유. scoped UI projection은 whole-site control journal과 다른 cursor.
- D6: 계약·모의·실장비·FAT·SAT·운영/사업 인수를 구별. native 효과는 독립 관측으로 검증. 제한적 SETUP의 선행 근거로 시험 범위를 확대.

## 초기 구현 결정

- Rust 1.98.1을 workspace에 별도 설치·고정. 사용자 shell rc 변경 없음.
- rusqlite 0.40.2의 bundled SQLite 사용. 실행 시 linked SQLite 3.51.3 이상 요구. 예전 0.38.0에 포함된 3.51.1은 WAL 수정 미포함이므로 채택하지 않음.
- JSON은 중복 key를 먼저 거부한 후 typed decode. counter는 문자열, enum/필드는 닫힌 집합, 의도는 JCS+domain-prefix SHA-256.
- 조건 tree 방어 한도는 깊이 32/노드 1024. 제품 profile 한도에 반영할 구현 값이며 실제 장비의 시간·반응 성능을 뜻하지 않음.
- SQLite 내부 revision/seq가 signed integer 범위를 소진하면 오류로 차단한다. wire uint64를 실수로 변환하거나 wrap하지 않는다.
- 최초 foundation 검증은 라이브러리 단위의 의미·원자성 증거다. 뒤 단계에서 wire 상호운용을 추가했으며 SIGKILL/power-loss·실물 성능은 아직 별도다.

## Wire 및 실행 경계 구체화

- rx-protocol은 generated Protobuf/gRPC와 strict wire/JSON codec을 소유한다. core에는 prost/tonic을 전파하지 않는다.
- proto/README.md에 서비스 이름·enum 이름·cell snapshot union의 구체 binding을 기록했다. 문서 기준판의 원래 hash는 변경하지 않는다.
- rx-solutions/interfaces는 platform export 도구가 만든 별도 hash-pinned source bundle이다. 다른 레포의 작업 경로에 대한 빌드 의존 없이 C++ 코드를 생성한다.
- rx-runtime의 writer는 SQLite를 직접 알지 않는다. 전용 스레드에서 생성한 application Processor만 실행하고 network/native I/O는 outbox consumer에 남긴다.
- 큐는 실행 중 항목을 포함하여 최대32, 일반24/제어8로 제한한다. 제어8개 burst 뒤 일반 항목을 처리해 일방적 기아를 방지한다. 실제 보호 반응이 이 DB queue를 기다려야 한다는 뜻은 아니다.
- 정상 close는 신규 접수 중단 후 이미 접수한 state command를 drain한다. reply timeout/연결 해제는 commit 취소 신호가 아니다. worker panic에서는 남은 receiver에 미확정/불가를 알리고 새 admission을 차단한다.
- writer enqueue 성공은 메모리 큐 수용일 뿐 외부 ADMITTED receipt가 아니다. application의 T1 durable commit 뒤에만 ADMITTED를 반환한다.
- 조건 평가의 현재 시각은 command를 실제 처리할 때 Clock port에서 얻는다. HTTP 수신 시점의 시각을 큐 대기 후에도 현재 시각으로 재사용하지 않는다.
- 고주기 control sample을 이 writer 큐에 넣지 않는다. 보호/무효화 사건과 일반 최신값 telemetry의 보존·합치기 규칙도 구별한다.

## Application 상태 소유

- rx-application은 설치·현재 자격·run/mandate·part/activation/work·resource/permit를 transaction 경계 안에서 변경한다. wire/storage 구현은 import하지 않는다.
- DB 내부 key는 entity 종류와 canonical identity digest로 만든다. 유효한 긴 외부 Name에 prefix를 붙여 Name 길이 제한을 깨뜨리지 않는다.
- principal namespace는 계정 수명 동안 고정한다. 인증 adapter가 확인한 Identity로 현재 session/principal/단말을 조회하며 caller의 역할 주장을 받지 않는다.
- CreateRun에는 실제 시작 예산이 없다. 첫 StartRun이 예산을 고정한다. 같은 시작의 재시도와 다른 예산의 새로운 의도를 혼동하지 않는다.
- 유한 단계 binding의 activation 유일키는 (run,node,visit)이며 part 관계는 별도 metadata다. part마다 visit=1을 재사용하지 않는다.
- 관측의 원본 evidence와 cell별 condition projection을 분리한다. 같은 원본이 여러 셀에서 쓰일 때 cell별 age 정책 차이를 증거 충돌로 오인하지 않는다.
- 실제 변화의 기록을 남기고도 API 오류를 반환해야 하는 경우, transaction은 오류 처분 값을 성공적으로 commit한 후 바깥에서 오류를 반환한다.
- 현재 Helper API는 공개 RPC 전체 구현이 아니다. 계약 메서드별 추가 필드/권한/key semantics와 실제 Host receipt/evidence 연결을 다음 단계에서 완성한다.

## Host 제어와 native 경계

- rx-solutions/runtime/rx-host는 Rust로 journal/gate를 소유하며, native port의 C++/ROS/SDK 구현은 solutions에 둔다.
- P 업무 authority는 재사용 SDK에서 제외한다. Host는 native receipt와 immutable evidence만 만들고 결과/허가의 상위 판단을 복제하지 않는다.
- native submit은 gate 안에서 수행하지만 동작 완료 대기를 의미하지 않는다. 실제 adapter가 제출 API에서 block할 수 있으면 그 호출이 해소되기 전 새 소유권을 주지 않는다.
- 별도 local protection port는 gate·DB와 분리한다. 실제 장비별 반응·지지·시간 보장은 해당 binding의 실물 검증 대상이다.
- 프로세스 kill fixture는 production binary에 기본 포함하지 않으며 test-harness feature로만 빌드한다.

## 실행 복원 상태의 저장 경계

Run 변경 transaction에서 activation/slot/공정 결정을 수집하고 실제 bytes의 내용 주소 artifact와 현재 RunSnapshot, 제어 사건을 함께 기록한다. artifact 생성 때문에 업무 Run revision을 별도로 올리지 않는다. 조회 시 현재 접근권, 현재 Run과 snapshot cut, 실제 payload의 digest/schema/size·연결을 대조한다.

과거 snapshot은 보존하며 현재 운전 허가로 해석하지 않는다. 로컬 HTTP의 frozen RunView 투영까지 연결했고, 원격 executor의 Session/Cell/GetRun 조회에도 연결했다. Workflow 변경·CommitCheckpoint·artifact 확보·C++ Frame 복원은 후속이다. 자세한 저장 구조와 장기 운전 용량 한계는 [checkpoint artifact 명세](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/CHECKPOINT_ARTIFACT.md)를 따른다.

실행기 세션은 [ExecutorPeer](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/EXECUTOR_PEER.md)로 관리한다. 재접속은 같은 session에 수렴하고, peer boot/binding 교체는 이전 세션 및 관련 운전 권한을 함께 철회한다. 폐기된 boot는 영속 tombstone으로 늦은 재진입을 거부한다. 등록과 transport liveness/readiness를 구별하며, 현재 wire는 Run 조회까지만 활성화했다.

## 실행기 명령과 접수 확인서

공개 BeginPartAttempt/ResolveActivation의 envelope·현재 peer/cell scope·key/fingerprint 검사를 application의 executor_requests에 두고, 실제 상태 변경은 기존 workflow와 공통 transition을 사용한다. 바뀐 mandate/visit/CAS 값을 같은 key로 숨기지 않는다. part/activation의 응답과 Run/checkpoint 변경은 같은 transaction에 저장한다.

신규 Work 생성의 ADMITTED control record seq를 같은 commit의 immutable AdmissionReceipt에 연결한다. P control journal ID는 installation/store generation/view에 결합하며 process boot와 구별한다. 공개 Cell.SubmitOperation의 유한 run envelope/Receipt 반환은 이 접수 근거에 연결했다. Run/activation/part/cell/parent와 중첩 context, 두 CAS를 검증하며 기존 submit transition·dispatcher를 사용한다. 연속 제어·복구 parent는 후속이다.

Operation.Get은 P의 현재 결과/지식/무결성/자원 처분을 그대로 반환한다. SUCCEEDED와 RELEASED를 합치지 않고, 후발 모순은 기존 outcome과 함께 DISPUTED/QUARANTINED로 표현한다. 실제 원격 E→P→별도 모의 H의 양쪽 응답 유실 시험과 native effect 수는 [유한 제출 명세](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/EXECUTOR_SUBMISSION.md)에 기록한다.

## 복원·현재 조회·C++ Frame

Run/ProcessCheckpoint와 checkpoint DTO는 rx-process-contract의 shared data model이다. P의 권한/transaction engine은 수출하지 않는다. 현재 execution snapshot은 별도 P transaction cut에서 run/셀 epoch·scope·현재 work/branch/wait와 허용 여부/이유를 읽는다. 오래된 maintained condition은 새 요청 처리 시 다시 검사한다.

선택적 rx.executor.v1 읽기 binding은 새 fields를 frozen RunView에 몰래 붙이지 않고, 별도 manifest hash로 protobuf/DTO/validator/의미를 고정한다. 기존 Workflow/Cell mutation을 대체하지 않는다. S runtime/rx-executor는 인증된 P endpoint에서 run-owned artifact와 live snapshot만 읽고, 고정 Context identity와 동일 호스트 clock을 확인해 C++ IPC Frame을 만든다.

Frame 현재성은 source CLOCK_BOOTTIME/boot ID와 짧은 local deadline을 함께 사용한다. C++는 source clock을 publish/tick/handoff에서 재검사한다. 이 경계는 data reader/projection이며 실제 BT mutation worker·pending-key journal·branch/wait/checkpoint commit과 두 image 상주 구성은 아직 후속이다.

## S 영속 요청과 유한 worker

S journal은 요청 key/body와 network 진입/응답을 소유하며 P operation·native 결과를 소유하지 않는다. run/recipe/installation/store generation/definition에 고정한 저장소에 PREPARED→EMIT_ENTERED를 선행 commit하고, 그 뒤에만 crate-private client mutation을 호출한다. 같은 요청의 body를 바꾸지 않으며 atomic Resolve/Submit의 ABORTED 확인 뒤에만 새 CAS/key의 다음 generation을 만든다.

현재 P mapping으로 확인한 activation/operation은 별도 observation이다. 받지 못한 RPC reply나 native 성공으로 덮어쓰지 않는다. worker는 실제 C++ request의 Context와 argument를 새 validated snapshot/plan에 대조하고, Resolve 뒤에 새 read cut을 얻어 Submit을 준비한다. 기존 mapping/잘못된 context/권한·시계 만료를 확인한다. 세부 경계와 미지원 요청은 [S worker 명세](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/runtime/rx-executor/JOURNAL_AND_WORKER.md)를 따른다.

## Explicit BT halt와 PauseRun

P의 현재 permit/Arm이 cell epoch/scope에 묶이므로 실행/Arm 중인 run의 pause는 cell/resource closure의 허가 철회·fence를 동반한다. origin은 PAUSED, 다른 영향 run은 RECOVERY_REQUIRED로 둔다. 준비 허가가 전혀 없는 PREPARED run은 자체 상태만 바꾼다. 정상 WAIT/조회 지연과 explicit halt를 구별한다.

Finalized transaction view는 control capture 뒤 projection 조회와 요청 결과 저장만 허용한다. core state를 뒤늦게 변경하는 API를 노출하지 않으면서 PauseRun 응답을 같은 commit의 최종 snapshot으로 고정한다. S pause key는 원래 session/epoch에 고정하고, 다른 명시적 실행 context의 새 halt를 과거 요청과 혼동하지 않는다. [Pause 명세](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/EXECUTOR_PAUSE.md)를 따른다.

## 지속 BT 프로세스 경계

S의 EngineProcess는 고정 release binary를 검증하고 private stdin/stdout으로만 INITIALIZE/STEP/HALT/CLOSE를 교환한다. C++는 한 context의 BT와 operation/branch/wait 연속성 기억을 유지하며, P 검증은 Rust Client·worker와 P authority에 남는다. 초기화만으로 tick하거나 driver를 로드하지 않는다.

PendingRequests는 C++가 한 번 전달한 제안을 결과까지 유지한다. BeginWait 시작과 결과를 구별하고, bounded queue·재시도 간격·우선 pause를 관리한다. 실제 mutation body/key/응답 미확정은 S journal이 보존한다. RunService·직렬 part coordinator·durable stop intent가 이 구성 요소에 연결되어 있다. 전체 P/Host/S process supervision은 후속이다. 세부 계약은 [지속 엔진](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/native/executor/PERSISTENT_ENGINE.md)을 따른다.

## Run/visit 서비스 수명주기

S RunService는 배정 대기와 현재 P view 처리, planner·pending queue·worker 조정을 담당한다. run-scoped stop intent를 node/visit request와 분리해 저장하고, 정상 요청을 동결한 뒤 planner 종료와 P pause 확인을 진행한다. restart 시 stop intent를 먼저 처리하여 자동 기동을 차단한다. 저장 장애의 best-effort P pause는 durability_fault로 구별한다. [서비스 명세](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/runtime/rx-executor/SERVICE_LIFECYCLE.md)의 범위이며 전체 supervisor나 병렬 소재 조정을 대체하지 않는다.

## 직렬 소재 조정

기본 SerialProduction은 선택적 Production.Inspect의 일관된 part/budget 상태를 읽고, frozen BeginPartAttempt와 P CompletePart를 S journal로 연결한다. 완료/중복 처리의 공통 전이는 P에 있다. S는 현재 P 공정 완료를 확인하고 완료를 요청하며, 최신 P part 완료로만 해당 planner context를 retire한다. 같은 run의 다음 visit은 현재 session/epoch/mandate를 유지하며 중간 pause를 만들지 않는다. 최종 run 완료는 P가 결정한다. [조정자 명세](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/runtime/rx-executor/PRODUCTION_COORDINATOR.md)의 직렬 범위이며, 병렬 소재·재시작·실제 material genealogy는 후속이다.


## 셀 공개 상태와 운영 API 전송 신원

Cell은 RX 운영 mode·commissioning 상태를 기록하고 각 Block은 실제 생성 cell revision/관련 case를 가진다. 최초 시작의 최종 Arm/Run/Mandate commit은 셀 mode도 함께 갱신한다. frozen Cell.Inspect와 canonical HTTP 조회는 같은 저장 상태를 투영하며 없는 metadata를 추정하지 않는다. Cell metadata의 schema4와 후속 사용자·단말 binding의 schema5는 이전 decoder의 잘못된 rollback을 차단하면서 기존 문서 bytes를 보존한다.

OPERATOR_API peer는 mTLS 인증·base/cell 협상을 가진 전송 서비스다. 그 서비스의 재접속은 실행기나 run 권한을 바꾸지 않는다. 인간의 사용자 세션·등록 단말을 서비스 호출과 연결하는 단계는 별도이며, 이 서비스에 Executor/RecoveryLead 역할을 붙여 우회하지 않는다. [상태·신원·호환 경계](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/CELL_CONTEXT_AND_OPERATOR_PEER.md)를 따른다.

직접 단말 HTTPS는 검증된 TLS leaf certificate와 사용자 자격을 같은 writer Session에 결합한다. API cookie는 그 단말 인증서에 묶이며, 역할/등록 revision/셀 교집합 검사를 cache보다 먼저 수행한다. 서비스 계정이 인간 보고자가 되는 역할 혼합은 거부한다. [현재 신원 경계](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/TERMINAL_IDENTITY.md)와 SDK source 동기화 검사를 따른다.


## 플랫폼 실행 파일과 process-stop barrier

rx-platformd는 hash로 고정한 catalog/credentials/TLS 설정, 단일 writer, terminal HTTPS와 gRPC를 구성한다. 최초 설치는 임시 DB에서 완성 후 공개하고 재시작 때 catalog를 재적용하지 않는다. 현재 qualification authority는 연결되지 않은 uncommissioned draft다. Linux clock과 실제 process/socket을 사용하지만 장비 Host/driver를 기동하지 않는다.

Runtime lifecycle은 SERVING→STOP_REQUESTED→STOP_COMMITTED다. stop 요청은 먼저 새로운 authority를 막고 기존 cell 권한을 철회한다. API drain 뒤 미결 상태를 보고하고 writer를 닫으며 physical_shutdown_assessed=false를 유지한다. 이것을 전체 현장 종료·지지 인계 확인으로 쓰지 않는다. [기동/종료와 이미지 범위](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-platformd/README.md)를 따른다.


## 솔루션 자사 스택과 dormant image

자사5개/전이3개의 고정 source에서 ROS42개 package와 정책 자산을 설치한다. Rust executor/compiler와 production BT engine, UI bundle을 함께 담되 기본 프로세스는 읽기 전용 software diagnostics뿐이다. Native ELF·정책·runtime 파일 hash를 검사하고 장비를 자동 기동하지 않는다. APT inventory·profile metadata·실물 qualification을 구별한다. [이미지 범위](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/dependencies/NATIVE_IMAGE.md)를 따른다.
