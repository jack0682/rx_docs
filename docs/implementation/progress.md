# 구현 작업 기록

## 2026-09-10 · 착수

- 기존 규범 8개 파일의 SHA-256과 두 protocol manifest 일치 확인.
- 신규 두 레포와 제품 소스가 없음을 확인. 이전 세부 계획은 문서 구현 완료로 취급하지 않음.
- Docker Desktop Linux arm64 engine 사용 가능. Rust는 미설치여서 workspace 전용 toolchain 설치 시작.
- 사용자 결정: Linux 현장 PC/LAN, 등록 조작 단말, 현장 계정, 시각적 편집기, 호스트 관리 도구.
- 다음: 순수 domain 계약 표현·정규화·상태/조건 불변식과 저장 경계부터 구현.

## 2026-09-10 · 순수 domain과 저장 foundation

- 두 로컬 Git 레포를 codex/initial-draft에 생성. 외부 remote/push/장비 실행 없음.
- platform에 rx-domain / rx-ports / rx-storage 구현. core의 시간·ID 생성도 바깥에서 주입하도록 정리.
- frozen CV01–03, strict JSON/oneof/counter, UNKNOWN/후발 모순, 관측 age/source/세대, 예산·scope epoch 19개 시험 통과.
- 원자 rollback·CAS·요청 key 보존·outbox tombstone·snapshot cut·writer lock·온라인 backup 8개 시험 통과.
- 총 27개 시험 통과. cargo fmt 적용, clippy --all-targets -D warnings 통과.
- bundled SQLite 실제 소스 3.53.2 확인. 시작 시 3.51.3 이상 검사. 기존 0.38/rusqlite + SQLite 3.51.1 선택은 수정됨.
- 두 규범 기준판 복사본과 원본 8개 파일 hash 일치. 규범 본문 수정 없음.
- solutions 필수 자사 5개 레포의 정확한 원격·HEAD·clean 상태 재확인 후 robotis.repos 고정. 전체 전이 의존 lock·빌드는 아직 미완료.
- 시험 출력: references/implementation/phase01_checks.txt. 이 결과는 라이브러리 의미·저장 원자성의 범위다. 전체 T1/cell admission, gRPC/C++ 상호운용, 프로세스 강제 종료·실물 검증을 대신하지 않는다.

### 다음 작업

1. frozen Protobuf/셀 타입과 strict wire decoder, 타입/상태 원본의 직렬화·복원 검증.
2. application의 실제 셀·run·command 상태 소유와 단일 writer actor. Repository 위에 전체 T1–T5와 조건/예산/자원 CAS 결합.
3. solutions Host journal·모의 native endpoint·executor 연결. SEND_ENTERED 전후 실제 프로세스 장애와 응답 유실 검증.
4. 패키지·UI·인증·두 image·관리 도구·통합 인수까지 requirements 전체를 계속 구현.

초안 전체는 아직 미완료다. 이 checkpoint로 목표 범위를 축소하지 않는다.

## 2026-09-10 · v1 wire binding·C++ 상호운용·writer 실행 기반

- rx-protocol 추가: 두 Protobuf schema, 583개 필드 의미 alias, 생성된 Rust gRPC client/server 타입.
- rx-domain에는 통신 의존을 추가하지 않았다. wire→domain 변환은 rx-protocol 바깥 경계에서 수행한다.
- 문서 원본에서 독립적으로 추출한 403개 field 번호·타입·optional/repeated와 compiled descriptor 일치 확인.
- proto3 기본 parser 이전에 미지 필드, 중복 singular/oneof, 미지/명시 UNSPECIFIED enum, 잘못된 wire type, overflow/truncation, 비유한 실수를 거부.
- JSON은 일반 ProtoJSON 대신 RX 규약의 snake_case·hex Digest·문자열 uint64·명시 false/zero·닫힌 oneof를 사용. CV01 digest 보존 확인.
- 실제 loopback gRPC 시험에서 잘못된 bytes가 업무 handler에 도달하지 않음을 확인. 이 시험은 인증/mTLS 시험이 아니다.
- solutions에 독립 C++ strict parser와 CMake protocol target 추가. 프로토콜 source bundle의 hash를 빌드 전에 검사.
- Linux arm64 C++ Protobuf 3.21.12로 17개 positive/negative fixture 통과. Rust→C++→Rust 왕복 후 CV01 digest·uint64 최대값·optional zero·Cell.StartRun message 보존.
- 변조된 protocol bundle의 빌드 전 거부 확인. 검증용 image ID: sha256:efb3b752bd6f7d69dadf038330511997d4e5f3013302355e76a03e15e886525d.
- Operation/RunBudget의 저장 상태 복원 검증 추가. UNKNOWN·DISPUTED·소비 이력을 보존하며 모순/중복된 저장 상태를 거부.
- rx-runtime writer 추가: 전용 state thread, 전체 처리 중 요청 최대32(일반24/제어8), 제어 burst8 후 일반 처리, enqueue/close 직렬화, drain·panic 차단. Processor가 command 우선순위를 결정하며 client 입력에 priority를 받지 않는다.
- 응답 receiver 폐기 후에도 실제 SQLite commit이 남는지, 일반 부하가 제어8개 공간을 침범하지 않는지, worker panic 때 자동 replay 없이 차단하는지 시험.
- Rust 전체47개 시험 통과. 마지막 변경 후 writer3개 재검증 및 workspace clippy --all-targets -D warnings 통과.
- 출력/소스 hash 증거는 references/implementation/phase02_checks.*에 보존.

### 구현 바인딩 결정과 남은 범위

- 문서의 Session/Evidence는 message와 logical service 이름이 겹친다. 실제 IDL service에 Service 접미사를 붙이고 모든 generated client/server에 동일하게 적용했다. enum 상수에는 충돌 방지 prefix를 쓰며 RX JSON token과 wire 번호는 유지했다.
- CellSnapshot의 typed union을 SnapshotEntity(base_entity=1/cell_entity=2)로 구체화했다. 원문 manifest와 IDL/source bundle hash는 별도로 관리한다.
- strict wire 검사는 인증·필수 업무 필드·profile/현재 조건 검사를 대신하지 않는다. 각 실제 application/RPC handler의 검증은 다음 단계다.
- C++ 결과는 message 상호운용 증거다. C++ Intent JCS/digest 계산, gRPC Host, native journal·gate는 미구현.
- writer의 Processor는 현재 실제 업무 engine이 아니라 실행 경계다. 전체 T1–T5/cell admission, key/slot/budget/resource의 공동 transaction을 실제 command handler로 연결해야 한다.
- 다음 우선 작업은 rx-application의 설치·셀·run·명령·권한 state ownership과 Host handshake/outbox/evidence. 이후 패키지/BT/계정·UI/자사 전체 빌드/제품 image/설치복원까지 계속한다.

## 2026-09-10 · 실제 application state와 T1

- rx-application 추가. SQLite/Protobuf/ROS를 의존하지 않고 rx-ports transaction을 사용한다.
- 구현을 identity/access, configuration/admission, observation, workflow, dispatch, invalidation, request identity 모듈로 분리했다.
- principal/현재 session/단말 certificate binding을 저장 상태로 대조. 운영 요청의 key 조회 전에 현재 접근권 검사.
- CreateRun은 예산 없는 PREPARED draft를 만든다. StartRun에서 목적·예산 단위·한도를 고정하며 같은 key의 다른 예산은 충돌이다.
- StartAttempt는 run의 pending slot을 예약하고 모든 Host의 동일 epoch/boot Arm ack 이후에만 mandate·EXECUTING을 commit한다. 시작 준비 기한과 origin 권한/단말을 재검사한다.
- PartAttempt는 한 번만 예산을 소비하고 activation은 (run,node,visit)에 유일하다. 현재 유한 단계 binding에서 visit는 run 전체의 part ordinal을 사용한다.
- T1에 key/intent·activation slot·run CAS·전역 자원 예약·permit·outbox·사건을 결합했다. 실패 전 rollback과 commit 후 응답 유실을 실제 SQLite로 시험했다.
- permit 만료는 envelope TTL, grant 유효 기간, 사용한 관측의 유효 기간 중 가장 이른 시각으로 제한한다. 조건 ANY는 유효한 witness를, ALL은 전체 근거의 가장 이른 기한을 사용한다.
- 중단은 공통 resource/zone의 연결 범위로 전파한다. 공유 자원을 쓰는 셀은 함께 차단하고 독립된 셀은 계속 실행할 수 있다.
- 미전송 outbox를 원자적으로 VOIDED한 작업은 NOT_EXECUTED로 기록하되 자원은 격리한다. 이미 emit에 진입한 작업은 불명 재조정 경로로 남긴다.
- 동일 observation ID의 충돌이나 source generation 변화는 incident/무효화를 commit한 뒤 오류를 반환한다. 오류 응답 때문에 실제 변화 기록이 rollback되지 않는다.
- Runtime 재시작은 세션·mandate·permit를 되살리지 않는다. run 소비량을 보존하고 새 epoch/fence/차단 상태로 복원한다. 현재 검증 catalog와 맞지 않는 qualification은 이력에 남기고 활성 자격에서 제거한다.
- application18개 + 조건 witness1개 시험 추가. Rust 전체66개 시험·workspace clippy -D warnings 통과.

### 이번 단계의 한계와 다음 작업

- Host 준비/lease/Arm은 테스트의 검증된 입력이다. 실제 Host native gate·전달/evidence journal·gRPC 양방향 연결은 다음 단계다.
- 첫 resolved workflow는 유한 dependency steps다. 일반 분기·반복·하위 공정·BT compiler/체크포인트의 전체 의미는 아직 미완료이며 범위에서 제외하지 않는다.
- qualification 검증은 in-memory catalog port와 SimulationAuthority 시험이다. 실제 서명/보고서 validator·physical qualification은 미완료다.
- 공개 RPC와 application DTO의 전체 mapping, auth credential 검증, operator recovery/change/clearance, native 결과 T2/취소/T3–T5, 전체 UI와 제품 배포는 계속 남아 있다.
- 후속 우선순위: Host journal과 native-once gate → 모의 장비의 실제 Prepare/Authorize/Evidence 교환 → application 결과·자원/복구 → 공개 API·패키지/BT·UI·제품 image/관리 도구.

## 2026-09-10 · Host journal·native gate·프로세스 강제 종료

- solutions Rust workspace와 rx-host 추가. Host의 제어/기록은 Rust, ROS/SDK native 접근은 C++ 경계로 유지하는 구현 결정을 기록.
- 공통 SDK를 producer에서 export하고 46개 source 파일의 hash/inventory를 검증. P 업무 engine인 rx-application은 Host SDK에 포함하지 않음.
- Host delivery journal과 evidence outbox의 ID/순번을 분리했다. 같은 SQLite transaction에 permit 소비와 SEND_ENTERED를 저장한다.
- caller/session, binding/intent digest, permit 전체 내용, purpose/parent, Host boot, grant/fence, epoch/scope, local guard와 expiry를 대조한다.
- 같은 gate를 native 제출 진입까지 유지한다. 저장 이후 시간이 지난 경우 native 진입 전 유효성을 재검사한다.
- grant renewal replay는 유효 기간을 연장하지 않음. 같은 fence의 새 grant를 거부. Fence/Arm의 durable request receipt를 재사용하여 지연된 재전송이 새 상태를 지우지 않음.
- PREPARED를 새 permit로 검토·재결합할 때 이전 permit ID를 영구 폐기. SEND_ENTERED 뒤에는 조회/근거 회수만 수행하며 native 자동 재호출 없음.
- Prepare보다 먼저 온 취소/void 요청을 영속 tombstone으로 기록. Host receipt에 platform의 RESULT_RECORDED/operation revision을 부여하지 않음.
- 독립 file device를 사용하고 device 자체 owner lock과 실제 호출 로그를 Host DB와 분리했다. 장비 모형은 호출을 dedup하지 않으므로 중복이 발생하면 시험에서 드러난다.
- SIGKILL을 SEND_ENTERED commit 후/native 호출 전과 native 호출 후/evidence commit 전 두 지점에 주입. 재기동/동일 요청 재전송 후 효과 수가 각각 0회/1회로 유지됨.
- gate가 native 호출을 기다릴 때 fence가 앞질러 확정되지 않으며, 별도 protection port는 호출 가능함을 시험.
- Host11개 시험 및 clippy -D warnings 통과. platform66개 시험 증거는 phase03이며 이번 변경으로 그 결과를 전체 플랫폼-Host 통합 완료로 확대하지 않는다.
- 실제 build verifier에 미등록 build.rs 추가·기존 SDK source 변경을 주입해 빌드 전 거부를 확인.
- 증거: references/implementation/phase04_checks.* 및 phase04_sdk_check.json.

### 다음 우선 작업

1. Host의 mTLS/gRPC 표면과 platform의 outbox delivery/receipt/evidence ingest를 연결.
2. native 결과 T2, resource handover, 취소 journal, 연속제어 expiry/deadman 및 복구 명세의 실제 처리.
3. 선언형 공정/BT·패키지·공통 UI·계정/단말과 제품 두 이미지·관리 도구·통합 인수까지 진행.

현재는 Host library와 process-crash fixture 검증이다. 실제 보호 성능, 물리 장비 지원, 전원 상실 내구성, 전체 Runtime–Host 네트워크 흐름은 아직 검증하지 않았다.

## 2026-09-10 · Host mTLS/gRPC 실제 왕복

- Host server에 필수 client certificate, CA chain, 명시적 leaf fingerprint 등록을 적용했다. 인증된 peer 이름과 PeerHello의 설치/release/clock/base manifest를 대조한다.
- Cell.Open에서 cell manifest와 CellDefinition을 별도로 협상해야 해당 cell/resource API를 사용한다.
- session handshake의 동시 재시도는 같은 사용 가능한 세션으로 수렴한다. 요청 future가 사라져도 Host bind와 session publish가 어긋나지 않도록 blocking 작업에 handshake 소유권을 넘긴다.
- Host-owned grant/renew/inspect/fence/arm/prepare/authorize/receipt/reconcile를 실제 generated gRPC 표면에 연결했다.
- 플랫폼 소유 업무 메서드는 Host에서 거부한다. legacy base Prepare/Authorize도 cell gate 우회 경로로 사용하지 못한다.
- RPC request key와 stable effect ID를 정규화된 업무 body에 영속 결합. wire permit 전체의 digest를 저장해 로컬 gate에 직접 쓰지 않는 필드가 바뀌어도 같은 ID를 재사용하지 못하게 한다.
- 네트워크 handler는 장비/저장 작업을 bounded blocking 실행으로 넘기고, event loop에서 Host gate를 기다리지 않는다.
- 실제 test CA/server/client certificate로 session→cell negotiation→grant→Arm→Prepare→Authorize→Evidence 회수 수행. 중복 Authorize 뒤에도 독립 device log는1회.
- 유효 CA에 속하지만 미등록인 client, client cert 없는 접속, manifest 불일치, cell 협상 누락, key 내용 변경, legacy 우회를 거부하는 시험 통과.
- Host 전체16개 시험 및 clippy -D warnings 통과. 그중 mTLS 네트워크 시험5개. 기존 platform66개·C++17개 증거는 각각 앞선 단계의 범위다.

### 다음 구현의 입력

- 현재 네트워크 client는 테스트의 platform-like client다. rx-application의 실제 outbox consumer/receipt 처리/T2와 연결해야 한다.
- Host Reconcile의 최초 retained prefix만으로 큰 journal 전체를 따라잡을 수 없다. background Evidence.Publish와 durable ack cursor, 재연결/복원 generation별 catch-up을 구현해야 한다.
- H→P publish session과 P→H request session의 신원을 혼동하지 않는다. Reconcile 응답의 context는 echo/correlation이며 producer 권한은 검증된 Host 채널에서 얻는다.
- native result의 의미/후조건, observation·material/support evidence, cancellation journal, streaming/deadman/복구, 패키지/BT/UI/두 제품 이미지/인수는 여전히 남아 있다.

## 2026-09-10 · application outbox→Host→T2 실제 연결

- SQLite schema2 migration과 DELIVERED outbox 상태 추가. 이전 EMIT_ENTERED를 보존하며 처리 완료된 메시지를 NEW로 되살리지 않는다.
- application이 pending delivery를 제공하고 emission 전에 현재 run/permit/condition을 재검사한다. 이미 emit에 진입한 항목에는 원격 receipt 재조정이 필요하다는 결과를 반환한다.
- Host PREPARED receipt의 불변 식별·journal/seq·invocation을 저장하고 Authorize outbox를 같은 transaction에서 만든다. Arm ack와 그 outbox 완료도 공동 commit 경로로 연결.
- T2에 native evidence·source slot·연속 cursor·work 결과·사건을 결합. 중복 prefix는 재적용하지 않고 GAP을 건너뛰지 않는다. 동일 seq/ID의 상충은 증거와 차단을 commit한 뒤 오류를 반환.
- Native/Predicate/Unobservable completion policy를 구별했다. Host capture가 곧 성공이 되지 않으며 성공 기록과 자원 해제를 분리한다. 후발 모순은 원 outcome을 보존하고 DISPUTED로 격리한다.
- journal ID 변경은 자동으로 순번0부터 허용하지 않는다. 변경 사건과 관련 차단을 기록하고 명시적 gap 재조정을 요구한다.
- rx-host-client 추가: mTLS/계약 협상, grant·fence·Arm·Prepare·Authorize·receipt·evidence를 application DTO와 연결. 정해진 Host receipt 단계/증거 schema를 대조한다.
- 별도 Host 프로세스를 실행하는 end-to-end 시험 통과: application의 실제 시작/part/activation/T1 outbox → mTLS Host → 독립 device log1회 → Host receipt → T2 SUCCEEDED. 초기 준비 관측은 명시된 시나리오 fixture이며 TLS 연결 성공으로 추론하지 않았다.
- platform 일반73개 시험 통과. 별도 network end-to-end1개는 tools/test_host_e2e.sh로 실제 실행하여 통과. Host16개/C++17개 기존 범위도 구분한다.
- schema1→2 migration 보존, T2 rollback/ack 유실, 증거 중복/누락/상충, journal 변경 검증 추가. workspace clippy -D warnings 통과.

### 남은 작업

- 실제 사용되는 background outbox pump/receipt 조정/Evidence.Publish 및 durable ack/catch-up. 현재 E2E는 명시적 단계 호출로 경로를 검증했다.
- resource release는 성공과 별도이며 아직 HELD다. 현재 상태·잔류 명령·소재 지지 근거를 받아 다음 작업으로 넘기는 경로를 구현해야 한다.
- 일반 workflow/BT·공정/장비 패키지, operator recovery/change/clearance, native cancellation/stream, 전체 UI/auth 사용자 흐름, 자사 의존 전체 빌드·두 제품 image·설치복원·인수.

## 2026-09-10 · 현재 인계 근거와 반복 소재 시도

- Host native adapter에 handover_snapshot port 추가. 미구현 adapter는 근거를 합성하지 않고 거부한다.
- 모의 file device의 현재 잔류 명령·제어 사용 가능·지지 상태를 작업/호출/device session에 결합한 세 관측으로 제공한다. 현재 물리 장비 구현이나 보호 성능 검증은 아니다.
- Host.WatchObservations의 명시된 handover source 집합으로 최신 snapshot을 받는다. 클라이언트는 schema·source 집합·correlation·quality·획득 오차를 대조한다.
- 플랫폼은 작업 완료와 자원 해제를 분리한다. 현재 cell revision/epoch, Host boot, device session, 원 invocation, 실제 완료 이후 관측, 세 조건·최대 age가 모두 맞을 때만 release를 commit한다.
- release에 사용한 관측·resource holder 변경·operation disposition·key·사건을 같은 transaction으로 기록한다. 실패 rollback과 같은 key 반복을 검증했다.
- PartAttempt 처분과 complete_part 검증 추가. 해당 part의 필수 단계가 SUCCEEDED/VALID이고 자원 인계까지 끝나야 CONFIRMED_COMPLETED가 된다.
- 허용 시도 예산을 다 사용하고 모든 part가 완료되면 run COMPLETED·mandate EXHAUSTED를 기록한다. 양품 품질 판정을 의미하지 않는다.
- 별도 Host process/mTLS E2E를 2개 소재 시도로 확장. 첫 작업 완료·인계 후 같은 자원을 두 번째 작업이 사용하고 최종 run 완료, 독립 device effect log2회를 확인.
- platform76개 일반 시험 통과 + 별도 network E2E1개 통과. Host16개 시험과 양쪽 clippy도 통과.

### 남은 경계

- 현재 E2E는 명시적 executor 단계 호출이다. 자동 운영 service/outbox pump/사용자 API와 UI가 아직 아니다.
- handover source는 snapshot 조회이며 일반 센서의 지속 stream·고속 control/deadman은 별도다.
- recovery/UNRESOLVED 후 인계·clearance, full workflow/BT·packages, 실제 지원/제품 image/유지보수·인수 목표를 계속 유지한다.

## 2026-09-10 · 실제 writer 기반 로컬 서비스와 운영 화면

- `rx-runtime::application`에 typed Command/Reply, Application Processor와 외부 서비스용 Handle/Port를 추가했다. 실제 application/SQLite는 전용 writer thread에서 소유한다. 조회·운영·세션 요청도 이 경계를 통과한다.
- `rx-application`에 현재 사용자 profile, user session 발급/종료, 권한별 일관 overview, idempotent 최초 셀 구성 등록을 추가했다. profile·셀·run·work를 같은 transaction에서 읽는다. 전역 control journal seq를 UI cursor로 노출하지 않는다.
- `rx-api`와 `rx-platform-local` 실행 파일을 만들었다. Argon2id 검증은 별도 제한된 worker에서 수행한다. 실제 socket/Host/Origin, JSON 중복/unknown field, cookie session, DB의 현재 역할/셀 권한을 검사한다.
- 이 실행 파일은 명시적 loopback 개발 설치만 받는다. 별도 Host 연결·자격 발급·장비 launcher가 없고, caller가 입력한 단말/역할 헤더를 신원으로 쓰지 않는다. 로그인은 실제 StartRun의 단말 검사를 우회하지 못한다.
- `rx-solutions/apps/operator`에 React/TypeScript 운영 앱을 만들었다. 로그인, 셀 상태, 새 실행 준비, 운전 보류, 실행/작업 기록, 현재 구성과 내 권한을 실제 API에서 조회한다. 장비 관측/결과/무결성/자원 처분을 구별한다.
- UI는 권한·자격을 자체 생성하지 않는다. 현재 연결/운전 가능으로 확인되지 않은 구성 항목을 연결 성공으로 표시하지 않는다. 셀 revision과 run revision은 각각 기록 버전으로 표시한다.
- 확인 창에서 검토한 cell revision과 요청 내용을 고정했다. 배경 조회가 갱신돼도 자동 교체하지 않는다. 상태가 바뀌면 application이 stale revision을 거부한다.
- mutation 전 key/내용/principal/installation/store generation을 sessionStorage에 보관한다. commit 뒤 응답을 잃어도 reload 후 같은 요청으로 회수한다. 미확정 요청을 새 key로 바꾸거나 조용히 지우지 않는다. 권한·복원 세대가 다르면 재전송을 막는다.
- 서버 조회 오류 또는 표시 상태가 오래되면 새 요청을 비활성화한다. 비밀번호와 session token은 브라우저 저장소에 보관하지 않는다. UI와 API 양쪽에 별도 구현한 운전 상태기계는 없다.
- platform 일반 시험81개(HTTP/실제 writer5개 포함) 통과, ignored network E2E1개는 이번 일반 시험의 통과 수에 포함하지 않았다. 기존 단계의 Host16개·C++17개·P–H network E2E 증거는 해당 범위를 유지한다.
- UI unit3개와 TypeScript/Vite build·format 검사 통과. 실제 server commit 후 응답 유실→reload→동일 key 회수에서 실행 기록이1개로 유지됨을 headless Chromium으로 확인했다. 검토 중 상태 변화·조회 연결 상실·logout·모바일 overflow도 확인했다. 실제 장비/모의 Host 프로세스는 이 UI 시험에 기동하지 않았다.

### 새 실행 입구와 증거

- [platform 서비스 경계와 실행 방법](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-api/README.md)
- [solutions UI 구조와 재현 방법](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/apps/operator/README.md)
- [브라우저 검사 결과](../../references/implementation/phase08-ui/browser-result.json)
- [운영 화면](../../references/implementation/phase08-ui/operator-overview.png)
- [응답 유실 후 확인 화면](../../references/implementation/phase08-ui/operator-pending.png)
- [모바일 화면](../../references/implementation/phase08-ui/operator-mobile.png)
- `phase08_checks.json`에 검증한 source hash·명령 결과·제한을 기록한다.

### 다음 구현의 범위

- 이번 서비스에 automatic outbox pump/Evidence.Publish/지속 관측/공정 실행기를 연결하는 일은 남았다. 현재 브라우저는 새 실행 기록을 준비하며 실장비를 시작하지 않는다.
- snapshot은 3초 polling이며 SSE·paged projection·대규모 indexed read가 아니다. 내부 scan 비용을 제품 규모에서 검증하지 않았다.
- 로컬 credential 파일과 DB 계정 권한을 하나의 관리/변경 흐름으로 완성하지 않았다. LAN/TLS/등록 단말, credential rotation·제품 secret 공급은 후속이다.
- UI는 기본 운영과 읽기 화면이다. 시각 공정 편집/BT·장비/공정 패키지, recovery/clearance/change/검증/배포/지원의 전체 사용자 흐름은 계속 구축한다.
- 두 제품 이미지, 자사5개 필수 stack와 전이 의존 빌드, Host lifecycle/continuous control/deadman, 설치·업데이트·복원·인수 목표는 그대로 유지한다.

## 2026-09-10 · 원본 보존과 Host 증거 전송

- 공유 `rx-protocol-adapter`를 추가해 Publish와 Reconcile가 같은 native evidence 변환을 사용하게 했다. 이전 변환에서 누락하던 native_id/native_data도 immutable 비교와 원본 조회에 포함한다. 과거 불완전 projection은 완전한 wire 원본으로 재구성하지 않는다.
- T2 결과에 producer through와 같은 transaction의 사건 위치를 결합했다. producer 소유권도 기록해 다른 Host가 동일 evidence ID를 재사용하거나 원본을 조회하지 못하게 한다.
- P의 `EvidenceIngress`에 실제 mTLS listener, Session.Open, Cell.Open, Evidence.Publish/Get을 연결했다. 등록 certificate·현재 principal·installation/store generation·release/clock·두 manifest·cell membership을 검사한다.
- producer session/Host boot/journal/인증 binding을 영속 연결했다. 동일 reconnect는 같은 session으로 수렴한다. 다른 incarnation/binding은 이전 session과 연관 운전 권한을 무효화한다. 브라우저 계정 수명과 구별하며 새 session으로 native 권한을 재생성하지 않는다.
- S의 `publication::Publisher`가 Host evidence journal을128개/1 MiB 및 협상된 더 작은 한도에 맞춰 전송한다. 각 destination의 ack 위치를 H에 저장하고, 응답 유실에는 같은 source seq/ID를 다시 전송한다. native 명령의 재전송 API는 이 모듈에 없다.
- ack의 설치/복원 세대/view/journal/range·일관된 순번을 검사한다. 과거 ack가 cursor를 되돌리지 않으며, 잘못된 세대·범위·후퇴·부분 batch ack는 수용하지 않는다. 원본 retention 삭제는 아직 하지 않는다.
- `Repository::journal_head`를 추가해 cursor/tail 읽기에 entity 전체 snapshot을 사용하지 않도록 했다. 갱신된 SDK47개 source bundle을 S에 재수출했으며 P application은 여전히 제외했다.
- platform 일반85개, Host17개 시험 통과. 양쪽 clippy -D warnings 통과. 별도 모의 장비 P–H E2E와 별도 publisher E2E를 각각 실행하여 통과했다. 일반85개의 ignored2개를 통과 수에 포함하지 않았다.
- publisher E2E는131개의 합성 orphan evidence를 사용했다. 첫 data batch를 P가 commit한 뒤 ack를 잃게 했고, 저장 slot은131개로 유지됐다. H restart 후 같은 journal/cursor, 이전 producer session 거부, 미등록 certificate 거부, 마지막 native metadata 조회를 확인했다. 이 시험에서는 실제/모의 native 호출을 하지 않았으며 qualification도 부여하지 않았다.
- 기존 P–H 작업 E2E는 별도로 두 모의 소재 시도의 T1→Host→T2→handover를 확인했다. publisher의 합성 기록 시험을 native 효과 검증으로 합쳐 표현하지 않는다.

### 관련 문서와 재현

- [P 증거 수신 경계](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-api/src/grpc/README.md)
- [무손실 protocol 변환](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-protocol-adapter/README.md)
- [H 전송과 영속 ack](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/runtime/rx-host/PUBLICATION.md)
- `rx-platform/tools/test_evidence_e2e.sh`, `rx-platform/tools/test_host_e2e.sh`
- `references/implementation/phase09_checks.json` 및 각 실행 log

### 다음 필수 경계

1. **공개 제어 원장 cursor**: 현재 DurableAck.platform_cursor.seq는 공유 내부 사건 로그 위치다. 내부 감사 사건과 공개 EventType/EntityView의 분리·정확한 매핑이 미완료다. `Journal.Subscribe/GetSnapshot`은 열지 않았으며, cursor binding을 정리하기 전 해당 계약을 VERIFIED로 올리지 않는다. producer through의 전달 검증과 공개 원장 적합성은 별개다.
2. **P→H 자동 outbox 전달**: 아직 명시적 단계 호출을 사용하는 작업 E2E다. 송신 재개 시 current authority/Host receipt 확인, PREPARED와 SEND_ENTERED의 다른 처리, 알려진 receipt 중복의 outbox 완료, 증거/receipt 도착 순서와 재조정까지 연결해야 한다.
3. **구성·배포 합성**: EvidenceIngress/Publisher는 library와 시험 프로세스에서 동작한다. 제품 두 이미지의 상주 프로세스/호스트 관리 도구와 자동 운전 서비스 구성은 후속이다.
4. 전체 source/profile/cancel/observation/attestation evidence, P 업무 RPC·공정/BT·packages·복구/clearance, 자사 필수 stack 빌드·업데이트·복원·인수를 계속 구현한다.

## 2026-09-10 · 감사/제어 순번 분리와 atomic control capture

- SQLite schema3에 control_events/control_entities를 추가했다. 기존 내부 audit/events, Host evidence journal, request/outbox 자료는 보존한다. 제어 사건과 현재 projection은 독립적인 연속 seq를 사용한다.
- Journaled<R>가 application transaction의 실제 core entity put을 추적하고 원래 transaction 안에서 최종 변화와 projection을 기록한다. handler별 event 호출에만 의존하지 않는다. 같은 transaction의 중간 값을 공개된 상태처럼 기록하지 않는다.
- 첫 제어 원장 초기화에서 기존 상태는 SNAPSHOT_SEED로 표현하며, 과거 사건을 새 실행 접수로 위장하지 않는다. 초기화 marker를 영속 보관한다.
- T2 ack는 control capture가 끝난 동일 transaction의 head를 받는다. 로그인/감사 append가 이 seq를 바꾸지 않으며 동일 evidence batch 재수신으로 제어 사건이 늘어나지 않는다.
- 셀 확장의 올바른 view 이름 site-cell-control-v1로 수정했다. H의 ack 검사와 영속 cursor key에도 view 이름을 반영하여 예전 audit/base 위치를 재사용하지 않는다. 빈 원장의 seq0도 표현할 수 있다.
- 저장/원장 원자성 fault injection, 직접 tx.put을 사용하는 Hold capture, source event의 연속 순번/exclusive after와 현재 projection 일치를 검증했다.
- platform 일반88개·Host17개와 양쪽 clippy 통과. 별도 publisher131개/ack 유실/restart 시험과 두 모의 소재 시도 P–H 작업 시험도 각각 통과했다. ignored2개는 일반 시험 통과 수에서 제외한다.
- SDK48개 파일을 재수출했고 P application은 S에 넣지 않았다. frozen 규범8개 파일은 변경하지 않았다.

### 완료한 것과 남은 것

내부 감사 순번을 control cursor에 넣던 문제는 별도 저장 구조와 같은 transaction cut으로 수정했다. **저장된 control payload는 현재 typed application 상태 snapshot이다.** 공개 CellJournalRecord/EntityView의 전체 변환·snapshot/paging·구독은 아직 미완료다.

특히 CellContext mode/commissioning·Block 생성 revision, Qualification limitations/상태, 검증된 checkpoint artifact, Mandate/Permit의 당시 관련 상태, 후속 case/material/change 모델을 정확히 보존·변환해야 한다. 현재 DB 값을 과거 사건에 붙이거나 빈 필드를 임의 값으로 채우지 않는다. 공개 Journal RPC를 아직 열지 않았고 R17은 PARTIAL이다.

다음 구현은 [제어 원장 상세](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/CONTROL_JOURNAL.md)의 모델·wire mapping과 P→H 자동 outbox 전달 경계다. 공정/장비 패키지·BT·복구·제품 이미지·자사 지원·설치복원·인수의 전체 목표는 유지한다.

## 2026-09-10 · P→H 자동 전달과 수신 기록 경합

- Host마다 bounded Dispatcher를 구성하고 실제 writer의 typed Command를 통해 Arm/Prepare/Authorize/Fence 전달과 GetReceipt/Reconcile/T2 조정을 수행한다. SDK 직접 호출과 workflow 결과 판정을 sender에 넣지 않았다.
- plan_delivery는 Host 권한·메시지 관계와 최초 emission의 현재 run/permit/condition을 같은 transaction에서 확인한다. 이미 EMIT_ENTERED이면 operation 요청을 다시 보내지 않고 receipt를 조회한다.
- pending outbox의 exclusive key paging과 cursor 순환, 제한된 pass/backoff를 구현했다. 앞쪽 미결 항목 때문에 뒤쪽 메시지가 영구적으로 숨지 않는다. scheduling memory와 별개로 미결 상태는 영속 저장된다.
- PREPARED 응답으로 Authorize outbox를 완료 처리하던 경계를 수정했다. 동일 receipt를 이미 저장했어도 올바른 관련 outbox는 완료한다. 잘못된 message를 cached receipt 때문에 수락하지 않는다.
- timeout/NOT_FOUND 등에는 UNKNOWN/격리와 영속 attention을 남긴다. PREPARED 상태의 이전 authorization은 새 grant/permit 재결합이 필요하다고 표시하며 자동 native 재전송하지 않는다.
- 늦은 receipt가 invocation 상관관계를 확정하면 보관한 native evidence를 같은 transaction에서 재평가한다. native entry가 입증되면 permit를 소비하고 아직 NEW인 authorization을 폐기한다.
- Fence ack의 Host boot/journal/target/message 관계를 확인하고 수신 근거와 outbox 완료를 함께 기록한다.
- Runtime은 새 전달·작업·인계 command를 같은 application에 연결한다. SubmitWork payload는 큐 메시지 크기를 줄이도록 box 처리했다.
- platform 일반92개·Host17개 및 양쪽 clippy 통과. 별도 프로세스 통합 시험은 명시적 작업 경로, 자동 dispatcher 경로, evidence publisher 경로의3개를 실제 실행했다. 일반 시험의 ignored3개를 pass 수에 포함하지 않았다.
- 자동 dispatcher 시험은 첫 Host Authorize가 실제 모의 호출을 마친 뒤 응답을 잃게 한다. 두 part에서 Authorize2회·독립 device effect2회로 유지됐고, GetReceipt/Reconcile로 결과를 회수했다. 완료 후 Hold의 Fence가 Host에 자동 적용되는 것도 확인했다.

### 범위와 다음 연결

[자동 전달 구조](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-host-client/DELIVERY.md)에 수신 기록별 행동과 한도를 기록했다. part/activation 생성, 인계 proof 취득·release, part 완료는 시험 executor가 명시적으로 수행한다. 이를 완전한 자율 생산 서비스로 표현하지 않는다.

새 grant/rebind·Host 재등록·attention→case/절차 UI, 큰 저장소의 reconciliation index, 제품 process supervisor 통합은 남았다. Reconcile의 초기128개 prefix를 넘어서는 전달은 별도 Publisher를 함께 배치해야 한다. 공개 제어 원장 wire mapping과 checkpoint 모델, 공정/장비 패키지·BT/편집기, 실제 자사 지원·두 이미지·설치복원·인수의 전체 목표도 계속 유지한다.

## 2026-09-11 · 패키지 신뢰/내용 경계와 자사 기본 catalogue

- P의 ROS 비의존 rx-package에 Device/Process/UI 공통 manifest, 파일 inventory, target/계약/ABI, 잠긴 의존성과 외부 asset 참조를 구현했다. S SDK에 같은 verifier를 수출한다.
- Ed25519 strict signature는 domain/key ID/정규화 manifest에 결합한다. 내용 digest와 signer rotation을 구별하며, 다른 key alias의 권한을 같은 서명으로 이용하지 못하게 한다.
- 종류별 permission 요청과 signer 허용 범위를 검사한다. UI/Process가 native endpoint 권한을 요구하거나 Process/UI가 native executable을 포함하면 거부한다. 검증 통과가 OS 접근권·장비 실행권·qualification 부여를 뜻하지 않는다.
- 전이 dependency에서 정확한 version/kind/digest, target/contract, 현재 trust를 재검사한다. root 구버전 재유입·동일 이름의 다른 버전·cycle·회수된 key의 기존 검증 결과를 거부한다.
- 폴더는 capability 안에서 regular file만 읽고 경로 탈출·symlink·case/hierarchy alias·reserved 이름을 차단한다. 수/깊이/bytes를 제한하며 검증 후에는 원본 경로가 아닌 immutable bytes를 보유한다.
- ROS 비의존 target과 특정 ROS 배포판 요구를 구별한다. 큰 policy/model asset은 독립 검증된 ArtifactRef catalogue로 연결할 수 있으며 대형 asset store/streaming 자체는 후속이다.
- S에 rx-solution-catalog와 robotis-support.v1.json을 추가했다. 다섯 필수 source와22개 모델/역할 구성을 유지한다. FFW BG2 revision3개와 leader/follower를 분리했다. Host가 이 catalogue를 필수 의존하며 시작 때 기본 구성을 확인한다.
- 모든 catalogue 행은 SOURCE_OBSERVED다. GPIO의 중첩 interface 구조를 보존하고 선언된 update rate/관절 배열을 실측/actuator 개수/완료 보장으로 바꾸지 않는다.
- Git commit blob으로 출처22개 파일을 대조했다. 다섯 레포 pin은 기존 확정 값과 같았다. 실제 ROS 패키지 로딩이나 controller 활성화는 하지 않았다.
- SDK exporter는 신선한 staging inventory를 만들고 교체한다. 기존 SDK의 수정·추가 파일은 덮어쓰기 전에 거부하고, 과거 inventory의 불필요한 생성 파일은 새 수출에 전파하지 않는다. P authority engine은 제외하며 SDK53개 파일을 수출했다.
- platform 일반100개, solutions19개(Host17+catalogue2), 양쪽 clippy 통과. 기존 명시적/자동 작업 및 publisher 별도 프로세스 E2E3개도 통과했다. 패키지8개 시험과 SDK 수출 regression, source identity 검사 범위를 각각 구별한다.

### 산출물과 다음 경계

- [패키지 신뢰·파일 경계](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-package/README.md)
- [자사 기본 catalogue](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/catalogs/README.md)
- tools/test_export_host_sdk.py, tools/check_robotis_catalog_sources.py 및 phase12 검증 기록

현재 VerifiedPackage는 내용·서명·호환 검사 결과다. 실제 descriptor semantic validation, DeviceFamily/Profile/ProcessSource·현장 resolved binding, package stage/install/activate, trust key 운영·OS sandbox, image 전체 전이 의존 빌드와 qualification은 아직 미완료다. 원래의 공개 원장 wire/checkpoint, 공정/BT/편집기, 복구/배포/복원/인수 목표를 그대로 유지한다.

## 2026-09-11 · 공정 원본·확장·후보 계획

- S의 rx-process에 Sequence/ParallelAll/Branch/Repeat/Call/Operation/Wait/Intervention 원본 schema와 결정적 compiler를 추가했다. 기존 source ID와 인스턴스 경로를 보존한다.
- 반복과 하위 flow를 유한하게 확장하고 고유 node identity를 만든다. duplicate/cycle/shared node/누락/도달 불가/깊이·확장 상한을 검사한다. 병렬의 실제 normalized resource set이 겹치면 거부한다.
- resolved source와 binding digest를 ProgressView에 결합했다. 다음 후보는 완전한 P view·기록된 branch/wait/개입 결정과 operation 결과·자원 인계를 기준으로 계산한다.
- UNKNOWN/DISPUTED/UNRESOLVED를 FAILURE로 낮추지 않는다. 미선택 branch 이력·부분 view·앞 단계가 없는 뒤 단계 이력은 거부한다. 계획 완료를 part/품질/운전 허가로 기록하지 않는다.
- VerifiedPackage Process entry에서만 source를 가져오는 semantic compiler 경로와 선언된 OperationSubmit permission 검사를 추가했다. 서명된 잘못된 문법도 거부한다.
- BT.CPP format4의 RX 전용 노드 XML, resolved JSON과 compile report를 생성하는 CLI를 추가했다. 임의 script/include/retry decorator는 출력하지 않는다.
- 소재 공급5단계 예제 파일을 컴파일하고 XML 구문을 확인했다. 산출물은 COMPILED_NOT_QUALIFIED다. placeholder program/parameter와 simulation 대상이며 실제 장비/현장 입력을 검증하지 않았다.
- process 관련9개 시험이 통과했고 solutions 전체28개 및 clippy가 통과했다. P 코드는 변경하지 않았으며 앞 단계의100개/P–H 통합 증거는 그 범위를 유지한다.

### 산출물과 필수 후속

[공정 모델/계획 경계](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/runtime/rx-process/README.md), [예제 원본](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/examples/process/README.md), [컴파일 보고서](../../references/implementation/phase13-compiled-example-v2/compile-report.json).

현재는 compiler와 pure frontier planner다. RX C++ BT 노드·factory/P client·halt/restart 복원, P의 branch/visit/checkpoint eligibility, 전체 public journal mapping, visual editor를 아직 연결하지 않았다. P의 기존 finite StepBinding에 분기/반복을 임의 flatten하여 운전하지 않는다. package/profile/site resolver·복구·실제 자사 image build·배포복원/인수 목표도 그대로 유지한다.

## 2026-09-11 · 실제 C++ BT 노드와 제한된 요청 큐

- BehaviorTree.CPP4.8.3 exact commit을 별도 dependency lock에 고정하고 실제 Linux C++17 build를 만들었다. Vendor는 원본 cache이며 source 변경을 검증 도구가 거부한다.
- RXSequence/RXParallelAll/RXBranch/RXOperation/RXWait/RXIntervention을 실제 factory에 등록했다. tick은 immutable Frame을 읽고 제한된 큐에 요청을 넣으며 ROS/native SDK나 P 결과 저장을 직접 호출하지 않는다.
- Context를 run/session/resolved digest/visit/epoch에 묶었다. complete/current/monotonic expiry/현재 submission 권한/eligible node를 확인하며, 큐에서 꺼낼 때도 회수·만료를 다시 검사한다.
- 동일 operation ID/branch decision/terminal outcome의 변경과 complete view의 binding 유실을 거부한다. 잘못된 Frame은 이전 정상 Frame을 계속 쓰지 않도록 정지하고 pause 요청을 남긴다.
- 반복 tick과 트리 재구성이 같은 요청을 재생성하지 않도록 Context 수준으로 dedup한다. 정상 요청32개와 별도 pause1개를 둔다. Halt는 pause 요청이며 native cancel/정지/자원 해제 완료가 아니다.
- UNKNOWN/UNRESOLVED/상충은 RUNNING으로 대기한다. 성공 후 release를 기다리고, parallel의 불명·실패·개입 대기에서는 새 admission을 억제한다. 진행 중 sibling을 임의로 완료/취소 처리하지 않는다.
- Factory 이전 XML 허용 목록을 구현했다. registry와 node kind/ID/속성/자식 순서·전체 목록을 대조하며 script/pre/post/include/임의 builtin/추가 attribute를 거부한다.
- 네 C++ 시나리오와 Rust compiler가 생성한5단계 예제를 실제 BT 엔진에서 실행해 통과했다. 시험은 network none/read-only/cap-drop all/no-new-privileges, 읽기 전용 fixture mount로 수행했다. C++ build는 -Wall/-Wextra/-Werror다.

### 검증의 범위와 다음 작업

[native executor](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/native/executor/README.md), tools/test_bt_executor.py, [시험 결과](../../references/implementation/phase14-bt/result.json).

P Frame·완료·decision·clearance는 합성 fixture다. 실제 P 통신 client, 정확한 protocol-to-Frame/eligibility mapping, 영속 request key/checkpoint와 restart 조정은 아직 연결하지 않았다. executor-validation은 제품 두 이미지가 아닌 검증 target이다. 이 시험을 장비 동작·실제 로봇·qualification 인수로 표현하지 않는다.

P의 공개 원장/완전한 checkpoint와 분기·visit 검증, package/profile/site resolver·시각 편집·전체 복구, 자사 stack의 두 제품 image·설치/업데이트/복원·인수를 계속 구축한다.

## 2026-09-11 · P 공정 결정/eligibility와 공통 의미 모델

- 공정 schema/frontier를 ROS·BT·I/O 비의존 rx-process-contract로 옮겼다. S는 SDK를 사용하며 source compiler/XML/C++ runtime 구현은 계속 S 소유다. P authority engine은 S에 넣지 않았다.
- CellConfiguration의 graph mode에서 resolved 구조·ID·resource와 recipe digest/schema/size, StepBinding Host/Intent를 검증한다. Graph와 별도 predecessor 해석을 섞지 않는다.
- P가 branch 선택을 현재 fact로 평가하고 decision/근거/시각/checkpoint/run revision/key를 함께 저장한다. UNKNOWN은 선택하지 않는다. 기존 선택은 재요청이나 이후 조건 변화로 바꾸지 않는다.
- P가 wait window와 deadline을 소유하고, 현재 조건/마감으로 결과를 기록한다. 재요청이 마감을 연장하지 않으며 caller의 PASS/시각을 받지 않는다.
- ResolveActivation과 새 Submit 모두 P의 실제 frontier eligibility를 검사한다. 선택하지 않은 branch와 미완료 wait/predecessor를 우회하지 못한다.
- Part 완료는 선택된 graph와 작업 결과/인계를 확인한다. P restart 후 decision/checkpoint는 유지되고 run authority는 철회된다.
- Runtime typed Command와 P progress 읽기에 연결했다. 외부 Workflow.CommitCheckpoint wire·artifact·C++ P client 연결은 아직 미완료다.
- P의5개 추가 시나리오가 통과했다. 전체 platform105개/solutions28개·양쪽 clippy, 별도 작업/dispatcher/publisher E2E3개와 실제 BT engine 시나리오/생성예제 검증이 통과했다. Frozen 규범 파일은 변경하지 않았다.

[공통 모델](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-process-contract/README.md), [P checkpoint](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/PROCESS_CHECKPOINT.md).

남은 핵심은 실제 executor wire adapter·checkpoint artifact/public journal 전체 표현, intervention/recovery/restart, index/성능, 시각 편집·현장 package resolver, 두 제품 image의 자사 stack·설치업데이트복원·인수다. Graph의 내부 결정 검증을 전체 외부 계약/물리 운전 검증으로 승격하지 않는다.

## 2026-09-11 · 내용 주소 checkpoint와 일관된 RunView 읽기

- 실제 Run 변경 transaction에서 activation/slot/intent 연결과 visit별 공정 결정을 수집하여 `rx.executor-state.v1` artifact를 만든다. canonical bytes의 실제 SHA-256/size를 저장한다.
- 원래 Run revision과 현재 RunSnapshot, immutable artifact·run 소유 참조, control event/projection을 같은 commit에 묶었다. schema 초기화 marker도 같은 transaction에 기록한다.
- slot의 Work가 실제 run/activation/part/cell/slot/operation에 속하는지 대조한다. 복원 조회에서 현재 Run과 snapshot, payload의 revision/내용·연결을 다시 확인한다.
- 이전 artifact는 새 revision 및 P restart 후에도 보존한다. restart 뒤 새 snapshot의 현재 상태는 권한 철회를 반영하며, 과거 EXECUTING이 현재 권한이 되지 않는다.
- Runtime typed command 및 로컬 BFF 두 GET route에 연결했다. RunView는 frozen codec의 Counter/enum/optional 규칙을 사용한다. Artifact 조회는 현재 세션·셀 접근권과 run별 소유 참조를 요구한다.
- T1 rollback/commit 후 응답 유실·동일 key 회수·원장 projection 일치, 이전 artifact 보존·잘못된 ref/접근권 거부를 검증했다. 기존 restart 시나리오에 branch 결정과 과거/현재 artifact 대조를 추가했다.
- 실제 HTTP/SQLite 조회와 strict query 입력, 여섯 RunState·2^53 초과 Counter를 검증했다. 최신 view에 정상적인 과거 artifact를 끼워 넣거나 저장 payload를 변경하면 무결성 오류가 난다.
- 전체 P109개 일반 시험 후 추가 무결성 시험을 포함한 영향 패키지를 재검증했다. 누적 P110개, 실패0. 현재 소스로 clippy와 별도 작업/자동 dispatcher/publisher E2E3개가 통과했다. S의 일반28개와 실제 BT 시험은 phase15의 범위이며 이번에 반복 실행했다고 표시하지 않는다. frozen 규범8개는 변경하지 않았다.

[저장/조회 명세](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/CHECKPOINT_ARTIFACT.md), [검증 기록](../../references/implementation/phase16_checks.json).

현재 artifact는 내부 run history를 한 문서로 담으며 entity scan과1 MiB 제한을 사용한다. 장기 생산의 용량 예약·분할·index·retention 및 한계 근처의 제어/evidence 수용 보장은 아직 완료하지 않았다. 실제 executor mTLS/Workflow.GetRun/CommitCheckpoint·artifact 확보·C++ Frame/worker 복원, 전체 public journal, intervention/recovery, 현장 package·시각 편집·자사 제품 image/배포/인수 목표를 유지한다. 원격 실행기 복원 또는 실제 장비 qualification 완료로 승격하지 않는다.

## 2026-09-11 · 실행기 peer 협상과 실제 원격 Run 조회

- PlatformIngress에 등록된 Executor의 Session.Open/Cell.Open/Workflow.GetRun을 연결했다. 기존 EvidenceIngress 이름은 호환 alias이며 Host evidence의 인증 binding은 유지했다.
- P의 ExecutorPeer는 principal/session/boot/인증 binding/협상한 cell definition을 영속 기록한다. Host와 Executor principal을 분리하고 body role을 권한으로 받아들이지 않는다.
- 동일 Open/응답 유실 뒤 session ID와 epoch는 유지한다. peer boot/binding 교체는 기존·legacy session을 철회하고 해당 실행기의 셀 및 공유 자원 영향 범위를 같은 transaction에서 무효화한다.
- 폐기된 E boot를 영속 기록하여 늦은 이전 프로세스의 Open이 새 session을 밀어내지 못하게 했다. P 재시작 뒤에도 이전 session/폐기 boot는 거부하고 현재 E boot는 새 P session/셀 협상을 요구한다.
- GetRun은 같은 인증서의 현재 base session, cell 협상, 계정 셀 범위, 실제 executor 배정과 현재 checkpoint 무결성을 확인한다. 이 조회가 run의 executor 권한을 호출자의 새 session으로 교체하지 않는다.
- 실제 TLS socket/SQLite 시험으로 두 manifest 협상 전 조회 거부, 미등록 인증서·역할 사칭·동일 principal의 다른 인증서 session 재사용·다른 executor 배정 셀 접근 거부를 검증했다.
- 현재 P 일반112개·clippy가 통과했다. 별도 명시적 작업/자동 dispatcher/Host publisher E2E3개도 새 ingress로 통과했다. frozen 규범8개와 phase15에서 검증한 S source는 유지한다. S 일반28개/실제 BT 증거는 이번 반복 실행으로 표시하지 않는다.

[실행기 세션 명세](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/EXECUTOR_PEER.md), [검증 기록](../../references/implementation/phase17_checks.json).

Workflow mutation/CommitCheckpoint, E의 artifact 확보·C++ Frame/request worker와 영속 pending key 복원은 아직 미완료다. 서비스 등록은 connection liveness/readiness가 아니며 heartbeat/disconnect monitor·새 시작 판단과 함께 구현해야 한다. 현재 등록/조회 경로만으로 실장비 운전이나 자동 복구 완료를 주장하지 않는다. 장기 run 용량·index/원장전체/복구·현장 package·편집기·자사 두 제품 이미지·배포복원/인수 목표도 계속 남아 있다.

## 2026-09-11 · 실행기 소재 시도·단계 요청과 최초 접수 근거

- Cell.BeginPartAttempt와 Workflow.ResolveActivation을 실제 mTLS→typed command→writer/SQLite에 연결했다. 계정/session/협상 definition과 executor 배정을 현재 transaction에서 확인한다.
- 공개 요청의 전체 payload(명시한 mandate·visit·객체 CAS 포함)를 key에 결합했다. 동일 요청 회수와 새 의도를 구별하고, 바뀐 payload의 같은 key는 ALREADY_EXISTS/KEY_CONFLICT로 반환한다.
- 기존 trusted composition 경로와 공개 요청 경로가 part 예산 소비·activation 할당의 같은 transition 함수를 사용하도록 정리했다. handler에 별도 상태기계나 SQL을 만들지 않았다.
- PartAttempt 응답의 실제 record revision, activation/slot/intent snapshot과 요청 결과를 core 변경 및 Run checkpoint와 같은 commit에 보존한다. 실제 소재 identity가 없는 material_id는 absent다.
- 저장 직전 실패/commit 후 응답 유실에서 part/예산/activation 유일성과 checkpoint cut을 검증했다. 새 key의 기존 activation 회수, 바뀐 mandate/visit 거부, 역할 회수 후 cached 결과 접근 거부를 포함한다.
- 실제 TLS 시험에서 simulation operator/qualification/Host Arm fixture로 시작한 후 원격 E가 part와 activation을 하나씩 만들고 GetRun에서 확인했다. 이 시험은 Work/native device를 생성·호출하지 않는다.
- 다음 Submit wire 연결에 필요한 ADMITTED Receipt 근거도 추가했다. 신규 Work의 실제 control record INSERT seq와 journal identity를 같은 T1에 저장한다. P boot와 store generation을 구별하고, 이후 Hold에도 원래 접수 확인서를 유지한다.
- 과거 Work에 원래 접수 위치가 없으면 현재 head로 꾸미지 않는다. 새 native 호출의 이유로 쓰지 않고 CONTINUITY_UNPROVEN으로 남긴다.
- P 일반115개·clippy, 별도 작업/자동 dispatcher/Host publisher E2E3개가 통과했다. 확정 규범8개를 유지했다. S 일반28개·실제 BT는 이전 범위의 증거이며 이번에 반복 실행했다고 표시하지 않는다.

[실행기 요청](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/EXECUTOR_REQUESTS.md), [접수 확인서](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/ADMISSION_RECEIPT.md), [검증 기록](../../references/implementation/phase18_checks.json).

다음 필수 연결은 Cell.SubmitOperation의 중첩 context/parent/part/두 CAS와 같은 T1·정확한 Receipt 반환, Operation 조회, branch/wait/CommitCheckpoint, E artifact/C++ Frame·영속 pending key 복원이다. 서비스 liveness, 전체 원장/장기 용량·index, 복구·현장 package·편집기·자사 두 제품 이미지·설치복원/인수도 계속 남아 있다.

## 2026-09-11 · 원격 실행기 유한 제출→자동 Host 전달→결과 조회

- Cell.SubmitOperation의 run mandate 경로를 연결했다. 중첩 CallContext의 session/call/key 일치와 revision 위치, cell/run/activation/part 관계, parent mandate, 두 객체 CAS와 normalized intent를 검증한다.
- 현재 peer/셀 권한 검사 뒤 전체 typed payload/key를 비교한다. cached 결과와 새 slot을 구별하며 기존 slot은 Work/Operation/Permit의 상호 연결과 digest/parent까지 확인한다.
- 유한 작업의 실제 T1 전이는 trusted composition 경로와 공유한다. 새로운 wire 경로에 별도 상태기계/allocator/native 호출을 만들지 않았다.
- 원래 접수 확인서를 반환하며, T1 뒤 receipt 읽기/전송 실패가 commit 취소가 되지 않는다. 같은 key/body로 원래 ADMITTED stage/revision/journal 위치를 회수한다. base Submit은 cell 검사 우회 경로로 활성화하지 않는다.
- Operation.Get을 현재 executor 범위에 연결하고 phase/knowledge/outcome/integrity/disposition/evidence를 독립적으로 표현했다. Work와 Operation의 intent digest 차이는 DATA_LOSS다. UNKNOWN·후발 모순·인계 전 격리 상태를 검증했다.
- core 시험은 잘못된 parent/part/CAS, T1 rollback/응답 유실, 전체 payload 충돌, 다른 key의 기존 slot, Hold 뒤 원래 receipt 회수와 역할 회수를 확인한다. API 시험은 실제 TLS에서 중첩 context/다른 run/part/parent·stale CAS 및 새 call trace ID의 동일 요청 회수를 확인한다.
- 기존 별도 Host 통합에 원격 E client 시나리오를 추가했다. E→P Submit 응답은 T1 뒤, P→H Authorize 응답은 실제 모의 제출 뒤 각각1회 유실한다. 두 part에 Authorize 호출2회·Host effects2회만 남으며, 원래 receipt 회수·P 결과 조회·인계·part/run 완료를 확인한다.
- 더 엄격하게 추가한 시험에서 ‘성공이면 HELD’라는 oracle 가정이 잘못임을 확인했다. 응답 유실로 격리된 자원은 성공 근거 후에도 인계 전까지 QUARANTINED일 수 있다. 계약대로 HELD/QUARANTINED를 허용하고, 인계 전 RELEASED를 거부하도록 시험을 바로잡았다. 최초 실패 로그도 보존한다.
- Domain의 read-only intent digest getter를 S SDK에 수출했고58개 inventory를 유지했다. P 일반117개, S 기본27개+test-harness crash1개, 양쪽 clippy와 별도 E2E4개가 통과했다. frozen 규범8개는 변경하지 않았다. 기존 C++ BT 검증을 이번에 다시 실행했다고 표시하지 않는다.

[유한 작업 제출 명세](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/EXECUTOR_SUBMISSION.md), [검증 기록](../../references/implementation/phase19_checks.json).

실제 C++ BT worker/Frame·영속 pending key·artifact 확보·branch/wait/CommitCheckpoint, cancel/recovery/control-session, 서비스 liveness, 원장 전체·장기 용량/index, UI와 자사 두 제품 이미지·설치복원/인수는 미완료다. 새 원격 client는 test-only이며 operator 시작/초기 모의 근거·인계/part 완료는 명시적 composition 경로다. 물리 로봇·PLC 운전 또는 현장 qualification 완료를 의미하지 않는다.

## 2026-09-11 · P 현재 상태→S 복원 client→실제 C++ Frame

- Run/Purpose/상태/ProcessCheckpoint/WaitWindow와 checkpoint/activation/slot DTO를 shared rx-process-contract로 옮겼다. 원래 checkpoint v1의 필드/정규화 표현을 유지하며 P Engine은 S SDK에 넣지 않았다.
- 현재 execution snapshot을 실제 P read transaction/control cut에 연결했다. 현재 cell revision/epoch/scopes, run/checkpoint, work/branch/wait, P 시각/만료와 요청 허용 여부/이유를 함께 읽는다. 단순 조회 실패를 허용 false로 숨기지 않는다.
- maintained condition이 새 보고 없이 age 한계를 넘는 경우를 확인하고, active_run에서 실제 처리 시점에 재평가하도록 고쳤다. 현재 read가 false인 것과 과거 Run=EXECUTING 기록은 구별한다.
- 선택적 rx.executor.v1 GetSnapshot/GetArtifact와 별도 source-pinned read binding을 추가했다. 기존 base/cell 필수 협상과 mutation은 유지하며, caller는 추가 binding hash도 맞아야 한다. GetArtifact는 run-owned checkpoint 또는 정확한 resolved process만 읽는다.
- S에 rx-executor client를 만들었다. P session/셀 협상, payload hash/size/schema, runtime/순서/시계·공정/작업 연결을 검증한다. epoch/session/digest를 기존 Context에 자동 채택하지 않는다.
- trusted same-host Clock port와 Linux CLOCK_BOOTTIME/kernel boot ID adapter를 추가했다. source absolute expiry와 local request-send bound를 함께 적용한다. C++ Frame에도 source clock을 넣고 publish/tick/handoff에서 검사한다.
- C++ strict IPC decoder와 source-clock 시험을 추가했다. duplicate/extra JSON key, 숫자/overflow uint64, 중복 node, clock 부재/변경/만료를 거부한다. 아직 넘기지 않은 request는 만료 중 queue에 유지하고 새 유효 frame에서 한 번 전달한다.
- 별도 S test-harness reader를 새 boot로 실행해 실제 mTLS로 checkpoint/live snapshot/resolved를 회수했다. 기존 작업 ID는 보존되며 Run은 RECOVERY_REQUIRED이고 새 admission은 false다. 이 데이터로 만든 Frame을 실제 Linux BT.CPP에서 읽어 작업 재발행/미실행 작업의 성공 처리가 없음을 확인했다.
- P 일반118개·S32개, 별도 E2E5개와 기존/추가 C++ BT 시나리오가 통과했다. macOS에서 Linux cross-check는 C cross compiler 부재로 끝났고, Linux용 고정 Rust1.98.1 toolchain을 기존 검증 이미지에서 native/offline으로 실행해 client5개 시험(실제 boottime 포함)을 통과했다. 교차 검사 실패와 native 대체 근거를 구별해 보존한다.
- 선택적 Docker Rust 이미지 metadata 조회는 응답 없이 장시간 유지되어 해당 작업만 중지했다. 새 이미지를 추정해 사용하지 않았고, 기존 검증 image와 공식 고정 Linux toolchain을 사용했다. 확정 규범8개는 유지한다.

[현재 실행 상태와 Frame 명세](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/EXECUTION_READ.md), [S client](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/runtime/rx-executor/README.md), [검증 기록](../../references/implementation/phase20_checks.json).

실제 운영 BT daemon/요청 worker·영속 pending key, branch/wait/Workflow.CommitCheckpoint·복구/취소/control-session, supervisor liveness, 장기 용량/index/전체 원장, UI·자사 두 제품 image·설치복원/인수는 남아 있다. 선택적 읽기 binding과 fixture client를 그 기능의 대체 완료로 취급하지 않는다. 시계/단말/qualification/장비 입력은 simulation fixture이며 실물 운전 검증이 아니다.

## 2026-09-11 · S 요청 journal과 실제 C++ 유한 작업 worker

- S 전용 journal을 installation/store generation/principal/release/cell definition/run/recipe에 고정했다. logical visit/node/stage의 current pointer와 불변 attempt generation을 분리하고 이전 key/body를 보존한다.
- prepare·enter를 실제 SQLite에 commit한 뒤에만 network client를 호출한다. 응답 유실/프로세스 종료의 EMIT_ENTERED를 Prepared로 되돌리거나 임의 새 key로 바꾸지 않는다. P atomic Resolve/Submit의 ABORTED가 확인된 경우에만 같은 의미의 새 CAS/key를 허용한다. detail 문자열을 machine 판정으로 읽지 않는다.
- local RPC reply와 P projection 관측을 분리했다. 새 snapshot에서 기존 작업이 보여도 없던 응답을 만들지 않는다. mapping/intent identity 변화는 거부하고 unchanged observation을 매 tick 기록하지 않는다.
- 실제 C++ request의 context/node/kind/argument/timeout을 P의 validated process에 대조하는 worker를 만들었다. 유한 operation에 ResolveActivation→새 snapshot→SubmitOperation을 실행하고, 각 RPC의 전체 body와 key를 선행 기록한다.
- 이미 P에 있는 작업은 그 ID를 확인해 사용한다. 알려진 응답의 mapping이 완전한 P snapshot에서 사라지거나 context가 바뀌면 조정 대상으로 남긴다. 나머지 BT request 종류는 Unsupported이며 성공으로 위장하지 않는다.
- C++ validation-only request producer를 추가했다. test harness 옵션을 켠 빌드에서만 만들고, S fixture는 고정된 local image digest를 network none/read-only/cap-drop/pull never로 실행한다.
- 실제 C++ request→별도 S worker→P mTLS/SQLite 시험에서 정상 처리, Submit 진입 직후 종료, P Submit 응답 뒤 local 저장 전 종료, Resolve/Submit 응답의 commit 후 유실을 각각 확인했다. 다섯 시나리오 모두 같은 key와 작업 수를 보존했고 새 boot recovery에서 무허가 재발행이 없었다.
- local rollback/commit 응답 유실·재개방·key 변경 제한·observed/received 구분·store generation 거부 시험도 통과했다. 이 통합은 P admission까지이며 기존 별도 Host 시험이 P→H/native/인계를 검증한다. 전체 운영 daemon이나 연속 복구 완료로 확대하지 않는다.

[S journal/worker 명세](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/runtime/rx-executor/JOURNAL_AND_WORKER.md), [검증 기록](../../references/implementation/phase21_checks.json).

아직 part coordinator/상주 BT loop, branch/wait/개입·인계·pause 요청 worker, CommitCheckpoint/명시적 restart/clearance/control-session, liveness·전체 원장/장기 용량/index, UI·두 제품 image·자사 native stack·설치복원/인수는 미완료다. Goal과 요구 추적표 범위를 유지한다.

## 2026-09-11 · 실제 BT halt→영속 PauseRun→허가 철회

- Workflow.PauseRun을 현재 executor session/definition/run CAS와 전체 요청 key에 연결했다. origin Run은 PAUSED이며, 이미 제한/완료된 상태를 더 약한 상태로 바꾸지 않는다.
- current Host authority가 cell epoch/scope에 묶이므로 실행/Arm 중인 run은 관련 closure의 epoch/block/mandate/permit/fence를 함께 처리한다. 준비 허가 없는 PREPARED run은 자체 상태만 바꾼다. budget/part/operation identity는 보존한다.
- 새로운 Finalized view는 capture 후 같은 transaction에서 projection을 읽고 요청 결과를 저장하되 core mutation을 노출하지 않는다. 응답 유실 뒤에도 원래 최종 RunSnapshot을 회수하며 origin revision을 중복 증가시키지 않는다.
- NEW operation 전송은 봉인하고 증명 가능한 미발행만 NOT_EXECUTED로 기록한다. EmitEntered를 취소 완료로 만들지 않는다. late PREPARED의 새 Authorize 생성과 late Arm의 자동 시작을 거부하고, 실제 후속 상관 결과는 계속 기록한다.
- S journal에 optional session/epoch control identity와 PauseRun body/완전한 RunView 응답을 추가했다. 기존 operation key의 canonical encoding은 유지한다. 새 context의 명시적 halt를 이전 pause key와 구별한다.
- 실제 C++ halt request→S worker→P mTLS PauseRun, pause 응답 유실, 새 boot recovery에서 key/미수신 상태 보존을 검증했다. worker 통합은 기존5개에 pause2개를 더한7개 시나리오다.
- core의5개 추가 시나리오가 pause rollback/응답 유실·shared closure·예산/원래 응답 보존·pending Arm·late receipt/result·준비 run 범위를 확인한다. S control identity 회귀 시험도 추가했다.

[PauseRun 명세](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/EXECUTOR_PAUSE.md), [검증 기록](../../references/implementation/phase22_checks.json).

Pause는 물리 정지/취소/안전 접근/인계 확인이 아니다. 전체 restart/clearance·분기/대기/개입·handover/control-session, 상주 loop/part coordinator/liveness, 원장 전체·장기 용량/index, UI·두 제품 image·자사 stack·설치복원/인수는 여전히 남아 있다.

## 2026-09-11 · 영속 조회 계획과 실제 BT 인계 요청

- Operation.Reconcile을 현재 Executor 권한·셀 협상과 P 영속 조회 계획에 연결했다. 진행 중 계획은 operation별 병합, 후속 명시적 조회는 새 ID/generation으로 구별한다. 계획 완료에는 실제 RELEASED 저장이 필요하다.
- Host dispatcher는 기존 receipt/evidence를 읽어 원래 처리기와 T2에 적용하고 세 인계 관측을 확인한다. 생산 invocation을 새로 만들지 않는다. 일시적 조회 실패와 권한·기록 충돌을 구별했다.
- false/불충분 관측도 별도 transaction에 원문 보존한다. 동일 관측 ID의 내용 충돌은 덮어쓰지 않고 제한·사건을 commit한다. 실제 resource release는 기존 freshness/상관관계/epoch/CAS 조건을 전부 통과해야 한다.
- S의 ReconcileOperation 요청 journal·client·RequestHandover worker를 연결했다. 접수 응답과 RELEASED 관측을 분리하고, 응답 유실 및 새 boot 복원에서도 원래 key/PENDING을 유지한다. CAS 없는 조회를 ABORTED로 재작성하지 않는다.
- 실제 Linux C++ BT 요청→별도 S worker→P mTLS의 정상 인계와 조회 응답 유실 2시나리오를 추가했다. 총 9시나리오에서 원래 작업 수/요청 key·응답 상태/해제 관측을 확인했다. Host 근거는 합성 fixture이며 별도 모의 Host 통합에서 처음 support=false를 거부하고 후속 인계 근거로 두 소재를 처리했다. native effect는 2회다.
- 최초 추가 통합은 증거 출력 상대 경로 처리와 시험용 EnsureState 완료 조건 누락 때문에 각각 실패했다. 출력 경로를 절대화하고 해당 시험을 명시적 모의 유한 프로그램으로 구성했다. 제품의 완료 조건 검사는 완화하지 않았다. 실패 로그도 보존했다.

[조회·인계 명세](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/RECONCILIATION.md), [검증 기록](../../references/implementation/phase23_checks.json).

P 일반126개, S37개, Linux executor10개 및 별도 E2E6개가 통과했다. 기존 C++ 검증 이미지를 사용했고 이번 C++ 소스는 변경하지 않았다. 규범8개와 선택적 read binding을 유지한다.

전체 운영 완료는 아니다. 조회 스케줄링과 원장 index/용량, ATTENTION 상세 UI, 상주 loop/part coordinator, branch/wait/개입/CommitCheckpoint·취소/복구/control-session, 자사 stack·두 제품 이미지·설치복원/인수는 계속 남아 있다. 실물 qualification은 수행하지 않았다.

## 2026-09-11 · P 분기·대기 후보와 frozen CommitCheckpoint

- 선택적 ExecutorPlan.PrepareCheckpoint를 추가했다. P가 현재 조건·frontier·시각으로 전체 rx.executor-state.v1 후보를 만들고, 기존 Workflow.CommitCheckpoint가 이를 확정한다. 상태 artifact를 명령 봉투로 바꾸지 않았고 임의 artifact 업로드를 허용하지 않는다.
- 후보 준비는 Run revision·공정 결정·작업을 바꾸지 않는다. 준비 기록/내용 주소 artifact만 보존한다. 유효한 반복 준비는 같은 후보로 병합하며 조건 UNKNOWN은 WAITING, 이미 확정된 전이는 ALREADY_APPLIED다.
- 확정은 현재 접근권→전체 key/body→run CAS·후보 session/boot/epoch/만료→현재 운전 적격성→현재 사실로 재계산 순서다. 후보와 실제 저장된 전체 상태·activation/slot을 비교하고 T3·최종 artifact·원래 응답을 같은 commit에 보존한다.
- 분기·대기 판단을 process_transition.rs로 모았다. 기존 내부 경로와 새 통신 경로가 같은 상태 전이 및 checkpoint 저장을 사용한다. 대기는 원래 P 준비 시각을 확정하며 재요청으로 deadline을 늘리지 않는다. 성공 후보가 deadline 이후 도착하면 timeout을 다시 준비해야 한다.
- core는 준비/확정 rollback·응답 유실·만료, 현재 권한, 후보/mapping 변조, 바뀐 관측, deadline 경계, 앞선 visit의 실제 자식 슬롯 보존을 검증했다. 실제 mTLS의 분기/대기 2시험은 준비 비적용·frozen CommitCheckpoint·응답 유실 후 동일 결과·artifact 조회를 확인한다.
- 두 확정 규범의8개 파일과 기존 executor-read binding은 유지했다. 준비용 binding은 별도 고정했고 SDK67개 파일과 wire semantic fields604개로 수출했다. P 일반133개·S37개, Linux executor10개, 양쪽 clippy와 별도 E2E6개가 통과했다. 기존 S worker의9개 시나리오를 회귀 검증했으며, 분기/대기 S worker까지 검증했다고 확대하지 않는다.

[후보 준비·체크포인트 확정](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/CHECKPOINT_COMMIT.md), [검증 기록](../../references/implementation/phase24_checks.json).

다음 연결은 S Client의 준비 응답/후보 검증, 분기·대기 단계별 journal, 동일 key의 CommitCheckpoint, 응답 유실 후 P 결정/window/result의 별도 관측이다. EXPIRED·확인된 CAS 거부와 transport 미확정을 구별하는 machine-readable 재준비 처리도 함께 필요하다. 상세 ErrorDetail의 통신 처리는 아직 전체 구현으로 표시하지 않는다. 상주 loop/part coordinator·개입/복구/control-session, 후보 보존 정책·원장 index/용량, UI·자사 stack·두 제품 이미지·설치복원/인수는 계속 남아 있다.

## 2026-09-11 · S 분기·대기 worker와 확정 거부·관측 복원

- 실제 BT ResolveBranch/BeginWait를 S의 CHECKPOINT_BRANCH/START_WAIT/CHECK_WAIT journal 단계에 연결했다. P의 준비 결과와 두 artifact를 검증하고 전체 상태·기존 작업 연결이 보존된 후보만 frozen CommitCheckpoint로 보낸다.
- 대기 window 존재 여부로 시작과 결과 확인을 나눴다. 반복 WAITING은 mutation attempt를 만들지 않는다. 상태는 P가 결정하며 S는 현재 확정된 branch/window/result를 각각 관측한다.
- CommitCheckpoint의 확인된 atomic 거부에 한해 strict ErrorDetail binary metadata를 추가했다. bare status/문구·중복·malformed metadata·transport 실패는 새 key의 근거가 아니다. 정확한 만료/충돌 거부 뒤에만 새 P 상태/후보와 다음 generation을 만든다. 다른 RPC의 실패로 일반화하지 않는다.
- journal은 원래 attempt의 body/key/거부 이유 또는 PENDING을 보존한다. 다른 후보가 먼저 확정된 경우 P 결정을 관측할 수 있지만 우리 RPC 응답으로 만들지 않는다. 이미 관측한 결정과 모순된 늦은 응답도 거부한다.
- 실제 Linux C++ BT→별도 S→P mTLS/SQLite 시험에 참·거짓 분기, 대기 성공/반복 대기/timeout, checkpoint 응답 유실, 진입/응답 직후 프로세스 종료, 실제 P 시계의 후보 만료를 추가했다. 총18개 시나리오에서 새 boot 복원·원래 key/응답 상태·P 결정/작업 수를 검증했다. 만료 사례는 generation1의 EXPIRED 기록과 generation2의 다른 key/정상 응답을 함께 보존한다.
- P134개·S38개, Linux executor11개, 양쪽 clippy와 별도 E2E6개가 통과했다. 규범8개·기존 read binding·base/cell protobuf는 유지했다. 선택적 preparation binding은 구조화된 거부와 공통 decision DTO를 포함하도록 갱신했고 SDK68개 파일을 수출했다.

[실행기 분기·대기와 복원](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/runtime/rx-executor/DECISIONS_AND_RECOVERY.md), [검증 기록](../../references/implementation/phase25_checks.json).

전체 상주 loop/supervision·part coordinator, 개입/clearance/취소·명시적 restart와 continuous-control, 장기 journal/index·후보 보존/용량, 전체 ErrorDetail·UI, 자사 stack·두 제품 이미지·설치복원/인수는 남아 있다. 새 시나리오는 operator/part 시작·조건/시계를 모의 구성하고 P admission/공정 상태를 검증한다. 실제 native 결과/인계는 별도 모의 Host 시험 범위이며 실물 qualification은 수행하지 않았다.

## 2026-09-11 · 지속 BT 프로세스·private pipe·pending queue

- 생산용 C++ rx-bt-engine을 추가했다. INITIALIZE는 tree만 구성하며 무동작이다. 명시적 STEP에서만 같은 context의 상태를 읽고 요청을 제안한다. malformed/다른 context/무결성 오류는 엔진을 재사용하지 못하게 하고, 같은 context의 만료 frame은 STALE로 무시한다. HALT 뒤 STEP과 시계 override를 금지한다.
- Rust EngineProcess는 release binary SHA-256·경로/크기를 확인하고 환경/현장 argv 없이 실행한다. bounded private-pipe protocol, sequence/응답/state/context 검사, I/O deadline과 실패 latch를 갖는다. 전체 service supervisor나 native Host 종료를 대신하지 않는다.
- PendingRequests가 최대32 일반 제안과 우선 pause를 관리한다. BT는 BeginWait를 한 번만 내고 Rust가 시작 이후 결과까지 요청을 유지한다. 같은 요청의 의미 변경·잘못 연결된 완료를 거부하고, transient backoff와 공정한 대기 순서를 사용한다. mutation의 durable key/미확정 상태는 기존 journal에 남는다.
- C++는 확정 wait 결과의 변경을 막고, P가 이미 해결한 미전달 제안을 내부 큐에서 제거한다. 기존 내부 BT 시험과 생성5단계 예제도 새 binary로 검증했다.
- 기존18개 통합 중 분기/대기9개를 지속 엔진+queue로 전환했다. 같은 자식 PID, BeginWait 제안1회, 반복 대기/결과 처리, 응답 유실·만료/재시작 보존과 정상 fixture 종료의 P pause 관측을 검증했다. 별도IPC9개는 malformed/중복/잘림/크기/시간/context/immutable wait 및 생산용 시계 보호를 확인한다.
- Linux 실시간 시계 검사에서는 실제 production binary digest 검증·반복 pipe 처리·동일PID·무권한 view의 요청 없음·CLOSE를 확인했다. 입력은 합성 복원 상태다. 그 상태의 NOT_EXECUTED를 RUNNING으로 예상한 최초 시험 오류를 BT FAILURE로 정확히 수정했으며 제품 동작은 완화하지 않았다.
- 초기 IPC 시계 시험에서 재사용한 fixture 파일의 잘린 JSON을 관측했다. 사례별 독립 파일로 바꾼 뒤 통과했고, 최초 오류/FAULT 응답도 보존했다. 미관측 wait 노드가 frame.nodes에 없을 수 있는 점도 시험 입력에 반영했다.
- Tokio process/I/O 기능을 활성화하고 rx-process를 runtime 필수 의존성으로 옮겼다. offline lock 갱신은 signal-hook-registry1.4.8을 추가했으며 기존 package 버전은 변경하지 않았다. P gRPC connect/RPC에 2초 제한을 추가하고 timeout을 미적용 증거로 해석하지 않는다.

[지속 BT 엔진 명세](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/native/executor/PERSISTENT_ENGINE.md), [검증 기록](../../references/implementation/phase26_checks.json).

P134개·S40개·양쪽 clippy, 별도E2E6개, Linux14개(명시적으로 활성화한 production binary 검사 포함), C++/IPC 시험이 통과했다. 규범8개와 두 optional binding은 유지했다. 새 image는 validation image다. 전체 daemon/signal/durable stop intent·part coordinator, intervention/recovery/control-session, 원장 index/용량·전체 UI·자사 stack·두 제품 이미지·설치복원/인수는 여전히 미완료다.

## 2026-09-11 · Run/visit 실행 서비스와 durable stop intent

- Linux rx-executor-service와 공통 RunService를 추가했다. P 배정/part 대기, 현재 view·지속 planner·pending queue 조정, 통신 grace·중단 window와 SIGINT/SIGTERM 연결을 제공한다. 소프트웨어 시작 시 P admission이나 part를 만들지 않는다.
- 중단 의도를 BT 단계 요청과 분리한 run-scoped journal에 먼저 보존한다. 실행 전 root/part가 없어도 중단할 수 있다. 시도별 key/session/expected revision은 고정하고, 응답 유실 뒤에는 원래 ENTERED와 응답 부재를 유지한다. P 제한 상태의 관측을 RPC 응답으로 꾸미지 않는다.
- 정상 요청을 동결한 뒤 planner만 닫고 P pause를 확인한다. 미응답은 Pending으로 남긴다. restart는 stop intent를 먼저 처리하며 BT를 띄우거나 기록을 지우지 않는다. 다른 executor/실행 세대에 오래된 중단 의도를 자동 적용하지 않는다.
- 로컬 journal 실패 시 planner를 동결하고 안정된 메모리 key/body로 P pause를 시도한다. 결과에 durability_fault를 남기며, 이를 durable stop 보존으로 주장하지 않는다. run 제어 조회는 실제 checkpoint artifact의 cell/recipe/state/연결도 검사한다.
- 실제 서비스 loop·별도 S·지속 C++·P mTLS/SQLite 통합6개를 추가했다: 실행 중/배정 전 중단, pause 응답 유실, 의도 commit 직후 종료, journal 장애, P pause 미응답. 전체24개에서 원래 기록·재시작 BT 기동0회·작업 수·미수신 응답을 검증했다.
- P134개·S42개, Linux16개(production planner 검사와 Linux service binary compile 포함), 양쪽 clippy·별도E2E6개가 통과했다. 규범8개·두 optional binding·SDK68개는 유지했다.

[실행 서비스와 중단 기록](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/runtime/rx-executor/SERVICE_LIFECYCLE.md), [검증 기록](../../references/implementation/phase27_checks.json).

이는 지정한 run/visit 서비스다. GraphComplete가 P part/run 완료를 뜻하지 않으며 part coordinator·같은 run의 명시적 restart/rebind는 후속이다. 전체 P/Host/S supervisor·실제 CLI signal-to-P 통합·장비 종료, intervention/clearance/cancel/control-session, 긴 원장/index·전체 UI·자사 stack·두 제품 이미지·설치복원/인수도 남아 있다. 시연 장비의 실물 qualification은 수행하지 않았다.

## 2026-09-11 · 직렬 소재 admission·완료·다음 context

- Production.Inspect/CompletePart를 별도 optional binding으로 추가했다. 첫 part 이전부터 종료 이후까지 part ID/ordinal/revision/disposition, budget·Run checkpoint·권한/epoch·시각을 같은 P control cut에서 읽는다. base/cell 및 기존 optional read/prepare binding은 유지한다.
- P completion을 공통 transition으로 정리했다. 실제 선택된 graph 결과·인계 근거를 확인한 뒤 part와 run/mandate·사건·응답을 원자적으로 갱신한다. 이미 완료한 part의 재요청은 새 revision/예산 소비를 만들지 않는다. 전체 body/key·현재 접근권·run/part CAS를 검사한다.
- S는 BEGIN_PART/COMPLETE_PART journal과 별도 part 관측을 추가했다. 원래 미수신 응답을 만들지 않고 P의 기존 part ID를 회수한다. 같은 revision의 다른 값과 모순된 늦은 part reply를 거부한다.
- 서비스의 기본 SerialProduction이 최초·다음 part를 조정한다. P 완료가 검증된 CompletedVisit으로만 planner를 retire하고, CLOSE의 run-pause 제안을 전달하지 않는다. 이전 context는 보존해 다음 part에서 새로운 session/epoch를 자동 채택하지 않는다. ManualVisit은 별도 옵션으로 유지한다.
- 두 소재를 처리하는 정상/첫 Begin 응답 유실/첫 Complete 응답 유실 3통합을 추가했다. P part2개·budget 소비2회·work2개·planner2회, 중간 pause 없음, 최종 P run 완료와 재시작 추가planner0회를 확인했다. Host 완료/인계는 명시적 합성 근거이며 실제 모의 Host 전송은 별도 기존 시험이다.
- P136개·S43개, Linux17개, 양쪽 clippy·별도E2E6개가 통과했다. worker 통합은 총27시나리오다. 규범8개는 유지하고 SDK72개와 wire semantic fields614개를 수출했다.

[직렬 소재 조정](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/runtime/rx-executor/PRODUCTION_COORDINATOR.md), [검증 기록](../../references/implementation/phase28_checks.json).

남은 것은 병렬 소재/실물 genealogy, 명시적 restart/rebind, intervention/clearance/cancel/control-session, 큰 run의 index/paging/용량, 전체 supervisor·UI·자사 stack·두 제품 이미지·설치복원/인수다. 실물 qualification을 수행한 것으로 표시하지 않는다.

## 2026-09-11 · 개입 사건 접수·보류·알림 확인 UI

- P Case/Open/Get/List와 notification ACK를 구현했다. 진단 사건은 non-latched block으로 새 admission을 보류하고 epoch/ACTIVE mandate를 유지한다. 접근·복구·정비·변경 사건은 기존 closure invalidation과 같은 transaction으로 허가를 철회하고 case/block membership을 보존한다.
- 현재 actor·lead 역할/영향 셀, 실제 operation 참조, 전체 key/body와 case CAS를 확인한다. 알 수 없는 scope/소재 참조는 불명 표시와 cell/resource closure로 보존하며 확인된 MaterialState로 만들지 않는다.
- ACK는 실제 계정·보고 UTC·P 기록 시각과 typed notification assertion artifact를 보존한다. case 상태·참여자·epoch/block·운전/접근/reset/restart를 바꾸지 않는다. 중복 key는 확인 기록을 늘리지 않고 다른 case의 제한도 제거하지 않는다.
- frozen executor Cell.OpenCase/GetCase와 개발 HTTP/운영 화면의 사건 목록·ACK를 연결했다. UI는 ‘알림 확인과 작업 허가는 별도’임을 표시하고 참여 기록 없음과 사람 없음도 구별한다. 생성 catalog/UI와 실제 ProcedureRecord/clearance/restart는 아직 연결하지 않는다.
- core2개와 HTTP1개 시험을 추가하고 실제 mTLS 사건 조회를 기존 API 시험에 포함했다. 브라우저는 commit 뒤 ACK 응답을 잃고 reload한 다음 같은 body/key로 회수했다. record1개·CONTAINMENT_PENDING·동일 epoch/block을 확인했고 desktop/mobile·JavaScript 오류를 검사했다. 화면을 직접 확인했다.
- P139개·S43개·양쪽 clippy, UI3개/build/format·브라우저, 별도E2E6개(실행기27시나리오)가 통과했다. time0.3.55의 parsing 기능을 직접 사용했으며 기존 package 버전은 바꾸지 않았다. 규범8개·세 optional binding·SDK72개는 유지한다.

[개입 사건과 알림 확인](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/INTERVENTION_CASES.md), [검증 기록](../../references/implementation/phase29_checks.json), [운영 화면](../../references/implementation/phase29-browser-final/operator-cases.png).

완성된 개입/복구 절차가 아니다. typed 외부 절차 근거와 stale-CAS 사실 보존, 절차 진입/참여자·인수, recovery plan/step slot, clearance cohort·restart/비운전 종료, 전체 원장/보존, 생성 catalog/UI·제품 supervisor·자사 stack/두 이미지/설치복원·인수는 후속이다. 실장비나 물리 접근 시험은 수행하지 않았다.

## 2026-09-11 · typed 절차 보고·사실 보존·정책 기반 상태 전이

- 외부 절차/의존 근거와 cell/definition/envelope, 허용 actor/step·조건/source·age를 가진 정책을 추가했다. 기본 authority는 정책 admission을 거부하고, 승인 및 승격 시 현재 verifier를 사용한다. 시험은 명시적 simulation authority다.
- typed assertions와 immutable record/source-event ID를 확인해 실제 보고를 저장한다. WorkStarted/Finished·격리/reset/configuration 같은 외부 상태 보고는 필요한 latch·조건/qualification 제한을 남긴다. 업무 CAS가 stale이어도 사실/차단을 commit하고 transition_error와 record/case ID를 반환한다. 응답 유실은 같은 key로 회수한다.
- entry에는 현재 lead 역할/전체 scope/Host fence·정의된 P 조건 근거가 필요하다. 이전 entry context와 현재 epoch가 다르면 다시 확인해야 한다. configuration_changed는 새 진입을 제한한다. 개인별 작업 종료·전체 인원/인수를 모아도 REVALIDATING까지이며 READY_FOR_RESTART를 만들지 않는다.
- 개발 HTTP inline report와 frozen RecordProcedure의 저장 artifact 참조 경로를 같은 처리기에 연결했다. mTLS service identity 외에 실제 Operator/RecoveryLead 역할도 필요하다. 일반 operator-API peer session·전용 절차 입력 UI는 후속이다. notification ACK와 procedure 기록/카운트는 구별한다.
- core2개(정상 다인 절차/외부 epoch 상실 분기 포함)·HTTP1개 시험이 stale-CAS 사실 보존, rollback/commit 응답 유실, fence/조건 전 진입 거부, 한 명의 종료로 다른 참여자 제한을 해제하지 않음을 확인했다. P142개·S43개·양쪽 clippy, UI3개/build/format·브라우저와 별도E2E6개가 통과했다.
- 회귀 중 모의 시계 파일의 truncate 갱신이 잘린 JSON을 만드는 문제가 드러났다. 엔진은 그 값을 거부했다. 전용 clock 디렉터리와 원자 rename으로 교체하도록 fixture를 수정하고 다시27시나리오를 통과했다. 생산용 clock/판정 규칙은 완화하지 않았다.

[절차 사실과 상태 승격](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/PROCEDURE_REPORTS.md), [검증 기록](../../references/implementation/phase30_checks.json).

미완료 범위는 실제 release/package procedure verifier·물리 절차 인수, recovery plan/guarded operation, clearance cohort·restart/close, 새로운 구성 qualification, operator service session/전용 입력 화면, 원장/보존·전체 supervisor·자사 stack·두 제품 이미지·설치복원이다. 실장비 안전성/운전 자격 검증으로 확대하지 않는다.

## 2026-09-11 · 비운전 clearance·사건 종료와 종료 후 보고

- `PrepareClose`와 `CloseWithoutRestart`를 application/Runtime 및 개발 HTTP에 연결했다. 외부 종료 절차·의존 근거, 영향 셀 definition/envelope/조건/TTL을 가진 별도 정책을 사용하며 기본 verifier는 거부한다. 준비/소비 모두 현재 verifier를 검사한다.
- 현재 lead·영향 셀 접근권, 셀/사건 CAS, 전원 작업 종료·실제 인원 확인/인수 record, 현재 Host Fence·조건 근거를 검사한다. clearance는 전체 context·정확한 evidence IDs·정책·기간에 묶이며 준비만으로 상태를 확대하지 않는다. target run/restart plan은 요구하지 않는다.
- 소비와 대상 사건 종료·OUT_OF_SERVICE latch·원래 응답을 원자적으로 저장한다. 공유 범위 전체의 기존 권한을 철회하고 대상 사건 소유 차단만 정리한다. 다른 사건/원인의 차단, UNKNOWN 결과와 자원 quarantine/holder를 보존한다. ArmCell·native reset/이동/취소를 생성하지 않는다.
- 물리 변화 보고는 이전 인원 확인/인수 결론을 무효화한다. 동일 record가 새 요청 key로 재전송되어도 이전 작업 전이를 재실행하지 않는다. CLOSED 사건의 새 비물리 보고는 기록만 남기고, 새 물리 변화는 사실·차단·case membership을 다시 기록한다. 과거 종료 영수증은 보존한다.
- core6개(여러 장애·변화 분기 포함)와 개발 HTTP1개 시험을 추가했다. 준비/소비 rollback·응답 유실, 만료/CAS/epoch/source/조건/공유 범위/역할 변경, 한 번 소비, 다른 사건 차단과 UNKNOWN 자원 유지, 종료 후 보고를 확인했다. P149개·S43개·양쪽 clippy, UI3개/build/format, 기존 별도 E2E6개(실행기27시나리오)가 통과했다.
- 운영 앱은 새 OUT_OF_SERVICE 상태를 해석하며 ‘운전 제외 · 별도 재검증 필요’로 표시한다. 전용 종료 화면이나 브라우저 종료 플로를 구현·검증했다고 표시하지 않는다. 규범8개·세 optional binding·SDK72개는 유지했다.

[비운전 종료 명세와 경계](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/NON_OPERATING_CLOSURE.md), [검증 기록](../../references/implementation/phase31_checks.json).

남은 범위는 실제 package/release procedure verifier, 무진입 진단/불명 scope/새 구성 종료, 담당자 변경·여러 원 셀 cohort, 전체 CellContext projection 및 frozen gRPC·operator service peer/전용 화면, recovery plan/step·restart/cancel/control-session이다. 전체 원장·보존/제품 supervisor·자사 stack·두 제품 이미지·설치복원도 계속 남아 있다. 물리 셀은 NOT_COMMISSIONED이며 이 시험은 현장 격리·접근·안전성·납품 인수를 입증하지 않는다.

## 2026-09-11 · 기록된 셀 공개 상태·운영 API 전송 세션

- Cell의 RX 운영 mode/commissioning과 Block의 실제 생성 revision/case를 저장한다. 최초 시작은 모든 Arm 확인 뒤 Run/Mandate와 함께 모드를 commit한다. latched 상실·개입·비운전 종료의 상태와 기존 자격 기록을 구별한다. 서로 다른 실행 목적이 같은 셀 운영 문맥을 동시에 차지하지 못한다.
- frozen Cell.Inspect와 canonical HTTP GET 조회를 연결했다. 현재 사용자/서비스의 scope·session/certificate·셀 협상과 같은 저장 cut의 CellContext를 사용한다. 없는 metadata를 현재 revision/임의 모드로 채우지 않고 UPGRADE_REQUIRED로 구별한다.
- OPERATOR_API base/cell 서비스 협상을 추가했다. 서비스 계정과 사람/Host/Executor 역할을 구별하고 인간 로그인 세션으로 열지 못하게 한다. 새 boot/binding은 이전 서비스 세션을 퇴역시키되 셀/run/executor 권한을 바꾸지 않는다. 현재 역할·셀 범위·인증서·협상을 조회 때마다 확인한다. 인간 쓰기 RPC의 위임/단말 binding은 후속이다.
- SQLite schema4 compatibility barrier를 추가했다. 기존 raw record/request/event/outbox/control 자료를 바꾸지 않으며 이전 decoder가 이 저장소를 열지 못한다. schema3→4와 backup의 record bytes 보존·future version 거부를 시험하고 이전 source archive의 downgrade guard도 확인했다.
- core3개·HTTP2개·storage1개 시험을 추가하고 실제 TLS fixture에 운영 API 조회·재접속·scope/쓰기/실행기 권한 거부를 포함했다. 운전 모드 기록으로 셀 revision이 바뀌므로 고정/시작 전 revision을 쓰던 인계·gRPC·Host 시험 client를 현재 authoritative 조회로 수정했다. 생산 CAS 규칙은 완화하지 않았다.
- P155개·S43개·양쪽 clippy, UI3개/build/format·브라우저와 별도 E2E6개(실행기27시나리오)가 통과했다. 화면은 ‘RX 운영 모드’와 자격 기록/재검증 필요를 구별한다. 기존 미등록 셀·응답 유실 복원·모바일 화면도 확인했다. 규범8개·세 optional binding·SDK72개는 유지한다.

[셀 상태·서비스 신원·저장 호환](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/CELL_CONTEXT_AND_OPERATOR_PEER.md), [검증 기록](../../references/implementation/phase32_checks.json), [운영 화면](../../references/implementation/phase32-browser-final/operator-overview.png).

인간 사용자·서비스·등록 단말의 binding과 frozen 인간 쓰기 RPC, legacy metadata의 명시적 검토/보완, 실제 모드 전이·qualification 갱신, recovery/restart, 전체 journal/SSE·보존, 제품 supervisor·자사 stack·두 제품 이미지·설치복원은 미완료다. 실제 장비의 모드나 물리 안전기능을 RX mode 표시로 대신하지 않는다.

## 2026-09-11 · 사용자·등록 단말·직접 HTTPS 신원

- 등록 단말용 `TerminalHttps` ingress를 추가했다. 실제 TLS client certificate의 leaf fingerprint와 비밀번호 검증을 통해 writer가 현재 사용자/Terminal을 결합한 Session을 발급한다. forwarded header/body의 단말 주장은 신원 근거로 사용하지 않는다.
- Session에 Terminal ID·인증서·등록 revision을 저장하고, 매 요청마다 현재 binding·역할·허용 셀 교집합을 검사한다. cookie는 해당 TLS 단말에 묶이며 Secure/HttpOnly/SameSite=Strict로 발급한다. 다른 단말 replay·오래된 등록·잘못 조립한 Identity를 거부한다.
- 단말 등록 변경은 관련 cell closure의 권한을 같은 transaction에서 철회하고 pending start도 무효화한다. 동일 내용의 정확한 CAS 재적용은 기존 revision을 유지한다. 서비스 계정에 사람 역할을 추가해 ProcedureRecord를 작성하거나 case lead가 되는 이전 초안 경로도 차단했다.
- TLS/HTTP 연결 수·크기·대기·수명을 제한하고 HTTP drain과 writer/native 효과를 구별한다. 실제 TLS 시험은 무인증서/다른 CA/미등록·header/body 사칭·cookie replay·scope·재로그인/로그아웃, 정상 ARMING 접수·같은 key 회수·등록/계정 철회 후 거부, NOT_COMMISSIONED 및 미완성 handshake shutdown을 확인했다. 실장비 Arm 응답이나 실행 완료는 생성하지 않았다.
- schema5 barrier로 새 Session 의미를 모르는 decoder를 차단한다. phase32에서 P schema4와 S SDK schema3가 달랐던 동기화 누락을 확인해 공유 storage 및 두 migration을 함께 수출했다. SDK payload74개(별도 source-lock 포함75개)다. `check_host_sdk.py`는 자체 integrity와 현재 P export 일치를 모두 검사하며, 실제 phase32 SDK archive의 stale 상태를 검출했다.
- macOS P160개·S43개·양쪽 clippy, 격리 Linux P160개·S executor17개, 기존 별도 E2E6개(실행기27시나리오), UI3개/build/format·브라우저를 확인했다. Linux 재빌드 중 한 linker가 signal9로 종료된 실행은 실패로 남겼고, CARGO_BUILD_JOBS=1로 재실행해 통과했다. 테스트/권한 조건은 완화하지 않았다.

[직접 HTTPS와 신원 경계](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/TERMINAL_IDENTITY.md), [검증 기록](../../references/implementation/phase33_checks.json), [SDK stale 회귀](../../references/implementation/phase33_sdk_regression.json).

이것은 API ingress 구성 요소다. 제품 supervisor/daemon·S UI와의 HTTPS routing·실제 브라우저 단말 인증서 배포/회전, OPERATOR_API gRPC 사용자 위임과 frozen 인간 쓰기 연결은 남아 있다. recovery/restart/cancel/control-session·전체 journal/보존·자사 stack/두 이미지/설치복원도 계속 미완료다. 단말 인증은 현장 위치·물리 접근·장비 안전기능을 입증하지 않는다.

## 2026-09-11 · 플랫폼 실행 파일·process-stop barrier·첫 runtime image

- `rx-platformd init/run`을 추가했다. catalog/credentials/TLS 파일 pin과 권한·TLS 구성을 검사하고, 최초 설치를 임시 디렉터리에서 완성한 뒤 공개한다. 기존 설치를 덮어쓰지 않고 재시작 때 초기 계정/셀 catalog를 다시 적용하지 않는다. 현재 qualification authority는 NOT_CONNECTED인 uncommissioned draft다.
- HTTPS·gRPC·단일 writer를 묶고 Linux shared boottime을 사용한다. 두 주소를 먼저 확보하고 OS runtime-directory/SQLite 잠금으로 중복 프로세스를 막는다. 상태 파일은 atomic rename과 소유 schema/installation 확인으로 기록한다.
- SERVING→STOP_REQUESTED→STOP_COMMITTED를 영속화했다. stop은 먼저 새 authority를 차단하고 cell closure를 철회한다. API drain 후 writer를 닫으며 UNKNOWN·retained work·Host Fence 미확인·열린 case를 그대로 보고한다. 이 P 프로세스 종료를 물리 정지/지지 인계로 표시하지 않는다. schema6 및 동기화된 SDK75개를 사용한다.
- 실제 composition 시험은 TLS 로그인·조회와 gRPC 협상·조회, 두 번의 기동/종료, 변경된 계정 권한 보존, 중복 실행·잘못된 pin 거부를 확인한다. Linux에서는 실제 executable과 SIGTERM·shared clock도 확인했다.
- digest로 고정한 Rust builder/Ubuntu runtime의 `rx-platform:runtime-draft` arm64 이미지를 빌드했다. 실제 이미지에서 USER10001:10001, read-only root, cap-drop ALL, read-only config/독립 data volume, HTTPS health, SIGTERM과 STOP_COMMITTED를 확인했다. 시험 container/volume/인증서는 별도로 만들고 정리했다.
- 첫 외부 HTTPS image smoke에서 시험 CA/leaf의 같은 기본 DN과 누락된 issuer 식별 때문에 OpenSSL이 체인을 거부했다. DN·AKI를 명시한 시험 인증서로 고쳤고 인증서 검증은 끄지 않았다. 제품 TLS/권한 조건을 완화하지 않았다.
- macOS P163개·S43개, Linux P164개(실제 process 시험 포함), 별도 E2E6개(실행기27시나리오), 양쪽 clippy·브라우저 회귀와 image smoke를 확인했다. 규범8개와 optional binding은 유지했다.

[실행 파일·기동/종료·이미지 명세](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-platformd/README.md), [검증 기록](../../references/implementation/phase34_checks.json), [실제 이미지 smoke](../../references/implementation/phase34_image_smoke.json).

자동 Host 발견/등록·dispatcher 구성, 실제 qualification authority, solutions 필수 스택 제품 이미지, 전체 현장 종료·지지 인계, 설치/업데이트/복원·사용자 위임/복구 전체는 미완료다. 이미지 한 개와 SOFTWARE_READY 상태를 전체 제품/실물 운전 준비 완료로 세지 않는다.

## 2026-09-11 · 솔루션 자사 필수 스택·CPU runtime image

- 자사5개와 interfaces/hand 전이3개를 정확한 Git commit으로 고정하고 원본 작업 트리를 수정하지 않은 archive로 빌드했다. 42개 ROS package를 모두 컴파일했다. 첫 GUI build의 메모리 부족은 compiler/Qt 병렬 수를 1로 제한해 해결했고 패키지를 제외하지 않았다.
- ROS base/metadata commit, ONNX Runtime 배포 archive와 정책11개 파일을 pin했다. 초기 검색에서 빠진 Sapiens 정책4개를 Git archive에서 확인해 정정했다. source tree 및 지원 catalog의 commit/파일 hash를 실제 build 입력과 대조한다.
- 설치42개, ELF69개 동적 의존성, catalog controller/hardware plugin17개, 자산11개와 ONNX CPU Session4개를 검증했다. ONNX runtime loader 경로 누락은 ldconfig 설정으로 수정했다. MoveIt의 별도 template XML을 RX catalog plugin 판정과 혼합하지 않았다.
- `rx-solutions:runtime-draft` arm64 이미지는 자사 overlay·Rust executor/compiler·production BT engine·운영 UI bundle을 포함한다. USER10001, read-only root, cap-drop ALL, 장치 미매핑에서 진단 기동·42개 package/22개 profile 표시·control POST 거부·정책 변조 거부·SIGTERM 종료를 확인했다. entrypoint가 ROS/driver/BT/policy 프로세스를 기동하지 않는 것도 확인했다.
- image의 APT1824개 inventory를 고정하고 최종 runtime이 달라진 선택 결과를 거부하도록 했다. 오래된 .deb를 보관하는 mirror/offline 공급망과 amd64/GPU/sensor variant는 아직 미완료다. runtime draft에 일부 build/GUI/simulation 도구가 남아 있다는 제한도 기록했다.
- S Rust43개·clippy와 제품 이미지 안의 Linux executor17개를 확인했다. Sapiens 자체 gtest7개 실행 파일의46개 시험 및 CTest13개 그룹이 실패 없이 완료됐다. cppcheck2.13의 알려진 성능 문제로 upstream이 skip한87개 항목은 통과로 세지 않는다. XML schema 외부조회 실패는 고정된 공식 XSD의 로컬 catalog로 해결해 네트워크 없는 시험을 유지했다.

[스택·이미지 구성과 한계](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/dependencies/NATIVE_IMAGE.md), [검증 기록](../../references/implementation/phase35_checks.json), [실제 image smoke](../../references/implementation/phase35_image_smoke_verified.json).

두 레포의 runtime draft image가 존재하지만 전체 제품/실물 지원 완료는 아니다. 자동 Host/driver 준비·P permit 연결·전체 supervisor/복구/운영 API 위임과 현장 qualification이 남아 있다. upstream launch를 직접 실행할 수 있다는 것과 RX가 그 실행을 승인한 것은 구별한다.


## 2026-09-11 · Host 상태 조회·초기 연결·사용권 갱신

- 별도 optional `rx.host.read.v1` 계약과 공유 snapshot DTO를 추가했다. 인증·base/cell 협상 뒤 Host boot, 두 원장, 구성·epoch·자원 fence, 미결 작업과 요청한 source의 세대·취득 시각·품질을 읽는다. 지원하지 않는 관측은 unavailable로 반환하며 READY 값을 만들지 않는다.
- 실제 TLS 서버 인증서 pin을 검증하는 HostClient와 초기 연결 조정기를 연결했다. P에 먼저 인증된 evidence producer의 boot/journal/session과 H의 조회 결과가 일치해야 한다. 두 방향을 한 제품 launcher로 기동하는 구성은 아직 미완료다.
- P가 연결 계획·Fence/Acquire 요청 ID·자원 fence·원래 시각을 먼저 저장한다. 응답을 검사한 뒤 HostRegistration·Fence 근거·원래 receipt를 원자적으로 저장한다. 재전송 시 나중 시각을 사용해 lease를 연장하지 않는다. source 관측의 P Fact 반영과 qualification·Arm은 별도다.
- 갱신도 요청 ID/sequence/원래 시각을 먼저 저장한다. 현재 허가 문맥이 바뀌면 갱신을 거부한다. 연결 서비스는 초기 publisher를 기다리고, 연결 뒤 dispatcher와 갱신을 운영한다. 기존 연결이 깨졌을 때 새 장비 세대나 grant를 자동 채택하지 않는다.
- 원장 연속성 검토에서 동일 boot의 delivery journal 교체가 계획 재사용 경로를 통과할 수 있는 누락을 수정했다. 미확정/확정 계획과 같은/새 전송 세션의 네 분기에서 거부하고 원래 계획·요청 ID가 보존되는지 검증했다. 컨테이너 fixture의 Host client 인증서 종류와 경로 이식도 보완했다.
- macOS P168개·S43개와 양쪽 clippy가 통과했다. 별도 Host TLS 통합3개, publisher·reader·worker 각1개의 증거를 확인했다. worker 통합은 기존27시나리오를 포함한다. 새 원장 검사 뒤 P 전체와 Host 통합을 재실행했다. frozen 규범8개·기존 optional3개는 유지했고, 새 Host binding과 SDK79개를 확인했다.
- 두 runtime draft 이미지를 재빌드하고 각각 비루트/read-only/권한 제한·기동·SIGTERM을 검증했다. P는 연결 대상 publisher가 없는 구성에서도 API를 기동·종료했다. S는 제어 요청과 변조된 정책을 거부하며 native 프로세스를 시작하지 않았다. 최종 Linux P169개 시험도 통과했다. 파일별 근거는 아래 검증 기록에 둔다.

[Host 연결과 제한](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-host-client/HOST_CONNECTION.md), [검증 기록](../../references/implementation/phase36_checks.json).

지속 관측의 원자적 수집·P 조건 반영, 연결 Attention의 운영 화면/상태 파일 노출, 명시적 rebind·공유 자원 multi-cell lease, 실제 ROS/PLC adapter 및 Host/driver supervisor는 남아 있다. 기본 qualification authority는 연결되지 않았으며, 실물은 NOT_COMMISSIONED다. UI와 자사 native 동작 시험은 해당 소스가 바뀌지 않은 이전 증거를 유지하고 이번 단계에 재검증했다고 표시하지 않는다.


## 2026-09-11 · 원자적 관측 수집·유지 조건 만료 감시

- Host의 반복 조회를 현재 producer/Host 세대·두 journal·definition/envelope/environment와 대조한 뒤 P의 조건 근거로 받는다. Host별 지정 source를 정확히 포함해야 하며 최대 age는 P FactSpec을 사용한다. 원래 취득 시각·품질·evidence ID를 보존한다.
- 한 묶음의 descriptor 전체를 먼저 검사하고 immutable evidence/현재 source 값/필요한 철회를 한 transaction으로 저장한다. 모든 값이 갱신된 뒤 유지 조건을 평가하여 일부 값만 바뀐 중간 상태의 오판을 막는다. 이는 물리 센서들의 동시 측정 보장은 아니다.
- 무결성 모순과 세대 상실을 명시적 결과로 돌려주며 같은 묶음의 다른 사실도 보존한다. 같은 세대 상실이나 지속 disputed를 매번 새 차단으로 쌓지 않는다. 새 정상 관측 뒤 다시 disputed가 된 경우는 새 이상이다. 기존 차단과 철회된 mandate는 자동 복원하지 않는다.
- 초기 grant의 100 ms 현재성 창과 관측 기록을 구별했다. 지연 관측은 원래 시각으로 저장하고 더 최신인 값을 덮어쓰지 않는다. 오래된 값의 조건 평가는 UNKNOWN이며, Received는 유효/운전 가능을 뜻하지 않는다.
- P에 독립 유지 조건 감시를 추가했다. 네트워크 조회와 별개로 활성 Run/시작 시도의 조건 age를 확인하고 상실 시 영향 closure의 mandate/permit/Fence를 원자적으로 처리한다. 원래 true 관측을 거짓 false로 고치지 않는다. 25 ms는 요청 주기이며 검증된 최악 반응시간이 아니다.
- 연결 서비스가 dispatcher·조회 worker·lease 갱신을 함께 소유하고 종료 시 회수한다. P 실행 파일은 별도 유지 조건 감시를 하나 기동한다. writer 실패는 서비스 실패로 전파한다. 관측은 grant·qualification·Arm·작업 완료를 생성하지 않는다.
- macOS P177개와 clippy, 별도 통신 E2E6개가 통과했다. Host 통합은 수동 FactRecord 주입을 실제 조회 수집으로 바꾸고 반복 reader가 새 evidence를 저장하면서 native 실행 횟수는 늘리지 않음을 확인했다. 관측 코어7개·감시 수명주기2개를 추가했으며 worker E2E는 기존27시나리오를 유지한다. 소스 고정 후 Linux P178개와 최종 플랫폼 이미지의 비루트/read-only 기동·SIGTERM도 통과했다. 파일별 근거는 아래 검증 기록에 둔다.
- S 소스241개는 phase36과 일치한다. 공유 SDK79개·규범8개·optional binding4개를 유지했다. 변경되지 않은 S/native/UI의 이전 검증은 보존하며 이번 단계의 재검증으로 세지 않는다.

[관측 수집·감시와 제한](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/OBSERVATION_INGESTION.md), [검증 기록](../../references/implementation/phase37_checks.json).

실물 source/profile qualification, 연결·관측 상태의 운영 화면 통합, 명시적 rebind·전체 supervisor, 순간 신호의 event/latched 계약과 장기간 기록 보존·용량·반출은 남아 있다. snapshot polling은 모든 과거 변화의 수집을 보장하지 않는다. 첫 물리 셀은 NOT_COMMISSIONED이며 이 단계는 현장 반응시간·보호 기능·납품 인수의 증거가 아니다.


## 2026-09-11 · 운영 조건·관측 근거 화면

- P overview의 같은 읽기 transaction에 source 관측·등록된 Host 권한 문맥·시작/유지/작업 조건 진단을 연결했다. 현재 사용자·단말의 셀 범위를 먼저 적용하고 다른 셀의 근거를 노출하지 않는다. 조회는 자격·차단·run·native 상태를 변경하지 않는다.
- domain의 실제 조건 평가기를 사용하며 source가 유효한 false인 경우와 근거 불가 UNKNOWN을 구별한다. 현재 FactSpec의 source Host·취득 오차 제한도 공통 Fact 구성에서 검사하여 admission과 진단에 함께 적용했다.
- UI에 ‘운전 조건’을 추가하고 취득 시각/age·품질·세대·근거 ID와 판정 이유를 보여준다. 조건이 PASS여도 운전 자격 미등록·차단·개입은 별도로 남는다. Host 권한 문맥을 TCP 연결 또는 실제 장비 준비로 표시하지 않는다.
- 표시 유효시간은 source/grant의 남은 시간과 3초 상한으로 제한한다. 브라우저 요청 시작의 monotonic 시각에 묶어 응답 지연이 이를 늘리지 않게 했다. 만료/조회 실패에는 재조회 필요를 표시하고 이전 판정을 구별한다. 실제 쓰기는 기존 서버 검사를 다시 거친다.
- P181개·clippy, UI6개/build/format과 통신 E2E6개가 통과했다. HTTP의 셀 범위·권한 철회 검증에 진단 필드를 포함했다. 원래 요청의 응답 유실/회수, 검토 revision 고정과 개입 ACK 흐름도 브라우저에서 유지됐다.
- 실제 로컬 API의 관측 없음 화면과 P 시험이 생성한 PASS/FAIL/expired read-model의 표시를 확인했다. 후자는 응답 경계의 UI 시험이며 실행 중인 서버에 장비 관측을 주입한 것이 아니다. 응답 지연·desktop/mobile·JavaScript 오류를 검사하고 화면을 직접 확인했다.
- 두 이미지를 새 API/UI로 재빌드하고 비루트/read-only 기동·종료를 검증했다. S Rust/native/dependency/SDK는 변경하지 않아 이전 동작 검증을 유지했다. 규범8개·optional4개·SDK79개도 유지한다. Linux P182개도 통과했다. 최종 파일·화면·이미지의 근거는 검증 기록에 남긴다.

[운영 조건의 모델·표시 경계](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/OPERATOR_CONDITIONS.md), [화면](../../references/implementation/phase38-browser-final/operator-conditions-pass.png), [검증 기록](../../references/implementation/phase38_checks.json).

실물 신호와 화면의 현장 인수, volatile 연결/reader/dispatcher 상태 통합, 공식 ConditionEvaluation wire 매핑, 장비용 표시명/설명, 전체 paging/SSE·복구 화면과 공정 편집은 미완료다. 첫 물리 셀은 NOT_COMMISSIONED이며 조회 PASS를 운전 허가로 사용하지 않는다.


## 2026-09-11 · 현재 실행 서비스 진단·보고 소유권

- writer 소유의 volatile registry에 Host 연결·관측 조회·전달 루프 상태를 연결했다. heartbeat를 SQLite 권한 원장에 쌓지 않고 Application 재생성 시 이전 상태를 복원하지 않는다. 진단은 qualification/grant/permit/작업 결과를 바꾸지 않는다.
- 구성 대상을 전체 검증한 뒤 owner를 발급한다. 초기화 미수행·미구성·첫 보고 대기를 구별하고 잘못된 inventory의 부분 적용을 막았다. 현재 boot/definition/envelope에 owner를 묶고 sequence 후퇴·이전 owner 보고를 거부한다. owner 교체는 진단 식별자 교체이며 실제 장비 재시작이 아니다.
- 실제 ConnectionService/ObservationReader/Dispatcher 채널을 relay에 연결했다. owner와 service의 host/cell이 다르면 거부한다. producer가 없으면 인증 대기이며, 관측을 아직 받지 않았거나 전달 루프가 시작되지 않은 상태를 따로 표시한다.
- 보고의 현재성과 worker의 활동 시각을 구별한다. heartbeat만 새로 와도 오래된 수신/pass 시각은 늘어나지 않는다. 3초 경과 시 오래된 상태로 분류하고, UI에도 최근 응답/루프 확인 필요를 표시한다. 전달 pass는 native 완료나 queue 해소가 아니며 오류 이력도 현재 작업 실패로 바꾸지 않는다.
- 현재 사용자/단말의 허용 셀에만 상태를 붙인다. opaque owner ID·원시 오류 문자열·Host의 전역 처리 횟수를 브라우저에 보내지 않는다. 다른 셀의 보고와 이전 Runtime의 owner를 거부하는 시험을 추가했다.
- P185개·clippy, UI8개/build/format, 통신 E2E6개와 브라우저 검증이 통과했다. 실제 P HTTPS 기동 시험에서 인증 대기 보고를 확인했고, Host TLS 통합에서 실제 dispatcher pass 시각을 확인했다. 브라우저는 API 시험이 만든 current/stale/heartbeat-only/replaced snapshot을 표시 경계에서 검증했다. 장비 상태 주입이나 물리 검증으로 확대하지 않는다.
- desktop/mobile에서 보고는 현재지만 worker 활동은 오래된 경우를 직접 확인했다. 기존 조건 만료·요청 응답 유실/회수·개입 ACK 흐름도 유지했다. 두 이미지의 비루트/read-only 기동·종료와 Linux P186개 시험도 통과했다. 최종 결과는 검증 기록에 남긴다.

[Host 서비스 진단의 책임·시간·수명](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-runtime/HOST_SERVICE_HEALTH.md), [화면](../../references/implementation/phase39-browser/operator-service-detail.png), [검증 기록](../../references/implementation/phase39_checks.json).

실제 ROS/controller/GPU 등 하위 프로세스 health, 자동 Host 배치·재시작·명시적 rebind, 로컬 상태 파일의 전체 서비스 요약, 운영자 지원 로그와 설치/복원·현장 인수는 남아 있다. 첫 물리 셀은 NOT_COMMISSIONED다.


## 2026-09-11 · 솔루션 프로세스 관리·기동/종료 기록

- S에 rx-supervisor/rx-solutionsd를 추가했다. 별도 전용 SQLite store에서 계획 digest·instance·기동 경계·종료 관측을 기록한다. 계획은 선택한 release program 정의·파일 digest·효과 분류와 자사 profile에 결합한다. 다른 용도의 store를 새 supervisor 저장소로 사용하지 않는다.
- 기동 의도를 PREPARED/SPAWN_ENTERED로 먼저 commit하고 OS 실행 직전 authority를 확인한다. 저장 후 응답 유실과 실제 spawn 뒤 저장 실패를 구별한다. 같은 owner의 실제 Child handle이 있을 때만 기록을 보완하고, 새 supervisor는 이전 PID를 채택하거나 불명 기동을 반복하지 않는다.
- dependency의 process probe 확인 후 후속 프로그램을 시작하고 종료 시 의존 프로세스를 먼저 정리한다. stop을 메모리에도 latch해 저장 오류 뒤 새 기동을 막는다. 제어 효과 프로그램은 종료 authority가 없으면 유지하며 timeout만으로 강제 kill하지 않는다. 제품 authority 기본값은 제어 효과 시작/종료를 허용하지 않는다.
- 일반 서비스의 재시작 횟수·backoff를 제한하고, 명시적 software 재활성화는 전체가 확인된 terminal 상태일 때만 허용한다. EXITED의 저장 응답을 잃어도 종료 관측을 재저장하며, 확정 뒤 handle/timer를 회수한다. UNKNOWN은 이 재활성화 경로로 지우지 않는다.
- 이미지의 관리 경로는 release-owned rx/status-http recipe 하나다. 임의 실행 파일·script/argv·환경·효과 분류를 사이트 계획으로 받지 않는다. instance ID를 포함한 실제 child HTTP 응답으로 process readiness를 확인한다. profile OM-05 참조와 process readiness는 driver 준비나 qualification이 아니다.
- S54개·clippy가 통과했다. 새11개 시험은 commit 장애·불명 spawn·재시작·stop 권한·강제 kill 거부·stop latch·종료 재저장·순서·restart budget·현재 파일 무결성과 실제 무동작 child의 instance readiness/종료를 포함한다. P/운영 앱과 shared SDK는 변경하지 않아 기존 동작 검증을 유지했다.
- 최종 S 이미지의 기존 진단 모드와 새 관리 모드를 비루트/read-only/무장치로 검증했다. 정상 종료·새 instance의 명시적 재활성화, disposable 무동작 컨테이너 강제 종료 뒤 UNKNOWN 보존/재활성화 거부, script 변조 거부를 확인했다. 초기 검증 도구의 readonly SQLite sidecar 문제는 test volume의 writable sidecar와 read-only/query-only SQL 연결로 해결했다. Linux에서도 새 supervisor11개가 통과했다. 최종 결과는 검증 기록에 남긴다.

[프로세스 관리와 한계](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/runtime/rx-supervisor/README.md), [예제 계획](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/examples/deployment/solutions-startup.json), [검증 기록](../../references/implementation/phase40_checks.json).

실제 ROS/controller/BT의 release recipe, device/network 권한, 기존 P/Host lifecycle permit 검증, native 종료·지지 이관, 재시작 후 process adoption/부재 증명과 전체 설치/업데이트 supervisor는 남아 있다. P 화면과 S 관리 명령·상태도 아직 연결하지 않았다. 제어 프로세스의 모의 authority 시험을 실제 startup/stop 안전성이나 현장 인수로 취급하지 않는다. 첫 물리 셀은 NOT_COMMISSIONED다.


## 2026-09-11 · 공정 초안 저장·편집·이력과 공통 구조 검사

- P에 Engineer용 process draft 저장·조회·이력을 추가했다. 미완성 canonical JSON도 오류와 함께 저장하고 최신 version/index/내용별 document/이력/감사/요청 결과를 원자적으로 보존한다. 현재 역할/셀 범위를 cache보다 먼저 검사하며 같은 key/body는 원래 version, 다른 body나 stale CAS는 충돌이다.
- 구조 validator를 shared process contract에 두고 S compiler가 같은 규칙을 사용하도록 정리했다. source tree·연결/순환/재귀·유한 반복/대기·조건/전개 한계를 확인한다. 필요한 binding과 procedure reference는 연결 의무이며 실제 binding/자원 충돌·package/실물 승인은 별도다. validator source/model digest를 저장 결과에 묶는다.
- API의 CPU 작업은 writer 진입 전 immutable PreparedSave를 만들며, commit에서는 최신 접근권과 revision을 확인한다. 목록은 작은 index와 50개 page를 사용하고, 과거 version의 원문과 검사 결과도 읽을 수 있다. Cell/Run/configuration·native outbox를 바꾸지 않는다.
- UI에 공정 설계·flow/node 편집·구조 오류 위치·작업 연결 이름·source export·초안 복사·현재/과거 version 비교를 연결했다. preview는 순환/공유 경로에서도 256개 한도를 넘겨 확장하지 않는다. 조건 및 개입 artifact의 상세 입력은 현재 고급 JSON 경로다.
- 편집 buffer와 적용 전 JSON 입력은 계정/설치/저장 세대·셀별 메모리에 유지한다. 메뉴 이동이 내용을 지우지 않고, 적용 전에는 다른 편집·저장을 막는다. 저장 응답 유실은 기존 pending key/body로 회수하며, 충돌과 비교는 로컬 편집을 보존한다.
- P192개·S54개·양쪽 clippy, UI11개/build/format, 통신 E2E6개와 실제 API 브라우저 편집 검증이 통과했다. 브라우저에서 6개 version의 생성/수정·동시 변경·새로고침 후 회수·과거 비교·복사, JSON/조건 적용과 미변경 Cell을 확인했다. SDK80개로 수출했고 규범8개·optional4개는 유지했다. 두 이미지와 S 관리 모드, Linux P193개도 통과했다. 브라우저의 실제 source export와 저장 원문이 같음을 확인하고, 모의 binding을 붙여 최종 S 이미지에서 COMPILED_NOT_QUALIFIED 산출물을 생성했다. package/실행 승인을 뜻하지 않는다.

[공정 초안·버전의 책임](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/PROCESS_DRAFTS.md), [편집 화면](../../references/implementation/phase41-browser-export/authoring-editor.png), [검증 기록](../../references/implementation/phase41_checks.json).

시각적 capability/binding 선택·완전한 조건/복구 편집, compiler preview·package 생성/서명/활성화의 UI 연결, 검토 승인·변경 영향, 큰 목록의 DB page index·보존 정책은 남아 있다. 구조 통과와 source export는 실행 허가가 아니며 첫 물리 셀은 NOT_COMMISSIONED다.


## 2026-09-12 · 현재 등록 작업의 바인딩 선택·고정된 컴파일 입력

- 공정 source의 binding 이름을 현재 셀의 등록된 step에 연결하는 API/UI를 추가했다. 후보 digest는 cell definition/envelope/site config와 전체 step 정의를 포함한다. 저장 시 현재 source revision·binding CAS·catalog digest와 실제 등록 step을 대조한다.
- 바인딩은 별도 version/history로 보존하며 원문 digest, 원본 step digest, 정규화한 Host+intent와 미연결 이름을 기록한다. 같은 요청의 회수는 원래 version이다. 현재 Engineer 역할을 먼저 검사하고, 바뀐 body/원문/구성·잘못된 step은 조용히 적용하지 않는다.
- 공정 내용이나 catalog가 바뀌면 기존 선택을 보존하면서 stale 이유를 표시한다. 제목만 바뀌어 내용 digest가 같으면 불필요하게 무효화하지 않는다. 부분 선택은 저장할 수 있지만 current complete 상태가 아니면 컴파일 입력을 내보내지 않는다.
- source와 bindings를 같은 읽기 cut에서 `rx.process-compile-input.v1`로 묶는다. 정확한 두 revision과 내용/catalog를 확인하며 S compiler의 `--bundle` 경로는 digest를 재검사하고 기존 semantic/resource 검사를 사용한다. 결과에는 작성 provenance를 남기되 COMPILED_NOT_QUALIFIED를 유지한다.
- UI는 등록 작업 선택, 메뉴 이동 중 선택 보존, 응답 유실/새로고침 회수, 원문 변경 후 내보내기 거부와 명시적 재검토를 연결했다. 늦은 다른 draft의 조회 응답은 대상/generation 확인으로 무시한다. 모바일 버튼 배치를 확인·수정했다.
- P199개·Linux200개·S54개·양쪽 clippy, UI11개/build/format, 통신 E2E6개와 브라우저 시험이 통과했다. 두 이미지와 S 관리 모드도 통과했다. 브라우저에서 실제 선택·내보낸 묶음을 최종 S 이미지에서 컴파일하고 내용 변조 거부를 확인했다. 등록 step은 모의 개발 fixture이며 실행/활성화/서명/실물 검증은 하지 않았다. SDK81개로 수출하고 규범8개·optional4개는 유지했다.

[바인딩의 책임과 현재성](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/DRAFT_BINDINGS.md), [화면](../../references/implementation/phase42-browser-final/binding-detail.png), [검증 기록](../../references/implementation/phase42_checks.json).

현재 경로는 등록된 셀 작업을 재사용하는 작성 도구다. 새 장비 capability/profile/교정에서 binding을 생성하는 도구, 전체 StepBinding을 포함한 package 조립·서명·배포/활성화, compiler preview UI와 현장 인수는 남아 있다. 첫 물리 셀은 NOT_COMMISSIONED다.


## 2026-09-12 · 공정 패키지 후보·외부 서명·검증된 바이트 재컴파일

- S에 rx-process-package 도구를 추가했다. 원문·바인딩·작성 input·recipe·context 연결 의무를 결정적인 Process package 후보로 조립한다. 실제 사용하는 operation/observation 권한을 도출하고 필수 ArtifactRef 선언, 현재 compiler의 의미·자원 검사를 통과해야 한다. executable/native endpoint 권한을 Process package에 넣지 않는다.
- signing request는 key ID와 canonical manifest에 묶인 실제 message/digest를 내보낸다. 외부 detached signature는 별도 로컬 policy의 publisher/kind/permission·contract/target과 파일·dependency/asset 검증을 통과해야 한다. 개인키 생성/보관이나 P trust 자동 등록은 하지 않는다.
- 서명 검증 뒤에도 원래 조립과 manifest/files가 일치하는지 재검사하고 immutable bytes에서 재컴파일한다. 유효한 서명으로 서로 다른 원문/바인딩을 감추지 못하게 했다. 파생 결과의 package_digest는 실제 manifest digest이며 순환하는 자기 hash를 원본 패키지에 넣지 않는다.
- 공통 package 라이브러리에 검증 전 owned-byte 취득과 명시적인 manifest 구조 검사를 노출했다. 서명/내용 검증을 우회해 VerifiedPackage를 만들지 않는다. 신규 출력은 임시 디렉터리에서 완성한 뒤 Linux/macOS no-replace rename으로 공개한다.
- P199개·S62개·양쪽 clippy와 통신 E2E6개가 통과했다. 작성했던 실제 공정으로 최종 S 이미지에서 조립→외부 서명 요청→test-only signature 봉인→현재 trust 검증→재컴파일을 확인했고, 요청 bytes 일치와 권한을 회수한 policy의 거부도 확인했다. 결과는 CONTENT_VERIFIED_NOT_QUALIFIED이며 native 실행은 없다. 두 이미지·S 관리 모드, Linux의 process-package8개와 공통 package8개도 통과했다. 최종 결과는 검증 기록에 둔다.
- UI는 변경하지 않아 이전 브라우저 검증을 유지했다. 규범8개·optional4개·SDK81개도 유지한다. 테스트용 고정 키는 시험 코드에만 있고 산출물에는 signature/공개 policy/예상 signing message만 포함한다.

[패키지 조립·서명·검증의 경계](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/runtime/rx-process-package/README.md), [검증 기록](../../references/implementation/phase43_checks.json).

production signing service/HSM·trust 공급/회수, 실제 device/site/context 해석과 전체 StepBinding package 조립, P artifact admission·검토 승인/활성화, 운영 UI의 서명·배포와 현장 인수는 남아 있다. 첫 물리 셀은 NOT_COMMISSIONED다.


## 2026-09-12 · 패키지 보관·현재 정책 재검증·오프라인 가져오기

- 공통 rx-package에 VerifiedPackage의 원래 signature와 소유 bytes 읽기, 독점 object store, 로컬 policy loader를 추가했다. S의 trust 도구가 같은 loader를 재수출하여 두 구현의 신뢰·dependency·asset 판정이 갈라지지 않게 했다.
- object ID는 manifest digest와 signature-envelope digest다. 같은 내용의 재서명과 같은 서명의 재시도를 구별한다. 원본 경로를 다시 사용하지 않고 검증된 bytes를 쓰며, 내용/서명/파일·하위 디렉터리를 sync한 뒤 no-replace rename으로 공개한다. 기존 동일 object는 전 bytes 비교 후 회수하고 손상은 자동 덮어쓰기 없이 거부한다.
- 보관 root handle과 독점 lock을 보유하고 root/파일/반입 경로 symlink를 거부한다. 원래 경로가 다른 디렉터리로 바뀌어도 보유한 handle에서 작업한다. 미초기화된 다른 저장소나 중단된 staging을 완료 object로 채택하지 않는다. 잠금은 협력 프로세스 경계이며 동일 OS 계정의 악의적 변조까지 막는다고 주장하지 않는다.
- P 이미지에 rx-package-store를 포함했다. 관리자 설정의 반입 root·store root·정확한 policy 파일 digest를 사용한다. import는 현재 policy/원본 검증 후 보관하고 저장된 내용을 다시 검증한다. verify는 매 호출 현재 policy·dependency/asset을 새로 읽는다. 결과는 CONTENT_VERIFIED_NOT_ADMITTED이며 공정 의미 검증·현장 계정 승인·활성화를 만들지 않는다.
- 새8개 시험은 원본 삭제 후 재취득·재실행·반복 ID, 현재 key/target/dependency 회수, 손상 보존, 같은 내용의 재서명/잘못된 object 이름, 독점/표식/중단 staging, 깊은 경로/취득 한도, symlink와 root 교체, 정확한 policy byte pin/중복 입력을 포함한다.
- Linux 최초 시험에서 cap-std의 O_PATH 디렉터리 handle을 직접 sync할 수 없어 새 store7개 시험이 실패했다. 같은 handle 아래에서 읽기용 디렉터리 FD를 다시 열어 fsync하도록 수정했다. 수정 후 macOS P207개·S62개와 양쪽 clippy, Linux 패키지16개·platformd3개가 통과했다. 실패 로그와 수정 후 결과를 함께 남겼다.
- 두 runtime draft 이미지를 재빌드하고 비루트/read-only 기동·종료 및 S 관리 모드를 확인했다. P 이미지의 격리된 보관소에서 정책 pin/회수/경로 이탈의 초기 거부, 같은 ID 재요청, 원본 변조 후 저장 bytes 조회, 저장 손상 거부/자동 수리 금지를 확인했다. 실제 phase43 공정 패키지를 새 S 이미지에서 재검증·재컴파일한 두 결과 파일은 이전 bytes와 일치했다. 패키지 시험은 네트워크·실장비 접근을 막은 컨테이너에서 수행했다.
- 규범8개·optional binding4개와 SDK83개를 확인했다. UI35개 및 application/API/runtime/Host/executor 해당 소스는 이전 단계와 같아 기존 브라우저·통신 E2E 증거를 유지하며 이번 단계의 재실행으로 세지 않는다. source archive와 이미지별 결과는 검증 기록에 둔다.

[보관·재검증과 다음 접수/승인 경계](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-package/STORE.md), [검증 기록](../../references/implementation/phase44_checks.json).

사용자/단말·셀별 package admission과 writer의 현재 trust revision 재검사, 독립 검토·승인·활성화/변경 영향, asset bytes 보관·용량/GC·중단 staging 정리·백업 복원, production trust 공급/회수와 Windows publication은 미완료다. 실제 전원 차단·고장 디스크의 내구성은 시험하지 않았다. 첫 물리 셀은 NOT_COMMISSIONED다.


## 2026-09-12 · 사용자·셀별 패키지 반입·영속 접수

- P application에 반입 context/preflight/commit/조회·목록을 추가했다. 현재 Engineer와 사용자/단말의 셀 교집합을 검사하고, 내부 ticket에 입력·request key·실제 Identity·Runtime boot·등록 세대·전체 CellConfiguration digest와 30초 유효기간을 묶는다. ticket을 API로 직렬화하거나 PASS Boolean으로 대신하지 않는다.
- Runtime의 단일 취득 worker가 writer 밖에서 현재 고정 policy 파일·dependency/asset·원본을 검증하고, 요청의 manifest/signature 두 hash를 대조해 전용 Store에 보관한다. Store가 실제 소유 bytes를 다시 읽은 StoredPackage만 Prepared로 받는다. 서로 다른 Store owner나 검증 policy의 결과는 거부한다.
- commit 직전 역할·단말·구성·정책 등록·boot·시간을 재검사한다. 접수증/이벤트/request 결과를 한 transaction으로 기록하며 상태는 AWAITING_REVIEW다. source bytes는 DB transaction보다 먼저 완성하고, DB 실패 시 미참조 object가 남을 수 있음을 명시했다. Cell/Run/qualification/permit/outbox는 바꾸지 않는다.
- 동일 key/body의 접수증은 현재 권한 확인 후 회수한다. 이는 과거 결과 조회이며 새 내용 검증·승인이 아니다. GET은 검토 문맥의 현재 일치 여부, 내용 재검증 필요, activation_authorized=false를 별도로 표시한다. 재시작은 접수 이력을 유지하고 이전 boot의 live 등록과 대기 ticket을 채택하지 않는다.
- browser BFF의 context/submit/detail/list와 실제 terminal HTTPS에 연결했다. 선택 startup package_intake는 고정 import root·policy pin을 사용하고 Store는 data directory의 packages를 독점 소유한다. 실제 daemon은 신규 취득마다 policy 파일 pin을 다시 확인한다. trust hot-update 관리·독립 검토 승인·활성화와 구성/검토 UI는 후속이다.
- 새 application7개·HTTP1개·실제 HTTPS 기동/재시작1개는 DB rollback/commit 후 응답 유실, 단말/역할 회수, 정책 비활성화·교체, 만료, 다른 Store/policy proof, stale 구성, 동시 ID 충돌, 현재 권한 우선 및 이력 복구를 검증한다. 이미지에서는 실제 phase43 서명 패키지를 등록한 test 단말로 접수하고 같은 요청의 동일 응답·Run/qualification 미생성을 확인했다.
- 추가 경계 검사에서 JSON 정규화의 큰 u64 반올림 때문에 다른 정책 한도가 같은 fingerprint가 되는 반례를 재현했다. 한도를 Counter 문자열로 정규화하여 수정하고 새 regression1개를 추가했다. 최종 macOS P217개·S62개·양쪽 clippy, Linux 반입9개와 공통 패키지17개가 통과했다.
- 통신 E2E6개와 worker27시나리오도 통과했다. 이 E2E는 마지막 정책 fingerprint 정수 표현 수정 전에 실행했으며 해당 경로는 이 새 함수를 사용하지 않는다. 최종 새 함수/접수 경로는 이후 전체/선택 시험과 새 이미지에서 다시 검사했다. UI35개는 변경하지 않아 이전 브라우저 증거를 유지하고 재실행으로 세지 않는다.
- 최종 두 이미지를 비루트/read-only로 다시 검증했다. P 온라인 접수·기존 오프라인 보관·SIGTERM, S 일반/관리 모드·공정 패키지 내용 검증도 통과했다. 규범8개·optional binding4개와 SDK83개를 보존했다. 실패 재현과 수정 결과, 최종 소스·이미지·로그를 검증 기록에 둔다.

[반입 API·원장·worker와 승인 연결 조건](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/PACKAGE_INTAKE.md), [검증 기록](../../references/implementation/phase45_checks.json).

독립 의미 검증/검토 revision·Verifier 승인·변경 영향/활성화, 반입·검토 UI, production trust 관리와 자동 폐기, 수명/용량/GC 및 물리 commissioning은 남아 있다. 현재 ticket 검사는 DB writer의 정책 snapshot에 대한 것이며 filesystem을 지속 감시하는 장비 보호 기능이 아니다. 첫 물리 셀은 NOT_COMMISSIONED다.


## 2026-09-12 · 공정 검증 자료·독립 대조·소프트웨어 검토 승인

- 검토 request/report JSON 계약을 shared process contract에 추가했다. S의 review/validator-identity/review-signing-request 도구가 실제 signed package의 compile_verified 결과와 정확한 서명 대상 bytes를 출력한다. 성공 자료와 실패 issue를 구별하고 개인키·production 서명 서비스는 포함하지 않는다.
- P에 검토 요청·당시 CellConfiguration snapshot, signed report/P 검사 결과의 불변 버전·자료, 승인/반려·이력·현재 조회를 추가했다. verifier authority는 package publisher trust와 별도의 공개키/허용 validator 정책이며 pinned startup 옵션으로 구성한다. report domain/key/request/package/정책과 resolved hash/size를 검사한다.
- P의 독립 source_link 검사는 새 compiled tree를 만들지 않고 제공된 tree를 원문과 대조한다. 유효 node ID를 유지한 순서 바꾸기·분기 뒤집기·반복 횟수/호출 instantiation 변조도 거부한다. 현재 셀의 정확한 StepBinding·host/intent·FactSpec/schema/unit·모든 분기의 predecessor 순서를 함께 확인한다.
- report digest, signature, P checker digest/결과, source/resolved artifact와 revision을 review_digest에 결합했다. 승인 대상은 이 digest와 정확한 검토/결정 revision이다. 다른 검토 버전의 자료로 바뀌면 이전 결정은 새 버전에 적용되지 않는다. 조회에서도 report/request/artifact 내부 동일성을 확인한다.
- 승인자는 현재 Verifier 역할과 해당 셀 범위를 가져야 하며 반입 제출 계정과 달라야 한다. 승인 직전에 worker가 현재 패키지·정책·authority·서명·자료를 다시 읽고, writer가 boot/시간/현재 문맥·CAS를 재검사한다. 접수·검토·결정 이벤트와 요청 결과는 각각 원자적으로 저장한다. 승인 scope는 PROCESS_PACKAGE_SOFTWARE이며 activation_authorized=false다.
- 현재 intervention node는 P 절차 policy 검증과 아직 연결하지 않아 승인 준비로 통과시키지 않는다. Device/UI, 검토 화면·목록/이력 탐색, production 검증 서명자/HSM과 activation/change plan은 후속이다. 서명은 허용된 생산자의 주장이지 하드웨어 원격 실행 증명이 아니며, 검증기 identity의 source/lock 범위를 문서에 명시했다.
- application의 원자성/응답 유실·별도 계정·서명/자료/문맥 변경·버전 경합·authority/역할 회수, artifact 경로 한도/링크, 단말 mTLS 기동의 신규 시험이 통과했다. P224개 전체·S66개·양쪽 clippy와 Linux P225개 전체를 확인했다. 이어서 구현 변경 없이 재시작 후 검토 결정 보존/이전 대기 ticket 거부 시험1개를 추가해 macOS/Linux와 해당 clippy에서 검증했다.
- 실제 별도 S 실행 파일이 생성한 자료를 P HTTP로 제출하고, Store 손상 시 승인 거부·복원 후 별도 검토자 승인·같은 key 회수를 macOS/Linux 각각 확인했다. 이 시험은 test-only 외부 서명자를 사용한다. 별도 terminal HTTPS composition 시험은 기동 옵션/인증/worker/승인 연결을 검사하며 S 컴파일러 자체는 앞 통합 시험의 범위다.
- 기존 통신 E2E6개와 worker27시나리오, 두 이미지의 비루트/read-only 기동/종료·S 관리 모드 및 P 반입/보관 회귀도 통과했다. 최종 S 이미지에서 검증 자료와 signing request를 생성하고 resolved bytes가 기존 phase43 결과와 같음을 확인했다. 그 이미지 출력 시험은 미등록 요청에 대한 unsigned 자료 생성이며 P 승인 시험으로 세지 않는다.
- 규범8개·optional4개는 그대로이며 SDK는85개다. UI35개는 변경하지 않아 기존 브라우저 증거를 유지한다. 실패한 개발 검사와 수정, 소스·각 시험/이미지의 정확한 범위를 검증 기록에 둔다.

[검토·승인 계약과 한계](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/PROCESS_REVIEW.md), [검증 기록](../../references/implementation/phase46_checks.json).

소프트웨어 검토 승인이 현장 commissioning이나 장비 동작의 안전성을 증명하지 않는다. first physical cell은 NOT_COMMISSIONED다. 전체 구현 목표는 아직 진행 중이다.


## 2026-09-12 · 반입·검토·소프트웨어 승인 화면

- 운영 앱의 기존 화면 구성에 패키지 검토를 추가했다. Engineer의 서버 폴더 반입, 셀 작업 선택, 검토 요청 생성/내보내기, signed report 등록, 원문 흐름/전체 결과·근거 조회와 Verifier의 승인·반려를 실제 API에 연결했다. 파일 업로드/서명 실행을 구현한 것처럼 표시하지 않는다.
- P에 반입별 검토 목록/cursor, 과거 검증 revision 조회, 현재 최신 revision/is_latest 표시와 반입 context의 review authority 상태를 추가했다. 과거 조회는 읽기 전용이며 서버의 승인 최신성/CAS 기준을 변경하지 않았다. 목록은 기존 document scan을 사용하며 대규모 인덱스 최적화는 후속이다.
- 표시 자료 snapshot에 확인 표시를 묶고, 구성/정책/검토 자료가 바뀌면 확인 표시와 열린 승인 창을 해제한다. 마지막 조회 시작 후10초 경과/조회 실패에는 새 조작을 막는다. 승인 창은 제목·검증 revision·전체 review digest를 표시하며 클릭 직전에도 현재 대상을 확인한다.
- 새 mutation들은 기존 전역 sessionStorage pending 기록을 사용한다. 전송 전에 번호/내용/계정/설치를 보관하고 원래 대상·revision·digest·choice·의견과 일치하는 응답만 회수한다. 처리 중과 결과 미확인 문구를 구별하며, 다른 설치/계정의 pending을 회수하지 않는다. 과거 승인 기록과 현재 검토에 맞는 승인도 구별한다.
- 로컬 개발 서비스에 명시적 private package-service.json을 구성할 수 있게 했다. 브라우저 시험은 새로 만든 SQLite/계정/서명 패키지와 public test authority만 사용한다. 실제 S 컴파일러가 출력한 자료를 test-only 서명자가 서명하며 UI에서 등록·승인한다. production 키나 실장비에는 접근하지 않았다.
- UI14개 시험·typecheck/build/format, P226개 전체·clippy와 Linux 검토7개가 통과했다. S Rust/runtime/native/SDK/dependency 소스는 이전 단계와 같아 기존 Rust66개 등의 근거를 유지하고 이번 재실행으로 세지 않는다. 규범8개·optional4개·SDK85개도 유지한다.
- 새 실제 브라우저 시험은 반입/선택/export/report, 제출 계정 승인 거부, 새 검토 버전의 확인 표시 및 열린 창 해제, 과거 읽기, 대상 확인, 승인 응답 유실 뒤 reload/같은 key 회수와 모바일 overflow/JavaScript 오류를 확인했다. 기존 운영·조건·서비스 진단·사건·공정 편집/바인딩 브라우저도 다시 실행했다.
- 선택 필드의 접근성 이름을 명시했고, 초기 시험의 pending 표시/실제 commit 관측 경합은 처리 완료를 기다리도록 바로잡았다. TypeScript 단위 시험 fixture는 실제 사용하는 표시 guard 입력만 의존하도록 정리했다. 실패 기록과 최종 통과 기록을 함께 둔다.
- desktop/modal/mobile 화면을 직접 확인했다. 두 이미지를 새 코드/UI로 빌드하고 P 기동/반입/종료, S 일반/관리 모드를 비루트/read-only로 검증했다. 최종 소스·화면·각 검사의 범위는 검증 기록에 둔다.

[화면·API·복구 규칙](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/apps/operator/PACKAGE_REVIEW_UI.md), [승인 대상 화면](../../references/implementation/phase47-browser-final/approval-target.png), [검증 기록](../../references/implementation/phase47_checks.json).

파일 전송/검증 도구/서명의 자동 실행, 실패한 원문 preview 확대·decision 이력 비교, production 배포/계정 관리와 activation/change plan은 남아 있다. 소프트웨어 승인 화면에서 실장비 운전을 시작하지 않으며 첫 물리 셀은 NOT_COMMISSIONED다.


## 2026-09-12 · 승인 공정 변경 계획·영향 검토·staging·준비

- 승인한 검토 revision/review digest/decision revision을 변경 제안에 고정하고, 실제 Store/policy/signed report를 worker에서 다시 검증한다. target 구성은 검증된 compiled node와 기존 StepBinding으로 생성하며 host/intent/조건/completion/condition revision/handover 규칙을 보존한다. node ID에 따른 확장과 원래 template 연결을 기록한다.
- before/after는 내용 hash 기반 불변 구성 문서이고 plan digest는 검토 참조·target·원래 step·영향 범위·이유·builder identity를 묶는다. 클라이언트가 임의 after를 제출하지 않는다. stage까지 현재 CellConfiguration/Run/permit를 바꾸지 않는다.
- 셀 전체에서 공유 scope/resource/Host를 따라 영향 closure를 구한다. 모든 영향 셀에 권한이 있어야 한다. 별도 Verifier 계정의 영향 검토와 ReleaseManager의 fresh 검증 후 STAGED를 기록하며, 오래된 구성/승인/계획/revision을 거부한다.
- 실제 적용 준비는 현재 등록 단말의 ReleaseManager 명령으로 분리했다. 영향 셀의 epoch/scope epoch와 latched CONFIGURATION_CHANGE block, 옛 authority 봉인·work/자원 보존, Host fence 메시지와 Preparation/history를 같은 transaction으로 기록한다. 겹치는 변경의 준비를 직렬화하고, 같은 key의 응답 유실에는 기존 epoch/fence를 회수한다.
- 열린 사건·미처분 Run·NONE/UNRESOLVED/disputed work·보유/격리 자원·fence 미확인·구성 ack 필요를 조회한다. fence receipt는 해당 준비 메시지와 현재 Host boot/journal에 결합한다. fence 성공을 구성 ack나 적용 완료로 사용하지 않는다. 명시적 refresh는 이전 준비 이력/보류/작업을 보존한다.
- 신규8개 application 시험은 조건 복사/설치 불변, rollback/응답 유실, UNKNOWN/자원 보존, 공유 Host closure/권한, fence와 구성 ack 구별, 승인 회수 중 stage, 단말/겹침 거부, stale 준비의 명시적 refresh를 다룬다. P234개 전체·clippy, UI14개/build/format과 Linux 신규8개가 통과했다.
- 실제 S 컴파일러→P HTTP 검토 통합을 변경 제안/영향 검토/STAGED까지 확장했다. terminal 없는 prepare는 거부했다. 별도의 실제 단말 mTLS composition 시험은 현재 단말 ReleaseManager의 준비와 남아 있는 구성 ack blocker를 확인했다. 기존 통신 E2E6개/worker27시나리오도 재실행해 통과했다.
- 두 이미지를 재빌드하고 비루트/read-only 기동/종료·P 반입·S 일반/관리 모드를 확인했다. S Rust/native/SDK/dependency 소스는 이전과 같아 해당 이전 동작 검증을 유지한다. UI는 새 block reason/표시명만 바꾸었고 이전 브라우저 근거를 보존한다. 규범8개·optional4개·SDK85개는 유지한다.

[변경 계획과 준비 계약](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/PROCESS_CHANGE.md), [검증 기록](../../references/implementation/phase48_checks.json).

APPLIED_UNQUALIFIED/QUALIFIED_ACTIVE, Host 구성 handshake·부분 적용/불명/취소 조정, old Run의 old configuration 참조와 실제 선택 교체, 새 qualification 및 변경 전용 UI는 아직 연결하지 않았다. 현재 응답의 applied/activation_authorized는 false이고 기존 설치 구성은 유지한다. 이는 전체 구현 목표의 완료가 아니다. 첫 물리 셀은 NOT_COMMISSIONED다.


## 2026-09-12 · Host 공정 문맥·영속 receipt·mTLS 확인

- 선택 rx.host.configuration.v1와 transport 비의존 request/receipt/observation을 추가했다. base Session/CellCall·strict codec을 재사용하며 정확한 binding hash와 bounded JSON artifact hash/size를 대조한다. 기존 규범8개/optional4개를 변경하지 않았고 새 binding1개, semantic mappings630개, SDK89개를 확인했다.
- Host의 현재 Binding fingerprint와 전체 관리 셀 cohort, definition/envelope/environment, 필요한 intent/condition, 현재 blocked fence/epoch/scope를 확인한다. 부분 cohort나 binding 밖 변경은 수용하지 않는다. Host 전체의 남은 delivery work와 실제 adapter quiescence 관측을 확인하며 기본 미지원/오래된 근거를 성공으로 만들지 않는다.
- 공정 문맥/context와 change/preparation slot, 원래 request/digest, receipt/sequence/history를 한 transaction으로 기록한다. 결과는 APPLIED_UNQUALIFIED 또는 NOT_APPLIED이고, 같은 key/body는 원래 receipt를 회수한다. 같은 slot의 다른 ID도 거부한다. 이 효과는 Host의 공정 문맥 record이며 PLC/robot/driver 설정 적용이 아니다.
- 문맥이 기록된 뒤 Arm과 native 진입을 막는다. 기존 Arm 재전송, 새 grant 또는 Host 재시작으로 이를 해제하지 않는다. 과거 receipt와 현재 Host boot/binding/context/epoch를 구별하고 activation_authorized=false를 유지한다. recorded_at은 transaction 직전 검사 시각이며 지속 물리 안정성 보장이 아니다.
- P HostClient에 Inspect/Apply/Lookup과 응답 schema/hash/Host/request/current-metadata 검증을 추가했다. RPC 오류를 NOT_APPLIED로 바꾸지 않는다. P 업무 원장이 전송 전 request를 고정하고 Host별 결과를 현재 preparation에 연결하는 coordinator는 후속이다. 통합 fixture도 정확한 request를 전송 전에 보관한다.
- Host 신규7개 시험은 재전송/slot/caller, restart/Arm 거부, 전체 cohort/부분 거부, 준비 work, 미지원/오래된 quiescence 및 commit rollback을 다룬다. 추가 process-kill 시험은 commit 뒤 reply 전 SIGKILL에서도 문맥/receipt가 남고 Arm은 복원되지 않음을 확인했다. Linux에서 이8개도 통과했다.
- 실제 P client↔별도 S simulation server mTLS 시험은 commit 후 정상 응답 유실을 주입하고 Lookup/같은 request 재전송, 변경된 body 거부, 재시작 후 역사 receipt를 macOS/Linux 각각 검증했다. native effects는0개다. 응답 유실 설정과 kill hook은 테스트 전용이며 외부 제품 요청으로 선택하지 않는다.
- P234개·S74개 전체와 양쪽 clippy가 통과했다. 강화한 Arm/slot assertions 뒤 Host8개와 해당 clippy를 추가 확인했다. 기존 통신 E2E6개와 worker27시나리오도 통과했다. 전체 Linux workspace/UI browser는 재실행하지 않고 이번 Linux Host/새 mTLS 경로 범위를 구별한다.
- 두 이미지를 재빌드해 비루트/read-only P 기동·반입/종료와 S 일반/관리 모드를 확인했다. UI는 변경하지 않아 이전 브라우저 증거를 보존한다. 생성기의 CellCall type namespace 오류는 정확한 rx.cell.v1 이름으로 수정했고, 실패 로그와 최종 검증을 함께 남겼다.

[Host 문맥 계약과 한계](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/runtime/rx-host/PROCESS_CONFIGURATION.md), [검증 기록](../../references/implementation/phase49_checks.json).

P 변경 coordinator·Host별 receipt/current preparation 결합, 여러 Host의 혼합/불명 조정, 실제 P configuration 선택 교체, qualification 활성화·취소/복원과 범용 native reconfiguration은 남아 있다. Host receipt 하나를 P 전체 적용 완료로 사용하지 않는다. 첫 물리 셀은 NOT_COMMISSIONED다.


## 2026-09-12 · P 변경 원장의 Host 전송·영속 결과 조정

- 현재 등록 단말 ReleaseManager의 configure-hosts 명령을 추가했다. STAGED/검토/plan/preparation·영향 셀 권한과 준비 fence·Run/work/resource/case 장벽을 확인하고, Host별 Task/slot과 사용자 요청 결과를 원자적으로 기록한다. 같은 change/preparation/Host에 새 Task ID를 만들지 않는다.
- 인증된 전체 Host snapshot을 현재 준비와 대조하여 정확한 request/body digest를 보관한다. 전송 진입을 먼저 commit하고 writer 밖에서 RPC를 호출한다. 전송 후 오류는 결과 미확인으로 남으며 원래 ID Lookup을 먼저 수행한다. 이 멱등 metadata 확장에 한해 같은 세대·예상 문맥의 빈 조회와 현재 송신 권한을 다시 확인한 경우 같은 request를 재전송한다. native 명령의 재실행 규칙은 바꾸지 않았다.
- 첫 receipt는 후속 통신 오류에도 보존한다. 사라지거나 모순되는 receipt는 원래 사실을 덮어쓰지 않고 무결성 분쟁을 latch한다. 송신자 권한/준비가 변한 뒤에도 현재 해당 Host의 늦은 사실은 기록할 수 있다. 현재 적용 가능성은 별도로 판단한다.
- 변경 조회에 Host별 task/preparation/전송 상태/결과/문제와 현재 준비 확인, 일부 Host만 확인/결과 미확인 집계를 추가했다. refresh 후 이전 요청이 조회에서 사라지지 않도록 마지막 이력을 표시하고, 이전 미확정/분쟁 전송으로 새 준비를 우회하지 못하게 했다. 모든 Host 확인에도 P 구성 교체/운전 허가는 false다.
- ConnectionService가 기존 HostClient/Identity를 configuration worker에 연결한다. 최대16개 목록·cursor와500ms 주기를 사용하며 네트워크는 writer 밖이다. 소유 서비스 중단은 대기 중 worker도 종료하지만 이미 admit된 transaction/RPC의 취소 성공을 주장하지 않는다. 저장 장애를 권한 거부로 숨기지 않는다.
- 신규 원장8개와 worker2개를 포함한 macOS P244개 전체 시험 및 clippy가 통과했다. 원장 시험은 commit 전 실패/commit 후 응답 유실, fence/단말 조건, 같은 요청 재시도, 권한 회수·늦은 receipt, 일부 Host 확인, snapshot 변경, receipt 소실/모순, 새 준비의 이전 unknown 우회 거부를 다룬다.
- 별도 S 모의 Host와 실제 P writer/검토/준비/Task를 사용하는 mTLS 시험을 추가했다. Host commit 후 정상 응답 유실·새 worker의 같은 ID 회수, P 재시작 후 사실 보존/이전 준비의 새 송신 거부를 확인했다. 기존 raw-client/Host 재시작 시험과 함께2개가 통과했다. test-only signer를 사용하며 native effects는0개다.
- Linux에서도 원장8개·worker2개·위 통신2개가 통과했다. 기존 통신 E2E6개와 영속 worker27시나리오도 다시 통과했다. S 소스/SDK/UI는 phase49 inventory와 같아 이전 S74개·clippy·UI 브라우저 근거를 보존하고 이번 재실행으로 세지 않는다.
- 규범8개·optional5개·SDK89개는 변하지 않았다. 첫 통합 fixture의 fence receipt type/비동기 writer 생성 오류는 기존 API에 맞춰 수정했고 실패 로그와 이후 통과 결과를 함께 둔다. 최종 플랫폼 이미지 검증, 소스 및 증거 hash는 phase50 기록을 따른다.

[P 전송·결과·복구 계약](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/HOST_CONFIGURATION_DISPATCH.md), [검증 기록](../../references/implementation/phase50_checks.json).

실제 P active configuration 교체·old Run/history binding, 적용 직전 fresh barrier·새 qualification, 취소/복원·변경 전용 UI 및 일반 native reconfiguration은 남아 있다. 동일 definition digest가 중복된 multi-cell Host cohort는 현재 거부하며, 복수 ConnectionService의 같은 Host 세션 소유권 조정은 검증하지 않았다. `all_hosts_acknowledged`는 저장된 응답의 준비 문맥 판정으로 지속 물리 안정성/온라인 상태를 뜻하지 않는다. 첫 물리 셀은 NOT_COMMISSIONED다. 전체 구현 목표는 진행 중이다.


## 2026-09-12 · 실제 P 구성 선택 교체·과거 Run 구성 보존

- 공정 변경에 APPLIED_UNQUALIFIED와 ApplicationRecord를 추가했다. 현재 등록 단말 ReleaseManager의 apply API가 STAGED/검토/plan/준비와 전체 영향 셀 권한을 확인하고, 기존 package worker가 실제 Store/정책/서명/검토 자료를 다시 검증한다. commit 직전 모든 현재 조건을 재검사한다.
- Host receipt의 과거 저장만으로 적용하지 않도록 현재-process read proof를 분리했다. worker가 RPC 전에 얻은 P 시각과 응답 digest를 writer가 확인하고 Engine 메모리에만 둔다. 조회 시작부터3초 한도를 prepare/commit 모두에서 확인한다. 재시작으로 freshness를 복원하지 않으며 동일 응답의 반복 조회 때문에 영속 Task 사건을 계속 추가하지 않는다.
- 한 transaction에 Run 구성 참조 보완, 셀 구성 교체·선택 이력, 이전 qualification 보관/제거, SETUP/재검증 상태, 새 cell/scope epoch·변경 block·fence, Change revision/history/event와 같은 key 결과를 기록한다. 이웃 셀은 recipe를 유지하되 영향 경계·자격 재검토에 포함한다. 실제 장비 설정이나 운전 authority를 생성하지 않는다.
- 새 Run은 생성 시 정확한 CellConfiguration artifact와 불변 binding을 함께 저장한다. 첫 구성 교체 전의 옛 Run은 초기 구성과 recipe/envelope가 일치할 때만 binding을 보완한다. 교체 이력이 있는데 binding이 없으면 추정하지 않고 거부한다. 기존 binding을 새 셀 구성으로 덮어쓰지 않는다.
- execution_snapshot/executor_artifact/production_view는 Run의 원래 recipe/process를 읽고 현재 접근권·epoch/admission을 별도로 확인한다. 새 시작/실행 admission에는 구성 전체 일치를 요구한다. 실제 결과와 자원 인계까지 완료한 분기 공정을 fixture로 만들어, 변경 뒤에도 옛 원문·Run/생산 이력이 유지되고 새 Run이 새 구성을 참조함을 검증했다.
- 신규 적용4개를 포함한 macOS P248개 전체·workspace clippy가 통과했다. 이후 테스트만2개 추가하여 초기 DB binding/교체 후 누락 거부와 새 ReleaseManager 세션에서도 만료 Host read 거부를 확인했다. 마지막 application 선택 시험17개와 clippy도 통과했다. 구현 소스는 이 추가 시험 중 바꾸지 않았다.
- 별도 S 모의 Host와 실제 P writer의 mTLS 시험을 P 적용까지 확장했다. Host commit 응답 유실→새 worker 회수→패키지 검증과 P 적용→같은 apply key 회수→P 재시작 후 선택/적용 근거 보존을 확인했다. raw-client/Host 재시작과 함께2개가 통과하며 native effects는0개다. 서명자는 test-only다.
- 기존 통신 E2E6개와 영속 worker27시나리오도 통과했다. 과거 공정 조회의 첫 새 시험은 legacy executor 세션을 사용하여 NotFound로 실패했고, 실제 negotiated executor peer fixture를 사용해 통과했다. 실패 기록과 수정된 검증을 함께 둔다.
- Linux P 전체251개와 별도 mTLS2개도 통과했다. 최종 이미지, source archive 및 정확한 시험 범위는 phase51 검증 기록을 따른다. S298개·UI41개·SDK89개 소스는 phase50과 같아 이전 S/UI 검증을 보존한다. 공통 규범과 wire schema를 변경하지 않았다.

[구성 적용·역사·freshness 계약](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/PROCESS_APPLY.md), [검증 기록](../../references/implementation/phase51_checks.json).

QUALIFIED_ACTIVE와 적용 후 새 epoch fence/Host 문맥 재검증·해제, 변경 취소/rollback·복원, 변경 전용 UI는 남아 있다. 현재의 적용은 P 공정 구성 선택이며 물리 장비 설정 적용이 아니다. APPLIED_UNQUALIFIED의 block을 해제하지 않는다. definition/envelope 교체, production qualification authority 및 첫 물리 commissioning도 미완료다. 첫 셀은 NOT_COMMISSIONED이며 전체 구현 목표는 진행 중이다.


## 2026-09-12 · 재검증 정책·서명 근거·독립 검토

- 적용된 configuration/definition/envelope·환경별 pinned 정책과 필수6영역의 criteria/specification·acceptance plan·limitations·의존 자료를 정의했다. 의존 hash에는 현재 recipe/site, 단계별 profile/calibration 및 trajectory/tool/program/parameter/mode/stream 자료를 포함한다. 원본 bytes 없는 placeholder hash는 보고서를 검증하지 못한다.
- 등록 단말 ReleaseManager의 Begin은 change/전체 cell revision map·현재 policy·적용 구성을 확인하고, 새 epoch/scope/block/fence와 Job/요청 결과를 한 transaction에 기록한다. 재시작한 applied 구성이 같으면 현재 revision으로 새 요청을 만들 수 있으며 옛 요청의 현재성을 복원하지 않는다.
- Report는 원래 요청·validator와 모든 cell/criterion의 PASS/FAIL/NOT_RUN·설명·근거를 담는다. 서명 domain/key/validator/environment/요청/정책/범위를 검사하고, 누락·추가·중복 항목을 거부한다. FAIL/NOT_RUN도 보관하지만 모든 항목이 PASS일 때만 승인 준비로 표시한다.
- worker는 고정 import root의 qualification.json/qualification.sig.json 및 artifacts/<hash>.bin을 capability 기반으로 읽는다. 정책 pin은 매 작업에 다시 검사한다. 개별8 MiB/고유 합계32 MiB·metadata1 MiB와 동시 작업1개를 제한한다. writer 밖에서 crypto/파일 검증 후 private proof를 전달한다.
- 원본은256 KiB chunk와 전체 manifest로 저장해 DB 문서1 MiB 한도를 지키면서 report/history/event/같은 key 결과와 한 transaction으로 commit한다. 조회 시 조각·전체 hash/size를 재검사하며 충돌하는 기존 원본을 덮어쓰지 않는다.2 MiB 원본의 rollback과 정확한 회수를 시험했다.
- 독립 Verifier의 승인에는 최신 version/digest·decision CAS, 현재 전체 문맥과 정확한 Host fence ack, 저장 원본/정책 재검증이 필요하다. 요청자·반입자와 동일 계정의 승인을 거부한다. 검토 중 Hold/정책·역할·문맥 변경은 승인을 막고, 새 보고서 version은 이전 승인과 분리된다.
- Report/decision의 승인 scope는 REQUALIFICATION_EVIDENCE_REVIEW이고 activation_authorized=false다. Qualification·QUALIFIED_ACTIVE나 Host unqualified 문맥 해제를 생성하지 않는다. 실행 파일의 activation authority는 NOT_CONNECTED를 유지한다.
- 신규7개 원장 시험을 포함한 macOS P257개 전체·clippy와 Linux P258개 전체가 통과했다. 별도 S 모의 Host/P writer 통합은 파일 손상·정책 변경 거부, 재검증 근거 승인 후 Arm 거부, 재시작 후 승인 현재성 상실을 확인했다. raw-client/Host 재시작과 함께2개가 통과했다.
- 이후 테스트 경로를 실제 loopback HTTP 서버로 확장하여 report 반입/decision/원본·상태 조회를 통과했고 unbound Begin은 거부했다. Begin 양성 경로는 실제 writer의 등록 단말 identity로 검증했다. 마지막 HTTP 통합/host-client clippy/이미지 결과는 phase52 기록에 둔다. browser UI와 새 Begin의 전용 HTTPS 양성 시나리오는 후속이다.
- test fixture의 Arm 호출 인자와 새 optional startup 필드의 기존 테스트 초기화를 수정했다. 원본 저장은 기존 DB 문서 상한을 확인한 뒤 chunk 방식으로 바꾸었다. 실패한 개발 검사와 최종 통과 결과를 함께 기록한다. S298개·SDK89개·UI41개 소스 및 규범8개/optional5개는 유지한다.

[재검증 요청·증거·검토 명세](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/REQUALIFICATION_REVIEW.md), [검증 기록](../../references/implementation/phase52_checks.json).

다음은 승인 digest를 qualification ID/revision·현재 구성/세대에 묶고 Host의 durable 자격 수용/차단 해제 receipt를 모아 QUALIFIED_ACTIVE로 연결하는 단계다. 물리 시험·실제 자료의 전문 판단, production trust 공급/회수·activation authority, 변경 취소/복원, 검토 UI/정책 준비 도구 및 반입 부하/보관 용량 검증은 남아 있다. 현재 fixture 서명자·근거는 simulation protocol 시험용이며 제품 기본 trust나 현장 근거가 아니다. 첫 셀은 NOT_COMMISSIONED이고 전체 구현 목표는 진행 중이다.


## 2026-09-12 · Host 자격 수용·영속 receipt·현재 gate

- 선택 rx.host.qualification.v1와 transport 비의존 request/receipt/current observation을 추가했다. 기존 base/cell session과 exact binding hash·strict payload hash/size/schema를 사용하며 모든 cohort 셀의 협상을 요구한다. 규범8개와 이전 optional5개를 유지하고 새 optional1개를 더했다. SDK93개와 semantic mappings641개를 확인한다.
- Host가 전체 관리 셀의 현재 process context/request/sequence/change·static Binding/환경·현재 blocked epoch/scope와 정확한 fence를 대조한다. 허용 intent/purpose를 static 범위의 부분집합으로 제한하고, 빈 intent 집합은 어떤 operation도 허용하지 않는다. 남은 Host work나 미지원/오래된 quiescence는 수용하지 않는다.
- 전체 accepted bindings, 요청/slot/sequence/history와 자격 ID/revision의 불변 의미/최대 revision을 원자 기록한다. 같은 ID/body는 원래 receipt를 회수한다. 같은 review/version의 다른 ID, 같은 자격 revision의 다른 근거/범위, revision 후퇴와 같은 epoch의 교체를 거부한다. NOT_ACCEPTED는 기존 수용을 덮어쓰지 않는다.
- 수용은 block을 지우거나 Arm/grant/permit/native 동작을 생성하지 않는다. 기존 process-context가 있으면 startup의 옛 자격으로 fallback하지 않으며, 별도 Arm과 현재 새 qualification·narrowed intent/purpose·grant/fence/permit·현지 guard가 필요하다. Host 재시작/Binding/공정 문맥/epoch 변화는 옛 수용을 부적합하게 한다.
- 수용 시 device session도 보관하고 최종 Native guard의 session과 대조한다. Host 프로세스가 유지돼도 장치 session 변경 후 새 동작을 거부한다. 조회의 current flag는 Host/구성 metadata 일치이며 물리 안정성이나 전역 운전 허가를 뜻하지 않는다.
- macOS P257개·S83개 전체와 양쪽 clippy가 통과했다. 이후 device-session guard를 강화하여 최종 Host34개와 S 전체 clippy를 추가 검증했다. 신규 Host8개/commit 후 SIGKILL1개는 수용과 실행 분리, old ID/purpose/빈 scope, key/slot/epoch/자격 의미, cohort 원자성, pending work, quiescence/session 변경과 restart를 다룬다.
- 실제 P 검토 승인 view에서 테스트 harness가 만든 qualification Request를 먼저 파일에 보관하고 별도 S Host로 전송했다. Host commit 후 응답 유실·원래 receipt Lookup/재전송·본문 충돌 거부를 mTLS로 확인했다. 통합에서는 native effects0이며 P production 자격 발급/영속 coordinator/전역 activation을 구현한 것으로 세지 않는다.
- 공유 Observation predicate의 첫 괄호 오류와 Host fence tuple의 타입 추론 오류는 수정했다. simulator의 test-only loss flag와 기존 클라이언트 wrapper에 새 service를 연결했다. 실패 로그와 최종 결과는 phase53 기록에 남긴다.
- Linux Host/통신, 기존 전달·복원 E2E, 두 새 이미지와 SDK/규범·소스 보관 결과는 phase53 검증 기록을 따른다. UI41개는 바꾸지 않아 이전 browser 증거를 보존한다. 실제 native driver/PLC/hardware 검증은 수행하지 않았다.

[Host 자격 수용·최종 gate](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/runtime/rx-host/QUALIFICATION_ACCEPTANCE.md), [검증 기록](../../references/implementation/phase53_checks.json).

다음은 P에서 승인 근거를 재검사하고 qualification ID/revision과 영속 Host task를 발급한 뒤, 부분/불명·오래된 receipt를 조정해 전체 QUALIFIED_ACTIVE를 commit하는 단계다. block 해제 범위·별도 사용자 시작·현재 조건, production authority/trust 갱신, 취소/철회·복원과 실제 현장 검증도 남아 있다. 첫 물리 셀은 NOT_COMMISSIONED이며 전체 구현 목표는 진행 중이다.


## 2026-09-12 · P 자격 발급·Host 조정·전역 활성화·별도 작업 완료

- v2 재검증 정책에 명시적인 purpose 집합을 추가했다. v1은 빈 purpose를 직렬화하지 않아 기존 기록을 읽을 수 있지만 운전 목적을 추론해 발급하지 않는다. 신규 발급과 활성화는 재검증 근거/서명/현재 v2 policy뿐 아니라 원래 공정 package object를 현재 Store/package policy로 다시 검증한 private proof를 요구한다.
- 현재 단말 ReleaseManager의 Issue에서 전체 cell revision·현재 승인·quiet/fence 장벽과 해제할 block의 소유를 검사한다. Batch/새 qualification ID·Host task/slot/history/같은 key 결과를 원자적으로 기록한다. Pending sender 세션 만료 시 새 key의 명시적 재검증으로 sender만 갱신하며 원래 ID/Request는 유지한다.
- configuration 준비/apply/requalification 및 해당 자격의 suspension/runtime restart에서 block 출처를 기록한다. 현재 reason과 change/cell/ID가 모두 일치하는 block만 해제 대상으로 받는다. manual Hold/타 사건/출처 없는 과거 block은 보존한다. 자격 활성화와 남은 운전 제한을 구별한다.
- Host worker는 P가 만든 Task만 수행하고 원래 P 적용의 context request/sequence와 전체 Host snapshot을 대조해 Request를 보관한다. SEND_ENTERED commit 후 전송하며 응답 유실은 같은 ID 조회로 회수한다. receipt 소실/모순은 원래 사실을 보존하고 분쟁을 latch한다. 부분 Host 결과나 불명으로 전역 활성화를 만들지 않는다.
- 명시적 Activate는 최신 승인/원본/현재 역할·문맥을 재검증하고 모든 Host의3초 이내 memory read proof/수용을 확인한다. 모든 셀의 Qualification/COMMISSIONED/승인된 P block 제거, certificate/history·Batch ACTIVE·Change QUALIFIED_ACTIVE를 한 transaction으로 기록한다. 여기서 Run/Arm/permit/native 명령은 만들지 않는다.
- 기존 StartRun의 Arm에 승인된 clear plan을 연결했다. client가 실제 Host의 남은 block이 전부 승인된 집합 안에 있는지 확인하고 전달하며, Host는 부분 clearance로 Arm 성공을 반환하지 않는다. Host도 receipt의 전체 cohort를 최종 gate에서 다시 대조한다. 어느 한 구성원이 바뀌면 같은 Host의 다른 구성원도 옛 자격으로 진행하지 않는다.
- 자격/목적/원본 정책·등록·Host 문맥을 admission에서 확인한다. 명시적 Suspend, trust 등록 변경, Runtime 재시작과 확인된 Host 수용 상실은 자격을 history로 보존하고 제한/새 epoch/fence와 SUSPENDED/APPLIED_UNQUALIFIED를 기록한다. cached 활성화 응답은 역사 결과이고 현재 authority를 복원하지 않는다.
- 확인된 현재 fence에만 HostRegistration epoch/scope를 동기화했다. 원래 LinkPlan을 다시 만든 것으로 처리하지 않고 동일 Host/source/기존 grant/fence/자원 범위의 갱신만 허용한다. 만료 lease·새 자원·새 Host 세대를 자동 채택하지 않는다. 이것은 운전 허가나 Arm이 아니다.
- 발급/활성화 원자성·응답 유실/같은 ID, 부분 Host, manual Hold 보존, 정책 회수, receipt 소실, Runtime 재시작, legacy purpose 거부, 현재 세션 재승인과 목적 제한을 시험했다. 처음 전체 P268개/S84개와 양쪽 clippy가 통과했고, sender 재승인·목적 시험을 더한 최종 P270개/전체 clippy와 단말 HTTPS 통합도 통과했다. Linux는 Host35개/P269개 전체/통신2개 후 마지막 발급12개/통신2개를 추가 확인했다. 정확한 범위는 phase54 기록을 따른다.
- 실제 P writer/worker와 별도 S 모의 Host, 등록 단말 HTTPS에서 Issue/Activate를 수행했다. Host 수용 commit 응답 유실 뒤 새 worker가 같은 P 원장의 요청을 회수하고, 전역 활성화까지 native effects0을 유지한다. 이어 별도 작업자 StartRun→실제 Arm/prepare/authorize→native 성공 근거/인계 관측→자원 해제→Run 완료와 독립 file-device effects1개를 확인했다. P 재시작 뒤 자격/승인의 현재성이 복원되지 않음도 검사했다.
- native completion의 fixture는 실제 유한 program 작업으로 수정했다. activation 뒤 Run revision 재조회와 성공 후 별도 인계 절차를 추가했으며 기존 거부/자원 유지 규칙은 완화하지 않았다. 큰 모듈은 issuance/host_tasks/activation과 공유 검사로 나눴다. 초기 fixture/protocol 호출 오류·검증 로그는 보관한다.
- 규범8개/optional6개/SDK93개를 유지한다. UI41개는 변경하지 않았다. Linux 전체/마지막 발급·HTTPS, 기존 E2E6개/worker27시나리오, 두 이미지와 source archive의 정확한 범위는 phase54 기록에 둔다.

[P 자격 발급·전역 활성화 명세](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/QUALIFICATION_ACTIVATION.md), [검증 기록](../../references/implementation/phase54_checks.json).

전용 정책/검토/자격 UI, 장기간·최대 부하/용량, 만료·불명 작업의 전체 운영 복구, 다중 서비스/업데이트·취소/rollback, production trust 공급/회수와 실제 physical qualification/현장 인수는 남아 있다. 이번의 모의 자료/서명자/동작을 실장비 근거로 승격하지 않는다. 첫 물리 셀은 NOT_COMMISSIONED이며 전체 구현 목표는 진행 중이다.

phase54 배포 확인: 두 image smoke/관리 모드는 PASS다. S build는 변경한 Host library를 컴파일했지만 runtime에는 executor/process 도구/관리 프로세스만 복사한다. Host 통합은 별도 test-harness binary이며 납품용 Host executable·배포 연결을 완료한 것으로 세지 않는다.


## 2026-09-12 · 제품 Host 실행파일·Linux clock·수명주기·이미지

- rx-hostd inspect/init/run과 solutions image의 명시적 host entrypoint를 추가했다. Host mode는 ROS setup script 전에 직접 binary로 진입한다. startup은 pinned Binding/TLS·P fingerprint/설치·backend와 분리된 data/runtime 경로를 검사하며 테스트용 clock/seed/응답 유실 옵션을 받지 않는다.
- init은 장비 어댑터를 열지 않고 새 Host journal/설치 identity를 완성해 공개한다. run은 기존 descriptor·DB metadata/cell generation을 먼저 대조하고 runtime/DB/device owner lock을 확인한다. 유실·교체·잘못된 설치를 새 원장으로 자동 채택하지 않는다. 실제 시간은 Linux boot UUID/CLOCK_BOOTTIME이며 다른 OS run은 미지원이다.
- release-owned AdapterFactory의 open_passive 경계를 두었다. 현재 builtin은 FILE_SIMULATION이고 실제 P 통합을 제품 binary로 검증한다. VALIDATED_DRIVER는 구현이 등록되지 않아 시작 전에 거부한다. 자사 mandatory SDK/ROS/model 포함을 물리 driver 검증으로 바꾸지 않는다.
- stop은 atomic admission latch부터 내린다. gate/DB/native lock을 기다리지 않고 새 grant/renewal/Arm/prepare/authorize/configuration/qualification을 막으며 native 진입 직전에도 검사한다. 진행 중/미확정 delivery 사실을 지우지 않는다.
- 기존 stable handover와 구별되는 shutdown_snapshot/safe_to_drop를 추가했다. 기본 미지원은 종료 불가이고, resource 범위·시각·no pending/명시적 drop 허가를 검사한다. 근거가 없으면 같은 owner/검사 handle을 유지하며 timeout만으로 destructor/kill을 호출하지 않는다. transport/publication 정리 뒤에도 최종 drop 근거를 재확인한다.
- 선택 publisher를 실제 서비스에 연결하고 원래 ack cursor를 보존한다. publisher/RPC 확정 실패와 status 저장 실패는 admission 종료를 시작한다. 발행 확인이 없거나 준비/진입 work가 남으면 STOPPED_WITH_RECONCILIATION_REQUIRED로 구별한다. 강제 종료/정전은 정상 종료 보장이 아니며 독립 현지 보호의 검증이 필요하다.
- 제품 rx-hostd를 S runtime /opt/rx/bin과 runtime inventory에 포함했다. init/run/TLS/volume·비루트/read-only·수동 restart의 배포 템플릿을 추가했다. 기본 status 모드는 유지한다. supervisor의 physical/control lifecycle authority와 여러 실제 driver recipe는 후속이다.
- Mac P270개·S91개 전체와 clippy가 통과했다. Host42개는 stop latch/미확정 보존, gate가 막힌 진입 경계의 즉시 차단, stable handover와 drop 허가 구별, init의 no-adapter-open, owner/정상 stop, raw DB 유실/빈 교체 거부, 미지원 config/driver 및 drop proof 전 owner 보존을 포함한다.
- Linux에서 Host42개와 제품 rx-hostd를 사용하는 P–S 통합2개가 통과했다. 실제 kernel clock/mTLS/등록 단말 HTTPS로 자격 발급·응답 유실 회수·활성화·별도 사용자 시작·native simulation effects1·근거/인계·자원 해제/Run 완료를 수행했다. 제품에는 오류 주입 기능을 넣지 않고 테스트 클라이언트의 응답 전달 경계에서만 유실을 주입했다. 마지막 SIGTERM은 safe-to-drop와 보관 evidence1개를 남긴 정직한 종료 상태를 확인했다.
- S 이미지의 실제 rx-hostd 기동/중복 owner 거부/TLS h2·client certificate/정상 SIGTERM/재시작과 native effects0을 확인했다. 기존 S 진단/관리 모드도 통과했다. 초기 certificate fixture의 동일 subject/issuer 및 AKI 누락은 테스트 인증서를 정상 구성하여 해결했고 TLS 검증을 끄지 않았다.
- 개발 중 디스크가 소진되어 재생성 가능한 네 개 incremental build cache만 삭제해 약73GiB를 확보했다. 소스/원장/증거/이미지·volume을 삭제하지 않았다. 공간 부족으로 VM 기동에 실패한 Docker의 멈춘 backend를 복구했고 데이터 reset은 하지 않았다. 이후 incremental cache를 끈 검증을 사용했다.
- Linux clock의 최초 raw syscall은 unsafe 금지 규칙에 걸려 기존 프로젝트와 같은 safe rustix API로 수정했다. 실패한 개발 검사·환경 복구와 최종 artifact 범위는 phase55 검증 기록에 둔다. 규범8개/optional6개/SDK93개와 UI41개는 유지했다.

[제품 Host 서비스](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/runtime/rx-host/HOST_SERVICE.md), [배포 입력 템플릿](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/examples/deployment/host/README.md), [검증 기록](../../references/implementation/phase55_checks.json).

검증된 physical AdapterFactory/ROS·CNC·로봇 backend와 startup/drop/lifecycle authority, 실제 장치·fieldbus 권한, 다중 Host supervisor, 운영/qualification UI 및 전체 update/restore·장기 부하/보관 정책은 남아 있다. FILE_SIMULATION 검증을 첫 현장의 물리 qualification으로 승격하지 않는다. 첫 물리 셀은 NOT_COMMISSIONED이고 전체 구현 목표는 진행 중이다.


## 2026-09-12 · 첫 레이저 PLC용 제한 MC3E 통신 라이브러리

- S에 `drivers/rx-melsec-mc`를 추가했다. ROS/Platform domain 비의존 Rust library이며 M bit 읽기1–64개, D word 읽기1–32개, 열거된 M request bit 한 개 쓰기를 제공한다. 다른 device write·임의 frame·remote RUN/STOP·프로그램 변경 API는 없다.
- Q03UDVCPU 내장 Ethernet 매뉴얼과 MC Protocol Reference의 3E binary frame/0401·1401/bit packing·word order를 확인하고 고정 frame 시험을 만들었다. 실제 CPU 설정·주소·PLC 프로그램의 command 의미를 사진에서 추정하지 않았다.
- endpoint/route/timer/CPU device 범위·access 목록을 명시한다. Simulation은 loopback만 허용한다. 범위를 벗어난 요청은 송신 전에 거부한다. connect/drop은 PLC 명령을 보내지 않는다.
- 하나의 connection에서 요청을 직렬 실행하며 부분 송수신에도 하나의 전체 deadline을 적용한다. subheader/route/length/end code/payload/bit/padding을 검사한다. 교환 오류 후 연결은 faulted로 남고 자동 reconnect/retry하지 않는다. 송신 경계 이후 쓰기 실패는 결과 미확인으로 보존한다.
- WriteAcknowledgement는 MC 메모리 쓰기 응답일 뿐 물리 완료가 아니다. Raw read도 원본 freshness/세대/안전 조건으로 승격하지 않는다. 별도 NativeAdapter·영속 native journal·완료 관측·Host gate/qualification/종료 연결 계획을 작성했다.
- 새 loopback TCP 시험12개가 macOS/Linux arm64에서 통과했다. 고정 M/D frame과 조각 응답, ACK와 완료 분리, 응답 유실 후 모의 effects1·추가 송신 없음, 접근 거부0 byte, 잘못된 응답10변형, 지연 조각 deadline, passive connect/drop을 다룬다. Linux는 network-none container의 loopback만 사용했다.
- macOS S 전체103개와 workspace clippy가 통과했다. 초기 clippy의 constant chunks 검사 지적은 `as_chunks::<2>()`로 수정했다. Linux12개는 통과했으나 해당 toolchain에 cargo-clippy가 없어 Linux lint는 미수행으로 기록한다. macOS lint 결과를 Linux lint 통과로 세지 않는다.
- 독립 문서 독자 검토로 현재 raw 통신만 구현됐다는 점을 확인했다. UNKNOWN을 새 ID로 우회하지 못하는 복구 경계와 crash 시험의 중복 측정 대상을 보완했다. 두 문서의 로컬 링크도 확인했다.
- 이전627개 inventory 중 이번 코드 변경은 S workspace manifest/lock 두 개뿐이다. 기존 P·Host·executor·UI·SDK 소스는 유지한다. 공통 규범8개와 SDK93개의 일치를 다시 확인했다. 새 라이브러리는 rx-hostd에 연결하지 않았으므로 기존 runtime image를 새 PLC backend 포함 이미지로 표시하지 않는다.

[통신 구현 범위](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/drivers/rx-melsec-mc/README.md), [Host 연결 설계](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/drivers/rx-melsec-mc/HOST_ADAPTER_PLAN.md), [phase56 검증 기록](../../references/implementation/phase56_checks.json).

이 단계는 통신 기초다. NativeAdapter/작업 journal·semantic profile·PLC 세대/관측 일관성·완료와 drop proof·제품 factory·이미지 연결 및 현장 인수는 남아 있다. 자사 OMY/Dynamixel/ROS 필수 지원 의무도 유지한다. 첫 물리 셀은 NOT_COMMISSIONED이며 전체 구현 목표는 진행 중이다.


## 2026-09-12 · MELSEC NativeAdapter·영속 작업·Host 통합

- Host에 제한 EnsureState Predicate 어댑터를 구현했다. target/site/profile/calibration/resource·predicate/settle/완료·취소 규칙을 대조하고, 명시된 M request bit만 한 번 쓴다. 이미 목표 상태가 충족되면 쓰기 없이 상태 관측 capture를 기록하며 invocation의 물리 실행 증거로 바꾸지 않는다.
- PLC의 별도 9-word atomic publication 계약을 정의했다. epoch/sequence/flags와 source age·debounce는 검증된 publication 계층의 전제이며 MC batch read의 기본 보장으로 주장하지 않는다. 첫 sample만으로 readiness를 만들지 않고 sequence 진행을 관측한다. epoch 변경/sequence 후퇴·동일 sequence의 flags 모순/정체·시계/통신 오류는 쓰기를 latch한다. 실제 publication 계약 원본·서명/프로그램 일치는 후속 검증이다.
- 독립 SQLite native journal은 새 디렉토리에만 초기화하며 장치를 열지 않는다. 기존 journal identity/profile·소유권/메타/작업·invocation/pending index·frame hash와 capture source를 확인한다. 누락/빈 DB·다른 profile·잘못된 capture를 정상 원장으로 채택하지 않는다.
- native 진입 전에 operation/invocation/intent digest·device session/PLC epoch·실제 송신 예정 bytes와 SHA-256·원본 관측을 원자 기록한다. 같은 ID의 다른 body는 충돌이며 미해결 slot을 다른 ID로 우회하지 못한다. 기록 후 readiness/세대/latch를 다시 읽는다. read budget 안에 들어온 응답이라도 guard lifetime이 지났으면 쓰지 않는다.
- ACK는 메모리 쓰기 사실만 저장한다. Host SEND_ENTERED를 유지하며 Lookup이 같은 session의 후속 completion·queue-empty·새 publication을 확인해야 capture/pending 해제를 기록한다. 답변 유실·재시작 뒤 미완료 작업을 재송신하지 않는다. 저장된 capture는 원래 session으로 회수하고 복구 전 미해결 자원은 계속 차단한다.
- support와 drop_allowed를 분리했다. 지지 상태만으로 정상 종료하지 않으며 pending/queue와 별도 drop 근거를 확인한다. 보호는 DB/gate와 독립된 admission latch이고 자동 척 해제/reset/물리 정지를 실행하지 않는다. 오류 연결은 현재 reconnect하지 않아 drop 근거를 못 얻으면 owner를 유지한다.
- 실제 Host library의 Arm 전 거부→prepare→authorize→ACK 미확인→read-only reconcile→evidence/인계→stop을 loopback PLC에 연결했다. prepare/권한 거부 시 writes0, 한 작업의 승인 후 writes1, ACK만으로 evidence 없음과 완료 후 evidence1을 대조했다.
- 별도 자식 프로세스를 native entry commit 후, write 후 ACK commit 전, 이미 충족된 capture commit 후, write·completion capture commit 후에 process::exit(86)으로 종료했다. destructor 없이 재시작한 뒤 같은 invocation의 추가 write0·원래 capture 회수/미확정 보존을 검사했다. 전원/fsync 고장이나 물리 exactly-once 시험으로 세지 않는다.
- macOS S 전체116개와 workspace clippy가 통과했다. Linux Host/통신67개를 통과한 뒤 실제 CLOCK_BOOTTIME의 새 관측→쓰기→완료→drop 시나리오를 추가하여 최종 MELSEC14개가 통과했다. child 전용1개는 일반 목록에서 ignored이고 부모 시험이 네 번 명시 실행한다. Linux clippy는 해당 toolchain에 없어 미수행을 유지한다.
- 초기 컴파일의 임시 mutex guard/부분 move 오류를 수정했다. 병렬 시험의 process spawn과 원장 초기화가 겹친 실행에서 소유 lock 충돌을 관측해 테스트만 직렬화했다. 상속된 descriptor의 짧은 fork window 가능성을 고려한 격리이며 제품의 엄격한 소유권 검사를 완화하거나 자동 retry를 넣지 않았다. 실패와 이후 통과 로그를 보존한다.
- 새 workspace driver 디렉토리를 Rust image stage에 복사하도록 수정하고 S image를 다시 빌드했다. 최종 non-root/read-only 제품 Host의 init/run/TLS/client-auth·중복 owner 거부·정상 stop/restart, 기존 진단/관리 모드가 통과했다. 제품 Builtin은 FILE_SIMULATION이며 Melsec factory를 등록한 이미지라고 표시하지 않는다.
- 독립 문서 독자 검토에서 publication 가정·제품 미등록·ACK/완료/재시작 경계를 확인했고 Lookup 표의 전제와 실제 검증 보고서 링크를 보완했다. P/UI/SDK 및 규범8개/optional6개는 유지한다. 마지막 Linux 전용 test와 문서 변경은 runtime 구현 byte를 바꾸지 않았다.

[어댑터 명세](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/runtime/rx-host/MELSEC_ADAPTER.md), [검증 기록](../../references/implementation/phase57_checks.json).

publication 원본/프로그램/장치 일치와 physical qualification, 제품 factory·identity 원자 공개·설정/이미지 선택, P의 실제 장비 outcome/qualification, 진단 reconnect·승인 복구·native 원장 보관/한도 처리는 미완료다. 첫 물리 셀은 NOT_COMMISSIONED다. 자사 필수 지원·전체 R01–R30 구현 목표는 계속 진행한다.


## 2026-09-12 · 장비 참조 패키지 v2·MELSEC 제품 factory

- 기존 DEVICE v1은 executable adapter를 요구한다는 검증 규칙을 확인했다. JSON descriptor를 실행파일로 표시하거나 기존 검사를 완화하지 않고, rx.package.v2 / rx.package-abi.v2의 DEVICE_REFERENCE를 추가했다. 새 형식은 모든 executable payload를 거부하고 기존 signature/key/kind/permission/target/path/inventory 검사를 재사용한다. v1은 기존 의미를 유지한다.
- P의 package model/verifier를 SDK93개에 동기화했다. 새 패키지 시험은 올바른 v2·잘못된 schema/ABI·실행 payload 거부와 v1 executable 요구 보존을 확인했다. 공통 규범8개와 optional6개는 변경하지 않았다.
- 제품 Backend에 MELSEC_PACKAGE를 추가했다. 절대 package directory·manifest digest·독립 policy pin을 받고, 정확한 family/단일 profile/release-owned descriptor와 permission을 검사한다. source identity는 Host/MC source, manifest/lock, build script와 SDK lock으로 고정한다. descriptor를 실행하거나 임의 binary/library path를 로드하지 않는다.
- 현재 CPU의 Linux/ROS 불필요 target 및 base/cell/ABI를 재검사하고, publication contract/program evidence의 실제 원본 bytes/size/digest를 확보한다. 이것은 원본의 출처·내용 검사이며 실제 PLC 프로그램 일치나 원자 관측/센서 freshness를 증명하지 않는다. 초기화 대상 설치·셀·환경/condition·모든 allowed Intent도 맞아야 한다.
- init은 비공개 stage에서 Host/native journal과 manifest/profile/native identity를 함께 만들고 fsync·no-replace rename으로 공개한다. 생성 도중 생긴 빈 목적 디렉토리도 덮어쓰지 않는다. passive open은 TCP도 열지 않으며, 기존 native identity나 DB가 없으면 새 원장으로 자동 교체하지 않는다.
- 물리 binding은 startup의 qualification ID/revision으로 fallback하지 않는다. 현재 boot/journal/binding/process context의 qualification acceptance 뒤 별도 Arm/grant/fence/permit/native guard가 필요하다. loopback PLC에 PHYSICAL metadata를 사용한 시험에서 자격 전 거부와 현재 수용 후 별도 시작·writes1·완료를 확인했다. 실제 현장 qualification 요청이 아니다.
- 잘못된 signature/content/policy/key 회수/asset/contract와, 유효하게 다시 서명된 잘못된 source/controller 및 설치 불일치를 초기화 전에 거부했다. 시작 설정용 실제 lock 파일명이 host.writer.lock임을 확인해 검사 경로를 수정했고 symlink 거부 시험을 추가했다.
- macOS P 전체271개·S 전체124개 및 양쪽 workspace clippy가 통과했다. Linux Host/MC76개도 통과했다. 공통 시험 fixture를 공유 파일로 옮겼고 기존 native crash 네 경계/실제 Linux clock·Host gate/서비스 시험을 유지했다.
- 두 runtime image를 다시 빌드했다. 실제 rx-hostd에 서명된 모의 MELSEC package를 넣어 network-none/non-root/read-only 환경에서 init/run·native identity·mTLS h2·중복 owner 거부·SIGTERM drop proof를 확인했다. 별도 Python PLC는 시험이 직접 기동한 loopback 보조 프로세스이며 package 실행 payload가 아니다. native writes0, status reads2회 이상을 확인했다.
- 기존 FILE_SIMULATION 제품 Host init/TLS/stop/restart와 S 진단/관리, P 제품 image smoke도 통과했다. 초기 loader는 기존 DEVICE executable 요구에 막혔고 이를 형식 v2로 해결했다. factory의 Result import 충돌·fixture unused import와 개발 실패 로그도 보관한다.
- 새 문서의 독립 reader 검토에서 v1/v2, backend availability/qualification, source pin/실제 PLC 프로그램 검증, 기동 시 trust 검증/실행 중 감시를 구분했다. key 회수 시험 표현을 검증 시점으로 한정했다. source/검증·이미지 근거는 phase58 기록에 둔다.

[장비 패키지와 제품 기동](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/runtime/rx-host/DEVICE_PACKAGE_STARTUP.md), [패키지 v2 명세](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-package/DEVICE_REFERENCE.md), [검증 기록](../../references/implementation/phase58_checks.json).

실제 첫 현장 commissioning은 미완료다. 일반 장비 package authoring·제품군 template/현장 binding 재사용 도구, 실제 publication/프로그램/장치 검증·물리 인수, 실행 중 trust 회수 감시, backend 업데이트·native identity migration·복원, 전체 복구와 자사 필수 backend 연결은 남아 있다. source identity는 image/binary 서명이나 ABI 호환 판정을 대신하지 않는다. 첫 물리 셀은 NOT_COMMISSIONED이고 전체 R01–R30 목표는 진행 중이다.


## 2026-09-12 · 장비 Template/Site 작성·서명 도구

- S에 rx-device-package crate/CLI를 추가했다. driver-identity/template-digest/assemble/request/seal/verify/inspect를 제공하며 장치 연결·개인키·자동 trust/배포/qualification 기능은 없다. 현재 target은 MELSEC Q03UDVCPU의 제한 EnsureState다.
- 공통 Template은 논리 resource role·command slot·관측/완료/settle 의미와 publication 계약을 담고, Site는 정확한 template digest·설치/셀/target·실제 자원·M/D 주소·endpoint·program evidence를 연결한다. 누락/추가/alias·범위/bit/time 오류를 거부하고 실제 Host Profile을 생성한다. Template 수정 없이 두 Site를 조립하는 경우를 검증했다.
- Template/predicate/resource/calibration/target의 의미 없는 순서를 정규화해 같은 서명 메시지를 만든다. Template semantic digest와 concrete profile/package digest를 구분한다. CLI template-digest로 Site의 선행 참조를 만들 수 있게 했다.
- authoring/assembly.json에 정규화한 Template/Site 원문을 담아 네 번째 서명 파일로 추가했다. Host가 서명 후에도 이 원문을 재조립하여 family/profile 및 asset metadata와 대조한다. 유효하게 다시 서명했더라도 서로 다른 원문/결과는 거부한다. 기존 3파일 reference 형식은 유지한다.
- 후보는 Recipe/assembly에서 모든 manifest/file bytes를 재생성하여 대조한다. 외부 signing request는 실제 메시지 bytes의 hex/digest와 key ID를 담는다. seal/verify는 현재 독립 policy·실제 asset bytes·signature/permission/target을 검사한다. 출력은 CONTENT_VERIFIED_NOT_QUALIFIED이며 authority를 만들지 않는다.
- 기존 공정 패키지의 no-replace 파일 공개를 SDK rx-package::directory::publish_files로 옮겨 장비/공정 도구가 공유한다. fsync와 기존 출력 보호를 유지했고 단순 상대 출력명도 지원한다. SDK93개를 다시 동기화했으며 규범8개/optional6개는 유지했다.
- 새 authoring 시험7개가 한 Template의 두 현장, 순서 결정성, missing/extra/alias mapping, 후보 변조·key/permission/asset 거부, signed-but-inconsistent 원문과 실제 CLI의 외부 서명/봉인/검사를 다룬다. 초기 fixture의 module import 충돌과 공유 decoder의 불필요한 borrow를 수정하고 실패 로그를 보관했다.
- macOS P 전체271개·S 전체131개와 양쪽 workspace clippy가 통과했다. Linux Host/device-package/process-package81개도 통과했다. 기존 공정 writer·native crash/실제 clock/Host qualification·서비스 경로를 유지했다.
- rx-device-package를 S runtime image에 포함했다. 실제 image의 CLI를 network-none/non-root/read-only root로 실행해 Template 확인→조립→signing request→외부 test harness 서명→봉인→검사를 통과했다. 제품 CLI에는 private key를 넣지 않았다. 서명된 원문 존재와 manifest/profile 일치, activation false를 확인했다.
- 두 image를 다시 빌드하고 기존 제품 Host(FILE_SIMULATION/MELSEC_PACKAGE)·진단·관리·P image smoke도 통과했다. 새 도구의 4파일 원문 검사는 실제 image resolver를 사용한다. 기존 MELSEC Host image 기동 시험은 이전 3파일 fixture로 회귀를 확인한다.
- 오프라인 SIMULATION 예제 Template/Site/Recipe와 TEST ONLY 원본을 추가하고 실제 CLI로 조립했다. 운영 policy/key를 예제에 넣지 않았다. 독립 문서 reader가 digest/재사용/서명·운전 자격 경계를 확인했고, 외부 signer가 hex-decoded 원래 메시지에 서명하며 64-byte Ed25519 결과를 소문자128hex로 반환하는 규칙을 보완했다.

[장비 작성 도구](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/runtime/rx-device-package/README.md), [모의 예제](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/examples/device/melsec-simulation/README.md), [검증 기록](../../references/implementation/phase59_checks.json).

다른 제조사·ROBOTIS 모델/모드의 authoring/backend, 작성 UI와 P의 장비 검토/배포/변경·복구 연결, 실제 publication/프로그램/현장 검증 및 인수는 남아 있다. Template과 Site 분리는 입력 재사용 구조이며 generic middleware의 모든 장비 지원 완료가 아니다. 첫 물리 셀은 NOT_COMMISSIONED이고 전체 R01–R30 목표는 진행 중이다.


## 2026-09-12 · ROBOTIS JTC ROS action bridge

- S에 C++ rx-ros-jtc-bridge를 추가했다. 기본 ROBOTIS catalogue와 원본 SHA를 binary에 포함하고 support/controller/role·joint order를 선택한다. position JTC만 다루며 leader/impedance/policy/gripper 전용 action을 JTC 생산 경로로 오분류하지 않는다. 현 catalog의16개 지원 구성/51개 controller 선언을 모두 startup 선택/관절 목록으로 확인했다. 이는51개 실장비 검증이 아니다.
- 표준 ROS action의 SendGoal/GetResult/CancelGoal service에 직접 연결하여 caller invocation UUID를 유지한다. 명시적 joint order/전체 position/유한 수/증가하는 시간·양수 tolerance와 bounded duration을 검사하고, 직전 ListControllers의 active/type/정확한 claimed-interface 집합을 대조한다. DHI/driver/controller 기동·토크/모드 전환은 하지 않는다.
- private stdin/stdout 요청에 bridge instance·증가 sequence·같은 Linux boottime의 deadline을 요구한다. source catalogue pin, duplicate JSON/잘못된 UUID/초과 입력을 거부한다. ROS global arguments/parameter services를 열지 않고 response/goal cache 크기를 제한한다. middleware network identity나 controller boot generation을 증명하지는 않는다.
- operation/invocation/body를 프로세스 메모리에 먼저 기록하고 같은 요청은 재송신하지 않는다. 미해결 goal로 인한 preemption을 막는다. 응답 유실은 SEND_UNKNOWN/CANCEL_UNKNOWN으로 보존하고 새 send를 latch한다. result 조회의 timeout/UNKNOWN/error_code0을 완료로 바꾸지 않으며 ROS status와 controller code의 모순도 원문대로 보존한다.
- cancel은 known nonzero UUID와 zero timestamp만 보내므로 cancel-all/이전 시각 목표 일괄 취소를 표현하지 않는다. 반복/미확정 cancel은 재송신하지 않는다. cancel 접수와 terminal canceled, 실제 물리 정지/소재 지지를 구별한다. cached ACK/result/cancel은 실제 captured_at_ns를 유지하고 현재 reply 시각을 새로운 관측으로 바꾸지 않는다.
- 실제 rclpy ActionServer·controller service와 C++ client를 같은 격리된 ROS domain에서 시험했다. 최종16사례는 model/claims/shape/time/tolerance, same UUID 단일전송/경합, raw result UNKNOWN/abort/모순, exact cancel, preflight deadline, IPC context·sequence, send/cancel 응답 유실과 후기 결과·latch를 다룬다. 51개선언 선택에서는 goal을 보내지 않았다.
- Debug 빌드와 최종 S runtime image의 실제 executable 모두16사례/51선택을 통과했다. image 시험은 network-none/non-root/read-only이며 실제 robotis driver나 장비는 사용하지 않는다. default process manager가 bridge를 자동 기동하지 않는다.
- 초기 C++ misleading-indentation 경고를 수정하고 임시 도구 컨테이너의 clang-format으로 형식을 정리했다. formatting 도구는 제품 이미지 의존성에 추가하지 않았다. 새 client의 discovery가 끝나기 전에 response-loss 시험을 시작한 실패는 실제 service availability를 확인하도록 fixture를 수정했다. -Wall/-Wextra/-Werror 빌드를 유지했다.
- P/Rust/SDK/UI 및 catalogue 소스는 phase59 hash와 같아 P271/S131·양쪽 clippy 등 이전 검증을 보존하며 재실행으로 세지 않는다. 기존 Host image smoke는 이번 중간 S image에서 통과했고, 최종 image는 bridge 및 진단/관리 smoke를 다시 확인했다. 이전 S image ID가 로컬에서 조회되지 않아 old/new runtime binary byte 비교는 수행하지 못했고, 소스 일치보다 강한 비교를 주장하지 않는다.
- 규범8개·SDK93개를 다시 확인했다. 독립 문서 reader가51개 선언/실장비, action 결과/물리 인계, 메모리 cache/영속 Host 보장을 구분했고 latch 복귀가 현재 없다는 설명을 보완했다. source/최종 image/실제 시험 기록은 phase60을 따른다.

[ROS JTC 연결 명세](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/native/ros-jtc/README.md), [검증 기록](../../references/implementation/phase60_checks.json).

bridge는 아직 rx-hostd의 NativeAdapter/factory 및 영속 native journal/qualification/permit/handover와 연결하지 않았다. 재시작으로 past goal을 재송신하면 안 되며 controller generation/제어권·기구/교정/오차·지지/정상 종료를 입증하는 모델별 경계가 필요하다. gripper·leader·base velocity·Sapiens 경로와 실제 장비 인수도 미완료다. 자사5개 기본 레포/22개 구성 의무와 전체 R01–R30 목표는 계속 유지하며 첫 물리 셀은 NOT_COMMISSIONED다.

## 2026-09-12 · ROBOTIS JTC Rust NativeAdapter·영속 원장·최종 허가·종료

- S의 rx-host 라이브러리에 ROS JTC adapter를 연결했다. catalog/controller/joint 선택과 trajectory 원본 digest·site/calibration/resource를 검사한다. 실제 제어권·controller session·현재 조건·소재 지지·client 종료 허가는 독립 Authority 포트가 제공하며 기본 UnavailableAuthority는 동작을 거부한다. 이번 제공자는 명시적 시험 fixture다.
- C++ 실행파일의 원본을 hash 검증 후 private 디렉토리에 복사해 직접 실행한다. 제한된 환경과 bounded nonblocking IPC로 schema/bridge instance/sequence/boot clock을 확인한다. timeout·부분 응답·크기 초과·잘못된 instance는 통신 fault를 유지하며 자동 재기동/재전송하지 않는다.
- native.sqlite3에 operation/invocation·Intent와 profile/goal digest·controller session·bridge instance를 송신 전에 원자 기록한다. 원장 identity/index/count·capture 원문을 재검증한다. pending 작업이 있으면 새 ID로 우회할 수 없고, 반복 submit은 원래 기록만 회수한다. ACK와 terminal outcome을 구별하며 success/nonzero controller error 모순은 raw reply와 분쟁으로 보존한다.
- 응답 유실·Host/bridge 재시작 이후에는 원래 invocation의 result를 조회한다. 독립 Authority가 같은 controller session을 확인할 때만 새 사실을 연결한다. 이미 보관한 capture는 원래 session·관측 시각으로 반환한다. 결과가 늦게 도착해도 기존 분쟁을 자동 해제하지 않는다.
- Host 최종 guard의 device session과 permit/guard expiry 중 이른 값을 NativeDispatch에 넣었다. JTC와 기존 MELSEC가 native 진입 직전에 이를 다시 검사한다. Physical adapter가 context를 처리하지 않으면 기본 구현이 거부한다. JTC는 실제 bridge 요청 deadline까지 전달한다. 마지막 Rust snapshot과 ROS 수신 사이의 controller 교체까지 차단한 것은 아니며 production endpoint/lifecycle/fencing 구현·검증이 남아 있다.
- Host admission을 닫은 뒤 prepare_shutdown을 호출한다. JTC는 pending 없음·독립 제어권/지지·client-drop 허가가 확인될 때만 EOF를 시작하고 child가 실제 종료되기 전까지 Busy를 유지한다. 미해결·분쟁 entry가 있으면 정상 종료도 차단한다. 예기치 않은 adapter 소멸 시 독립 보호 callback을 호출하지만 그 호출이나 child 종료를 물리 정지 근거로 간주하지 않는다. 자동 native cancel/torque-off/timeout kill은 없다.
- 신규 adapter8개/process3개 시험을 포함한 macOS S 전체142개와 전체 workspace clippy를 통과했다. Linux Host 전체75개도 통과했다. entry/send/capture 직후 자식 프로세스를 종료하고 독립 effect 기록으로 재송신 금지를 확인했다. 원장 유실/변조·영속 분쟁, 세대/권한/허가 만료, executable pin·pipe 장애·child 종료 지연을 검증했다.
- 별도의 Linux 통합1개는 실제 SystemClock/Rust Host→복사된 C++ bridge→rclpy ActionServer 및 controller service를 사용한다. prepare/authorize→original UUID goal 하나→reconcile/evidence→인계/종료를 통과했고 모의 서버 received=1을 보관했다. 이 시험은 실제 ROS 통신 검증이며 실장비 검증이 아니다.
- 최종 S arm64 image를 다시 빌드하고 FILE_SIMULATION Host, MELSEC_PACKAGE Host, 진단, supervisor의4개 image smoke를 통과했다. ROS JTC 라이브러리를 rx-hostd 제품 factory에 등록한 것으로 세지 않는다. 최초 실제 ROS 시도는 private executable의 noexec tmpfs 때문에 실패했으며 명시적 exec mount로 수정했다. pin 검증을 우회하는 fallback은 만들지 않았다. 개발 중 import/검사 실패 로그도 최종 통과 로그와 함께 보관한다.
- P307개·SDK payload93개와 source-lock·UI41개 파일이 phase60 hash와 같다. 규범8개와 optional binding6개도 다시 확인했다. P271개/clippy 및 앞선 C++ bridge16사례/51선택은 기존 증거를 유지하며 이번 재실행으로 세지 않는다. 문서 검토에서 controller 세대 보장의 마지막 경계와 미해결 작업의 정상 종료 차단을 명확히 했다.

[ROBOTIS JTC 어댑터 명세](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/runtime/rx-host/ROBOTIS_JTC_ADAPTER.md), [검증 기록](../../references/implementation/phase61_checks.json).

다음 연결은 장비 패키지 authoring/factory와 P native outcome profile이다. 생산용 Authority·세대별 endpoint/lifecycle·ROS peer 정책, 영속 native cancel·분쟁 복구/책임 인계, 실제 모델 교정·관절/충돌 한계·소재 지지·인수는 남아 있다. 라이브러리 모의 검증을 생산 지원으로 승격하지 않는다. 두 이미지·자사 필수 지원 의무와 전체 R01–R30 목표를 유지하며 첫 물리 셀은 NOT_COMMISSIONED다.

## 2026-09-12 · 결과 대응표·ROBOTIS 결과와 코어 결론 연결

- 공유 rx-process-contract에 제조사 비의존 NativeOutcomeTable을 추가했다. 정확한 schema/code 쌍과 SUCCEEDED/FAILED/CANCELED만 표현한다. 최대16 case·case당64 code·전체128쌍, 중복/모호 선언과 unknown field를 거부한다. fallback이나 실행 가능한 조건문을 넣지 않으며 미일치 결과는 결론을 만들지 않는다.
- P의 CompletionRule에 NATIVE_OUTCOMES를 추가하고 table의 profile_digest/completion_rule을 해당 Intent와 대조한다. 표는 StepBinding·구성 digest/검토와 Work에 포함된다. 기존 단일 schema NATIVE/PREDICATE/UNOBSERVABLE의 형식은 유지한다. 새 내부 JSON variant를 기록한 구성을 옛 바이너리로 읽을 수 있다고 보장하지 않는다.
- T2의 기존 상관/Host 권한·원본·cursor·원자 기록 안에서 표를 해석한다. 성공 후조건이 있으면 현재 근거와 continuity가 필요하다. 실패/취소를 성공으로 바꾸지 않고, 결과 확정만으로 자원을 해제하지 않는다. 후기 상충 결과는 최초 outcome을 유지하면서 DISPUTED/QUARANTINED와 셀 차단으로 기록한다.
- S의 JTC Profile::outcome_table이 profile digest·완료 규칙을 결합해 실제 capture schema의 의미를 제공한다. 성공/code0, canceled/알려진 code, aborted/알려진 code 및 goal rejection을 구별한다. native 거부는 FAILED로 해석하며 송신 전 NOT_EXECUTED tombstone으로 바꾸지 않는다. 지원하지 않은 code와 접수/unknown schema는 결론 없음이다. P 소스에는 ROS schema 상수나 ROS 라이브러리 의존성을 추가하지 않았다.
- P의 신규 application4개/shared table2개 시험은 schema/code 구별, 원본/동일 batch, profile/rule 불일치·중복/한도·불허 결론, 조건 만료/Hold, commit 전 실패·ACK 유실·후기 상충을 다룬다. S의 신규1개는 실제 JTC adapter native capture를 생성해 공유 표로 해석하고 목표 UUID와 단일송신을 확인한다. 기존 reply-loss/reopen 시험에도 표 해석을 연결했다. 이들은 양쪽 경계 시험이며 새 전체 P→ROS 서비스 통합 시험으로 세지 않는다.
- 초기 Hold fixture가 UUID가 아닌 request key를 사용해 실패했고 유효 UUID로 수정했다. 잘못된 표의 설치 거부 시험은 권한이 있는 cell/b를 사용하고 동일 셀의 유효 표 설치가 성공함도 확인하여 다른 거부 원인이 통과처럼 보이지 않게 했다. 최종 P277개·S143개 전체 시험과 양쪽 전체 clippy가 통과했다.
- 두 arm64 이미지를 다시 빌드했다. P의 기동/mTLS 상태 조회/정상 종료, S의 FILE_SIMULATION Host·MELSEC_PACKAGE Host·진단·supervisor 등5개 image smoke가 통과했다. JTC 제품 factory는 아직 등록하지 않았다. C++ bridge7개 파일과 UI41개는 phase61과 같아 이전 검증 범위를 유지한다. 실제 ROS mock 통합은 phase61의 기존 증거이며 이번 재실행으로 세지 않는다.
- 규범8개·optional binding6개를 유지하고 SDK를94개 payload로 동기화했다. 새 SDK 타입은 해석 데이터이며 application authority는 export하지 않는다. 공식 ROS action 설계와 control_msgs5.9.0 원문을 확인해 접수/terminal 결과 및 code 범위를 문서화했다. source/archive와 실제 image ID·로그는 phase62 기록을 따른다.

[결과 해석 구조와 호환성](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/NATIVE_OUTCOMES.md), [검증 기록](../../references/implementation/phase62_checks.json).

다음은 이 표와 JTC Profile을 장비 패키지 작성·검증·제품 Host factory 및 P 구성 반입으로 연결하는 단계다. 현재 생성 함수 반환값을 검토된 구성에 연결해야 하며 자동 설치/승인/운전은 제공하지 않는다. 생산용 Authority·controller 세대 fencing, native cancel/분쟁 복구·책임 인계, 실물 교정/지지·인수와 전체 R01–R30의 나머지 범위를 유지한다. 첫 물리 셀은 NOT_COMMISSIONED다.

## 2026-09-12 · ROBOTIS JTC Template/Site·서명 패키지·Host metadata 등록

- JTC Template은 고정 catalog/support/controller와 자원·조건 역할·작업 slot/joint group/tool role 및 시간 한도를 선언한다. Site는 해당 Template digest와 설치/셀/실제 역할·교정/tool artifact·ROS namespace/manager/domain·goal을 결합한다. 누락/추가 slot·alias·잘못된 joint 순서·허용 실행시간을 넘는 goal을 거부한다. 같은 Template을 다른 현장에 재사용하고 의미 없는 action 순서만 정규화한다.
- 같은 조립에서 family/profile/adapter/authoring assembly/operations/outcomes의6개 payload를 생성한다. 원래 goal bytes로 trajectory 참조를 계산하고 정확한 Intent/결과표를 같은 profile digest에 묶는다. 교정/tool 외부 자료의 type/size/hash와 중복 참조 의미를 검사한다. 자료 내용의 물리 적합성은 별도 검증 대상이다.
- 공통 rx-device-package의 template-digest/assemble/request/seal/inspect를 확장했다. 기존 MELSEC 형식/API는 유지하고 schema로 구별한다. candidate를 다시 읽을 때도 전체 원본을 재조립한다. JTC의 Linux/Jazzy target과 정확한 권한·6파일·asset 목록을 요구하며 패키지에 실행 경로·환경·임의 함수를 넣지 않는다.
- Host의 공통 verifier가 소유한 불변 bytes에서 assembly를 해석해 profile/operations/outcomes/model/release를 다시 대조한다. 유효한 signer가 잘못된 결과표·timeout·model·release에 서명한 경우도 거부한다. JTC 구현 descriptor는 Host/SDK lock·C++ 연결 계층·catalog·자사 source lock 등을 포함한 빌드 소스로 계산한다. binary 서명·실제 controller identity의 증명으로 세지 않는다.
- JTC_PACKAGE backend를 제품 설정에 등록했다. 현재 CPU/계약/정책/manifest와 설치·셀·조건·환경, 패키지에서 생성한 정확한 Intent를 검사한다. inspect는 control_provider=NOT_CONFIGURED를 표시하고 init은 비공개 staging에 Host/native-jtc 원장과 identity/manifest를 만든 뒤 원자 공개한다. 기존 설치는 덮어쓰지 않는다.
- 실행용 production Authority/lifecycle 제공자는 아직 없다. Builtin의 JTC run은 `JTC_CONTROL_PROVIDER_NOT_CONFIGURED`로 실패하고 ROS client·READY를 만들지 않는다. package 서명/init/기동 시도를 실물 제어권으로 바꾸는 fallback은 없다. 이 단계의 factory 지원 범위는 내용 검사·metadata 등록이며 native 실행 제공자 구현 완료가 아니다.
- 신규7개 시험은 재사용/정규화·candidate roundtrip·유효 서명 아래의 불일치·자료/intent 변조·Host 원장 초기화·실행 제공자 부재와 실제 CLI의 외부 서명/검사를 다룬다. 최종 S 전체150개·전체 clippy가 통과했다. 초기 test module의 directory import 충돌·fixture용 uuid 의존 누락과 clippy 지적을 수정했으며 실패 로그를 보관한다.
- S arm64 이미지를 다시 빌드했다. 실제 image CLI로 JTC 조립→외부 호스트 test signer→봉인/검사를 수행하고, 같은 image의 rx-hostd inspect/init/run 거부까지 검증했다. MELSEC 작성 도구·FILE_SIMULATION Host·MELSEC_PACKAGE Host·진단·supervisor까지 총6개 image 시험을 통과했다. 시험은 격리된 파일/모의 자료와 network-none 또는 기존 제한된 Host smoke만 사용하며 실장비는 구동하지 않았다.
- 오프라인 ROBOTIS JTC SIMULATION 예제 Template/Site/Recipe와 TEST ONLY 교정/tool bytes를 추가했다. 운영 key/policy/서명 패키지는 예제에 넣지 않았다. 초기 phase63-jtc-fixture는 중간 빌드의 작성 fixture이며 최종 image의 서명·검사는 동결한 소스에서 새로 생성한 fixture를 사용했다.
- P311개·SDK94개 payload와 source-lock·UI41개는 phase62 hash와 같다. 규범8개·optional6개를 유지한다. P277개/clippy·기존 실제 ROS mock 통합 증거를 보존하며 이번 재실행으로 세지 않는다. source/최종 image/로그는 phase63 기록을 따른다.

[JTC 패키지와 Host 등록](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/runtime/rx-host/JTC_PACKAGE.md), [모의 작성 예제](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/examples/device/robotis-jtc-simulation/README.md), [검증 기록](../../references/implementation/phase63_checks.json).

후속은 생산용 controller Authority/lifecycle/fencing 제공자와 검증된 장비 operations/outcomes를 P의 구성 반입·검토·변경으로 연결하는 작업이다. 서명된 교정 자료의 내용 검증, 실제 소유권/지지·native cancel·복구/인수, 다른 자사 backend와 전체 R01–R30의 미완료 범위를 유지한다. 첫 물리 셀은 NOT_COMMISSIONED다.

## 2026-09-12 · 장비 작업 선언의 P 반입·보관·API·화면

- 공유 Catalog 타입에 설치/셀/환경/target/profile digest, condition ID, 작업별 Intent·optional 결과표와 signed source 문서 참조를 정의했다. 선언128KiB·64작업·32조건으로 제한하고 중복 조건을 역직렬화 단계에서 거부한다. 제조사 구조·ROS 라이브러리는 P에 추가하지 않았다.
- S JTC 작성기는 같은 assembly로 device-catalog.json을 생성한다. 기존6-payload JTC decoder도 유지하며 새7-payload 패키지는 공통 선언을 추가 재계산한다. candidate/게시물은 manifest와 recipe 또는 signature를 포함해9파일이므로 candidate 취득 한도를10파일로 맞췄다. 기존2MiB payload 한도와 exact release/source 검증은 유지한다.
- P는 기존 실제 Store/서명 검증의 불변 bytes에서 공통 선언을 추출한다. DEVICE_REFERENCE entry 경로·각 문서 hash/size/비실행 속성, operations/outcomes 원문과 내부 target/profile/rule 일치를 확인한다. 다른 셀은 Prepared 생성 때, 다른 설치/환경은 authoritative commit에서 거부한다. 제조사 profile의 의미·실제 교정 적합성을 검증했다고 표시하지 않는다.
- 정규화 선언·그 참조·receipt/object ID·event·request-key 결과를 기존 반입 transaction에 함께 기록한다. 현재 역할·셀·registration·구성 digest·ticket 유효기간을 재검사한다. 조회는 보관 선언의 hash/size/상관을 확인하고 현재 Engineer/Verifier 접근권을 요구한다. 원래 package bytes는 Store에 유지하며 정책이 바뀌어도 과거 조회를 현재 검증으로 승격하지 않는다.
- GET package-intake/device-catalog를 Runtime/application 경로에 연결했다. 응답은 review_context_current와 content_reverification_required/manufacturer_validation_required/activation_authorized를 구별한다. 뒤의 세 값은 true/true/false를 유지한다. 새 자료가 없는 과거 receipt/package는 null projection으로 읽는다.
- 패키지 UI가 DEVICE_REFERENCE를 인식하도록 수정했다. 기존 enum은 PROCESS/DEVICE/UI만 받아 새 장비 반입을 표시하지 못했다. 장비 선택 시 작업/조건·자원/시간·결과표·원본 참조와 다운로드를 제공하고 공정 검토 요청 조작은 구분한다. 셀/intake/object/reference 상관과 기존 abort/generation·자료 만료를 확인한다. 장비 검토 승인·구성 적용 기능을 제공한 것으로 세지 않는다.
- 신규 application4개·중복 조건 parser1개를 포함해 P282개, S150개 전체 시험이 통과했다. 원자 commit/ACK 유실, 과거 receipt, 원문/경로/해시·설치/환경/셀 불일치와 실제 ticket 만료·역할 제한을 다룬다. UI17개·typecheck·production build·format 검사가 통과했다. 양쪽 전체 clippy도 통과했으며 마지막 cfg(test) 블록 위치 수정 뒤 P 전체 clippy와 shared crate3개 시험을 다시 확인했다.
- 실제 S JTC CLI→외부 test signer→P Store/API→React 브라우저에서 반입과 응답 유실/동일 요청 회수, 다운로드 자료와 signed catalog 동일성·다른 셀 접근 거부, 구성 digest/셀 상태/Run 불변을 확인했다. stale context 표시는 응답을 주입한 UI 반례로 따로 구분한다. desktop/mobile screenshot을 확인했고 overflow/JavaScript 오류가 없다. 기존 공정 반입/검증/독립 승인·과거 버전·응답 유실 브라우저 회귀도 통과했다.
- 초기 P test의 canonical import/PackagePath 표시 오류를 수정했다. 첫 브라우저 시험은 존재하지 않는 overview.configuration 필드를 검사하다 실패했으며 실제 CellSummary와 전체 구성 digest를 비교하도록 고쳤다. 마지막 테스트 블록 위치 clippy 지적은 source 내 순서만 바꾸어 수정했다. 실패와 최종 증거를 함께 남긴다.
- 두 arm64 이미지를 다시 빌드하고 P 기동, S의 JTC/MELSEC 작성·Host 초기화/기동·진단·supervisor 등7개 image 시험이 통과했다. JTC는 여전히 production provider가 없어 run을 거부한다. native 실제 ROS 통합은 phase61의 기존 범위이며 이번에 실장비나 native 동작을 검증한 것으로 세지 않는다.
- 규범8개·optional6개를 유지하고 SDK95개 payload를 동기화했다. image/source/archive와 browser 원본/해시는 phase64 기록을 따른다. 최종 browser 뒤의 마지막 수정은 cfg(test) 블록 위치이며 production 로직/UI는 바꾸지 않았다. 변경된 SDK source reference는 최종 image와 package 시험에서 새로 생성했다.

[장비 선언 반입·조회 구조](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/DEVICE_CATALOG.md), [검증 기록](../../references/implementation/phase64_checks.json), [장비 선언 화면](../../references/implementation/phase64-device-browser-sealed/device-desktop.png).

후속은 제조사 validator의 근거와 독립 장비 검토 결정을 package object·선언 digest에 결합하고 승인된 작업을 실제 셀 구성 변경으로 연결하는 단계다. 현재 선언 조회를 장비 승인·운전 가능 상태로 표현하지 않는다. production JTC Authority/lifecycle/fencing, 실제 교정·지지/복구·인수와 전체 R01–R30의 나머지 범위는 유지하며 첫 물리 셀은 NOT_COMMISSIONED다.

## 2026-09-12 · 장비 소프트웨어 보고서·별도 신뢰 설정·독립 승인 API

- 공통 device-review Request/Report를 추가했다. package manifest/signature·catalog 참조·설치/셀·현재 구성/반입 정책·검증 authority를 요청에 고정한다. scope는 DEVICE_PACKAGE_SOFTWARE만 표현하며 content signature, device source consistency, catalog/request binding의 세 check를 구별한다. 누락 check/잘못된 scope·초과 issue/보고서를 거부하고 실물 qualification을 표현하는 필드를 넣지 않았다.
- S rx-device-package의 validator-identity/review/review-signing-request를 구현했다. 실제 공통 verifier·장비 decoder/원본 재조립을 수행하고, decoder 실패는 실패 check와 issue를 가진 소프트웨어 보고서로 남긴다. 원래 요청/package/catalog가 다르면 생성 자체를 거부한다. 서명은 외부이며 제품 CLI에 개인키/전송 기능을 넣지 않았다.
- P에 process authority와 별도의 장비 검증 key/허용 validator digest 설정을 추가했다. rx-platformd는 pinned 파일·의미를 기동 전에 검사하고, worker는 report/approve 때 원본 정책과 authority 파일을 다시 읽는다. 기본 설정은 미연결이며 package에서 신뢰 키를 받아 설치하지 않는다. 개발 서비스도 같은 선택 설정을 제공한다.
- 검증 Job, report version/history, 결정/history를 영속화했다. 현재 registration generation/Store owner·구성·authority·boot/30초 ticket·expected revision을 검사하고 원본/서명/참조를 실제 Store 자료로 재검증한다. report/decision·event·동일 request-key 결과를 한 transaction으로 기록한다. 응답 유실은 원래 결과를 회수하며 새 보고서는 옛 승인을 자동 채택하지 않는다.
- APPROVE는 현재 Verifier이고 package 제출자와 다른 계정이어야 한다. 정확한 최신 보고서와 checker digest·모든 소프트웨어 check 통과·원본의 현재 재검증을 요구한다. 검증 이후 정책/보고서가 바뀌어도 commit 전에 다시 거부한다. REJECT는 최신 대상을 명시하면 authority가 철회된 상황에서도 기록 가능하다. 과거 결정 회수는 현재 승인이나 활성화 복원이 아니다.
- HTTP/단말 HTTPS의 공통 router에 검토 생성·보고서 반입·버전/목록 조회·승인/반려 API를 연결했다. 실제 장비 승인 화면과 셀 구성 적용은 아직 연결하지 않았다. 조회의 context/approval match는 등록된 문맥·최신 버전과의 일치이며, 원본 파일을 방금 다시 검사했다는 proof가 아니다. 후속 적용은 별도 재검증을 요구해야 한다.
- 신규 P5개 시험은 signer/validator/request/catalog 충돌, 실패 보고서·승인 거부, 독립 최신 버전 승인·과거 조회, report/decision 원자성·응답 유실과 승인 검증 중 문맥 변경을 다룬다. S 신규2개는 실제 decoder 보고서·scope/coverage·CLI 서명 요청을 검증한다. P 전체287개·S 전체152개와 양쪽 전체 clippy가 통과했다.
- 첫 실제 API 통합에서 원래 P 반입 정책(32파일/4MiB)과 S의 추가 취득 한도(8파일/2MiB)가 서로 다른 policy fingerprint를 만들었다. 원래 반입 정책 fingerprint는 그대로 대조하고 동일 키/권한/target/asset에 더 엄격한 취득 한도를 별도로 적용하도록 수정했다. fingerprint 검사를 제거하거나 파일 한도를 완화하지 않았다. 수정 뒤 S 전체와 실제 통합을 다시 통과했다.
- 실제 JTC CLI→별도 test signer→P Store/API에서 검토 요청·서명 보고서 반입, 제출자 승인 거부·독립 승인/같은 요청 회수, 새 보고서에 의한 옛 승인 부적합·오래된 target 거부·과거 조회·authority 파일 변조 후 재검증 거부를 확인했다. 셀 구성/Run/qualification은 바뀌지 않았다. 이 시험은 loopback 개발 API를 사용하며 production TLS의 장비 승인 전용 시험으로 세지 않는다.
- 기존 장비 선언 브라우저와 공정 검토/독립 승인·응답 유실 회귀도 통과했다. operator production src28개는 phase64와 같으며 새로운 장비 검토 UI를 구현했다고 표시하지 않는다. 두 arm64 이미지를 다시 빌드하고 P 기동·S JTC/MELSEC 작성/Host·진단/관리의7개 image smoke가 통과했다. 새 보고서/승인 전체 경로의 검증은 위 개발 API 통합이며 image의 승인 E2E로 확대 해석하지 않는다.
- 규범8개/optional6개는 유지하고 SDK96개 payload를 동기화했다. 구현 중 patch 위치가 맞지 않아 거부된 시도와 첫 policy fingerprint 불일치를 수정했다. 최종 source/image/hash와 테스트 로그는 phase65 기록을 따른다. production JTC 실행 제공자는 여전히 미연결이다.

[장비 패키지 검증·독립 승인 API](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/DEVICE_REVIEW.md), [검증 기록](../../references/implementation/phase65_checks.json).

후속은 장비 검토 UI, 현재 승인 근거의 재검증과 승인된 작업을 실제 셀 구성 변경/qualification에 연결하는 단계다. read 목록의 최대 부하·보관 용량·전체 배포/복구와 production JTC Authority/lifecycle/fencing·실물 검증 및 R01–R30의 나머지 범위는 계속 미완료다. 첫 물리 셀은 NOT_COMMISSIONED다.

## 2026-09-12 · 장비 검토 화면·현재 버전 확인·응답 회수·목록 요약

- 장비 검토 목록을 전체 Detail/report 복제에서 Summary50개로 바꿨다. 요청자/시각·최신 보고서와 결정 요약·현재성만 목록에 담고 원문/서명/의견은 상세 endpoint에 유지한다. 32개의 긴 issue가 있는 보고서를 보존하면서 목록은4KiB 미만인 단일 요약으로 반환하는 반례를 검증했다. 전체 Job scan/장기간 부하를 해결한 것으로 세지 않는다.
- 기존 장비 선언 아래에 검토 요청·요청 다운로드·서명 보고서 등록·세 검사/issue·자료 다운로드·과거 버전·독립 승인/반려를 연결했다. package 제출자는 자신의 자료를 승인할 수 없고 scope는 소프트웨어 패키지 검토로 표시한다. 실제 교정/로봇 운전·qualification을 생성하지 않는다.
- UI schema에서 Job/Report/Decision과 선택한 cell/intake/review·package object/catalog 참조, scope·ready/current/version의 상관을 확인한다. 현재 registry/config/장비 authority 및 계정 문맥을 stamp에 넣는다. 같은 polling은 확인을 유지하고, 새 보고서·문맥 변화·오류/만료는 체크와 열린 확인창을 해제한다. 늦은 응답은 abort/generation으로 폐기한다.
- 확인창은 보고서 revision/review digest/expected decision revision·choice·note를 고정한다. 최종 버튼에서 같은 stamp와 현재 조작 조건을 다시 검사한다. 화면의 확인은 P의 fresh source/policy/role 재검증을 대체하지 않는다. 문맥이 어긋난 자료와 과거 버전에서는 승인을 활성화하지 않는다.
- 세 device mutation 경로를 기존 pending/sessionStorage 체계와 App 역할 검사에 추가했다. request key/command·계정/설치/store generation을 저장하며 응답 유실·형식/상관 오류 때 새 key로 바꾸지 않는다. 큰 revision을 문자열/BigInt로 비교하고 회수한 receipt의 대상/내용을 정확히 확인한다.
- 장비 선택 변경 때 이전 장비의 report 선택/입력을 재사용하지 않게 했다. 더 보기로 얻은 요약은 polling 때 보존하고 ID를 합친다. authoring·보고서·결정 오류에 대해 사용자용 설명을 추가했다. 기존 공정 검토 조작과 장비 조작의 scope/버퍼를 분리한다.
- P 신규 목록 반례를 포함한 전체288개와 전체 clippy, UI 신규5개를 포함한22개·typecheck/build/format이 통과했다. 첫 UI receipt fixture에 요청 전용 expected 필드가 섞여 strict parser가 거부했으며 fixture를 실제 응답 형식으로 고쳤다. parser를 느슨하게 바꾸지 않았다.
- 실제 S JTC CLI·별도 test signer·P API를 사용해 화면에서 request/report 생성·작성자 승인 비활성·다른 Verifier 승인, 새 보고서의 체크/열린 창 해제·과거 버전 읽기 전용을 확인했다. 권한 설정 문맥 변화는 응답 주입 UI 반례로 구분한다. 실제 authority 파일 재검증 거부는 phase65 API 증거를 유지한다.
- 승인 응답을 실제 commit 뒤 끊고 화면을 새로고침했다. 같은 요청 확인의 body가 원래 body와 같고 decision revision은1개로 유지되며 현재 승인 기록을 다시 조회함을 확인했다. 구체 버전/식별자 확인창·desktop/mobile을 검토했고 overflow/JavaScript 오류가 없다. 기존 공정 검토/독립 승인·응답 유실 브라우저 회귀도 통과했다.
- S Rust/manifest/SDK224개 파일이 phase65 hash와 같아 S152개·clippy 검증을 보존하고 재시험으로 세지 않는다. 두 arm64 이미지를 재빌드했으며 P 기동·S JTC/MELSEC 작성/Host·진단/관리의7개 image smoke가 통과했다. 브라우저는 개발 API 통합이며 현장 HMI 배포 인수가 아니다.
- 규범8개·optional6개·SDK96개를 유지했다. 정확한 source/image/browser 및 검증 로그는 phase66 기록에 둔다. UI의 승인 범위는 DEVICE_PACKAGE_SOFTWARE이며 첫 물리 셀은 NOT_COMMISSIONED다.

[장비 검토 화면 명세](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/apps/operator/DEVICE_REVIEW_UI.md), [검증 기록](../../references/implementation/phase66_checks.json), [승인 확인창](../../references/implementation/phase66-device-review-ui-final/device-approval-target.png).

후속은 현재 승인된 장비 근거를 재검증해 작업/조건/자원을 실제 셀 구성 변경 계획으로 연결하고, 적용 뒤 qualification·별도 시작까지 이어가는 단계다. 실제 native provider/실물 검증·복구·인수와 R01–R30의 나머지 범위는 계속 미완료다.

## 2026-09-12 · 승인된 장비 작업의 연결 후보·prospective 영향 검토

- 현재 steps가 장비 binding과 실행 단계를 함께 담고 compiled process와 host/Intent 일치를 요구함을 확인했다. 승인된 장비 작업을 바로 active steps에 덮어쓰지 않고 공정 순서가 없는 비실행 Candidate로 저장한다. predecessors는 후보에서 빈 배열이며 기존 process/recipe/Work는 유지한다. 새 후보를 실제 공정/Host 변경에 결합하는 적용 절차는 아직 없다.
- Propose는 정확한 device report/approval revision과 binding ID별 action·Host·condition ID→식·성공 후조건·인계 유효기간을 받는다. Intent와 결과표는 현재 승인된 원본에서 정확히 가져온다. 기존 step이면 원래 digest와 다음 condition revision을 후보에 기록하고, 새 step이면 revision1을 사용한다. active step revision은 바꾸지 않는다.
- worker가 실제 Store 원본/현재 package policy/device authority/서명을 재검증한다. writer는 현재 승인·등록·구성·boot/30초 ticket·역할을 다시 검사한다. 누락 condition ID·미지 action·handover0·빈 논리 그룹/잘못된 범위를 거부한다. 빈 관측 문맥의 evaluator는 구조 검사이며 관측 PASS를 만들지 않는다.
- 미등록 Host, 현재 FactSpec에 없는 fact/schema/unit, 다른 site configuration, 완료를 관측할 수 없는 경우를 미해결 issue로 보관한다. true나 성공값을 기본으로 채우지 않는다. process/Host binding/운영 envelope 재검토 요구는 고정 true다. 영향 검토가 이 issue 해결이나 운전 허가를 뜻하지 않는다.
- 기존 process-change 영향 계산을 추가 seed가 빈 경우로 유지하며, device 후보에서는 새 Host/resource를 더해 전체 셀·공유 host/resource/scope의 transitive closure를 계산한다. origin 영향 목록에도 새 자원을 포함한다. 모든 영향 셀의 접근권을 확인하고 이후 새 공유 셀/구성 변경으로 범위가 달라지면 현재성을 잃는다.
- before config는 기존 immutable 저장소에 보관하고 Plan Definition에 원본 승인/catalog/package·선택 입력·candidate/기존 step digest·issue·영향·builder를 결합한다. 입력128KiB, Plan+before 조회자료768KiB 한도를 둔다. 제안/history/event/같은 key 결과는 원자 기록한다. 독립 Verifier가 최신 원본과 후보/영향을 다시 확인하면 IMPACT_REVIEWED로 기록하지만 Definition digest는 유지한다.
- 생성/조회/목록/영향 검토 API를 Runtime의 bounded package worker에 연결했다. Detail은 등록된 context/device approval 현재성을 구분하고 activation_authorized/configuration_changed/application_supported=false를 유지한다. 변경안 UI나 실제 적용 endpoint를 구현했다고 세지 않는다.
- 신규5개 시험은 정확한 원본 후보·독립 영향 검토·구성/전달 불변, 새 resource로 확장되는 영향·전체 셀 권한, 새로운 공유 셀/보고서로 인한 무효화, 누락/잘못된 조건과 미해결 사실, 제안/검토 commit 전 실패·응답 유실의 원래 기록 회수를 다룬다. 전체 P293개와 전체 clippy가 통과했다. 초기 잘못된 query type과 테스트 helper 이름 가림은 수정하고 실패 로그를 보관했다.
- 실제 S JTC package/report·독립 승인→P API의 binding 계획과 두 셀 영향 검토를 통과했다. 제안자 자기 검토 및 일부 셀만 가진 reviewer를 거부하고, 격리된 test fixture에서 두 셀 권한을 가진 별도 impact-reviewer로 검토했다. 같은 요청은 같은 Plan을 회수했고 실제 구성/Run은 바뀌지 않았다. 장비 보고서 새 버전 뒤에는 Plan의 기존 승인 근거가 현재가 아니게 됨을 확인했다.
- 통합 예제는 JTC site digest와 기존 셀 site digest가 달라 SITE_CONFIGURATION_REVIEW_REQUIRED를 그대로 남긴다. 이를 숨기거나 검토로 해소하지 않는다. 기존 공정 검토/독립 승인 브라우저 회귀도 통과했다. 현재 planning API 통합은 개발 loopback이며 현장 적용/배포 인수가 아니다.
- P arm64 image를 재빌드하고 기동/HTTPS 조회/종료 smoke를 통과했다. S Rust/manifest/SDK224개 및 operator production src31개가 phase66 hash와 같아 해당 S152개·clippy/UI22개·S image 검증을 보존하고 재실행으로 세지 않는다. 규범8개·optional6개·SDK96개도 유지한다.

[작업 연결 변경안과 다음 적용 경계](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/DEVICE_BINDING_PLAN.md), [실제 통합 변경안](../../references/implementation/phase67-device-binding-api/device-binding-plan.json), [검증 기록](../../references/implementation/phase67_checks.json).

다음은 미해결 입력을 해결한 후보를 공정 작성·컴파일/검토에 연결하고, Host static binding 변경·quiet/fence·원장/세대를 입증한 뒤 APPLIED_UNQUALIFIED부터 적용하는 절차다. planning과 실제 적용을 같은 완료로 표시하지 않는다. 실제 native provider/물리 교정·지지·복구·인수와 R01–R30의 나머지 작업은 미완료이며 첫 물리 셀은 NOT_COMMISSIONED다.

## 2026-09-12 · 장비 변경 후보의 공정 초안 선택·v2 출처·실제 컴파일

- 기존 active binding catalog를 유지하고 POST preview로 exact device plan refs를 받아 후보를 합치는 경로를 추가했다. 최대16개·중복 plan/동일 binding ID 충돌을 거부하며 IMPACT_REVIEWED·issue 없음·현재 구성/영향/device approval 및 전체 영향 셀 접근권을 요구한다. 선택지 변경은 active step을 수정하지 않는다.
- Save/Version에 plan refs·필요 셀·alias별 device source를 추가했다. 요청 catalog digest를 재계산하고 모든 선택 plan이 실제 선택에 사용되도록 요구한다. 기존 v1 empty-source 저장 형식·digest는 유지한다. 같은 key 회수와 과거 조회도 현재 영향 셀 접근권을 확인한다.
- source/report/plan이 갱신되면 DEVICE_PLAN_CHANGED를 표시하고 내보내기를 거부한다. 원래 binding snapshot은 보관한다. export는 현재 선택/Intent/Host·step digest·provenance를 재계산해 저장본과 대조하며 예전 active step으로 자동 대체하지 않는다. 이 판단은 등록된 문맥의 현재성이지 실행용 원본 파일 fresh proof가 아니다.
- rx.process-compile-input.v2에 exact plan ID/revision/digest·plan 내 binding ID·전체 step digest·실제 action digest를 보관한다. bindings_digest는 bindings와 device_sources를 함께 포함한다. v1에 출처를 넣거나 v2에서 삭제·변경·다른 Host를 끼워 넣는 반례를 거부한다. compiler report와 signed package의 원래 compile input에도 출처를 유지한다.
- 현행 P process review는 active step의 guard/configuration을 검사하므로 device_sources가 있는 입력을 명시적으로 승인하지 않는다. Host/Intent가 기존 값과 같아도 새 출처를 검증한 것으로 간주하지 않는 반례를 추가했다. device-aware process review와 Host binding 적용을 구현한 것으로 세지 않는다.
- 기존 UI decoder는 v2와 plan stale reason을 보존하고 API로 저장한 후보를 조회·내보낼 때 출처를 버리지 않는다. 저장 시 기존 plan refs를 유지하며 후보가 현재가 아니면 조작을 차단한다. 새 plan을 선택하는 전용 UI는 아직 없고 현재 추가된 선택 경로는 API다.
- P 신규2개 초안/회수/stale 반례와 legacy review 거부1개, S의 signed v2 package/recompile·변조 거부1개를 추가했다. P 전체296개·S153개, 양쪽 전체 clippy와 UI24개/typecheck/build/format이 통과했다. 공유 test helper 이름만 정리한 마지막 수정은 production 로직에 영향을 주지 않는다.
- 실제 JTC package/report/impact review를 거친 clean plan→P 공정 초안/선택 저장→v2 bundle→S ResolvedProcess/BT XML→unsigned process package 후보를 만들었다. 실제 action과 provenance가 원문과 같고 qualification/운전이 생성되지 않음을 확인했다. 첫 harness는 trajectory wrapper와 ArtifactRef를 혼동해 recipe asset을 잘못 구성했으며 실제 nested reference를 선택하도록 고쳤다.
- 기존 process review/독립 승인 브라우저 회귀도 통과했다. 초기 fixture 자동 편집이 함수 반환형 위치에도 필드를 넣어 실패한 부분과 일부 테스트에서만 쓰는 helper의 dead-code lint를 수정했다. strict parser나 source/승인 검사를 완화하지 않았다.
- 두 arm64 이미지를 재빌드하고 P 기동·S JTC/MELSEC 작성/Host·진단/관리7개 image smoke를 통과했다. 새 v2 연결의 전체 증거는 위 개발 API/S compiler 통합이며 현장 배포나 native execution 인수가 아니다. 규범8개·optional6개를 유지하고 수정된 CompileInput의 SDK96개를 동기화했다.

[후보 작성·컴파일 출처와 승인 경계](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/DEVICE_PLAN_AUTHORING.md), [실제 v2 입력](../../references/implementation/phase68-candidate-authoring-final/candidate-compile-input.json), [검증 기록](../../references/implementation/phase68_checks.json).

다음은 process review request/job에 후보의 plan refs·guard/configuration 문맥을 결합하고 모든 device 원본/승인/영향을 현재 자료로 다시 검증하는 경로다. 이후 Host binding·quiet/fence/원장 세대와 APPLIED_UNQUALIFIED 적용·qualification을 이어야 한다. 현재 이 승인/적용은 차단되어 있으며 첫 물리 셀은 NOT_COMMISSIONED다. R01–R30의 나머지 범위도 유지한다.

## 2026-09-12 · 동일 보관소의 장비·공정 ABI 정책

- 단일 ABI 정책에서 장비 참조 ABI v2와 공정 ABI v1을 함께 반입하려면 정책 교체가 필요했고, 그 교체는 기존 장비 승인/변경안의 현재성을 잃게 할 수 있었다. `rx.package-verification-policy.v2`에 기본 ABI 외의 명시적 `additional_package_abis`를 추가했다. 기본 ABI 중복·추가 항목 중복·8개 초과·schema와 빈 목록의 불일치를 거부한다.
- 추가 목록이 없으면 기존 정책 직렬화와 fingerprint를 유지한다. 추가 목록은 fingerprint에 결합되며, ABI 외의 base/cell 계약 hash, manifest 종류/schema, target, 서명·종류별 권한·내용 검사는 그대로 적용한다.
- 실제 서명 JTC 장비 패키지와 장비 출처를 보존한 공정 패키지를 같은 정책/보관소에 반입했다. process signer와 device signer의 종류 범위를 분리하고, 두 번째 반입 뒤 registration/fingerprint·장비 승인·변경안 문맥의 현재성이 유지됨을 확인했다. active 구성/Run/qualification은 변경하지 않았다.
- 신규 패키지 정책 2개를 포함한 P 전체298개·S 전체153개, 양쪽 전체 clippy/format과 혼합 반입 통합을 통과했다. 규범8개·optional6개·SDK96개를 확인했다. phase69에서는 이미지를 다시 빌드하지 않았으며 phase68 이미지 결과를 현재 소스 이미지 검증으로 확대하지 않는다.
- 장비 출처가 있는 공정의 fresh review와 Host binding 적용은 여전히 차단한다. 추가 ABI 허용을 장비 승인·셀 적용·운전 허가로 해석하지 않는다. production JTC 제공자·물리 검증과 R01–R30의 나머지 구현 범위는 미완료다.

[검증 기록](../../references/implementation/phase69_checks.json).

## 2026-09-12 · 장비 변경 후보 공정의 현재 원본 검토·독립 승인

- 기존 active step 검토와 별도로 Create.device_plans를 받아 후보 공정 검토를 생성한다. 초안과 같은 composite catalog를 사용하며 clean/current IMPACT_REVIEWED plan과 모든 영향 셀 접근권을 요구한다. 각 plan·장비 Job/report/decision snapshot을 최대16개/512KiB로 고정하고 v2 request의 device_context_digest에 결합한다. v1 empty context 형식은 유지한다.
- 보고서 접수/승인 worker는 같은 Store owner/current policy 아래의 공정·모든 장비 원본을 다시 검증한다. 별도 장비 authority의 pinned 파일/서명/validator/report를 검사하고, 최초 plan과 같은 함수로 조건·완료 대응표·Host/Intent·인계 정책을 다시 만들어 원래 후보와 대조한다. 실제 signed compile-input의 plan/binding/step/action 출처와 composite catalog도 대조한다.
- writer는 commit 전에 plan/장비 승인/authority·구성·공유 영향·계정 접근권·등록/boot/ticket 현재성을 재검사한다. 과거 조회와 동일 key 회수도 영향 셀 접근권을 요구하며 목록은 권한 없는 후보 Job을 노출하지 않는다. 과거 snapshot의 builder가 바뀐 경우 구조 손상으로 취급하지 않고 현재성 검사에서 구별한다.
- 실제 JTC 장비 작성·서명/검토·binding plan→공정 작성·서명→S compiler 보고서→P 접수·독립 승인을 통과했다. 일부 셀만 접근하는 계정의 생성/보고서/결정/조회 및 제출자의 자기 승인을 거부했다. 장비 authority 파일 변경으로 새 공정 승인을 차단하고, 원본 복구 후 승인한 뒤 실제 장비 승인 철회로 종속 공정의 context/approval 현재성이 사라지는 것을 확인했다.
- 동일 요청은 같은 보고서/결정만 회수한다. 새 요청의 재승인은 거부하며 역사적 결정 회수는 권한 재발급으로 세지 않는다. active 구성/Run/qualification은 바뀌지 않았다. 현행 process-change와 Prepared 생성기는 device context를 명시적으로 거부한다. 후속 Host binding/envelope 적용 경계를 통과한 것으로 표시하지 않는다.
- UI가 v2 request/context를 보존하고 누락/형식 혼합을 거부하도록 decoder와 시험을 추가했다. 후보 검토라는 안내와 후보 원문을 표시한다. 전용 plan 선택 화면은 아직 없다. 새 검토 통합은 개발 loopback API이며 production TLS/이미지 승인 인수가 아니다.
- P298개·S153개 전체 Rust 시험, UI25개/typecheck/build/format, 양쪽 전체 clippy, 새 실제 API 통합과 기존 공정 검토·승인/응답 회수 브라우저 회귀를 확인했다. 첫 통합의 마지막 기존 fixture가 결정1개를 가정해 새 철회 결정과 충돌한 문제를 수정했다. 정적 검사의 불필요한 참조·조건 중첩도 정리하고 최종 API 통합을 다시 통과했다. 검사를 완화하지 않았다.
- 규범8개·optional6개를 유지하고 shared request의 SDK96개를 동기화했다. phase70에서는 두 이미지를 재빌드하지 않았다. phase68 이미지 결과는 당시 소스의 증거이며 현재 변경의 이미지 증거로 쓰지 않는다.

[장비 후보 공정 검토](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/DEVICE_PROCESS_REVIEW.md), [검증 기록](../../references/implementation/phase70_checks.json).

다음은 후보 Host/native binding과 운영 envelope의 변경을 적용 절차에 결합하고, quiet/fence·원장 세대·APPLIED_UNQUALIFIED·qualification을 입증하는 단계다. R01–R30 전체 목표는 유지하며 production JTC 제공자·실물 검증을 포함한 미완료 항목은 계속 남는다.

## 2026-09-12 · 장비 공정 변경 계획·스테이징·Host 기동 설정 비교

- 승인된 device context의 공정을 변경 제안/독립 영향 검토/staging에 연결했다. fresh 공정/장비 검증 뒤 후보의 guard·완료·인계 정책을 실제 compiled node별 target step으로 복사하며 active 구성은 유지한다. 새 Host/resource가 포함된 전체 공유 영향과 접근권을 제안·commit·현재성·stage에서 재검사한다.
- Change.host_binding_plan과 공유 rx.host-binding-plan.v1을 추가했다. before/after 참조·검토 문맥, Host별 정렬된 실제 Intent/조건·선택된 서명 패키지/catalog, 다른 영향 셀을 묶는다. 기존 device 없는 plan hash는 유지하고 새 요구는 추가 domain으로 결합한다. stage 시 target과 Host 요구를 다시 계산해 원래 값과 비교한다.
- GET에 HOST_BINDING_CHANGE_REQUIRED를 표시한다. device plan의 BeginPreparation은 아직 거부하며 Host 전송/P 적용 공통 barrier도 막는다. 기존 metadata configuration receipt를 native 설정 적용의 증거로 확대하지 않는다. 완전한 기동 설정 교체/복원·P 연동 receipt와 qualification은 후속이다.
- 제품 rx-hostd inspect-binding-change PLAN CURRENT_CONFIG PROPOSED_CONFIG를 추가했다. 실제 pinned 설정·release-owned native decoder와 P의 서명 패키지/catalog 요구를 대조하며 정확한 Intent/조건/envelope와 전체 cohort를 검사한다. 다른 셀·자격/purpose/peer·저장/네트워크/릴리스 변경을 끼워 넣지 못한다. JSON은 소프트웨어 비교 자료이며 서명된 승인이나 durable Host 적용 receipt가 아니다.
- 실제 JTC package→P 독립 공정 승인→변경/영향 검토/staging→제품 Host CLI의 비교가 통과했다. 두 Host가 공유 자원에 의존하는 두 셀 fixture로 전체 영향 권한을 유지하면서 단일 셀 JTC backend 제약을 그대로 검증했다. qualification/storage 변경을 거부하고 data directory/native process가 생기지 않음을 확인했다. JTC runtime provider available=false, installation_changed=false, activation_authorized=false다.
- 첫 통합에서 source node 이름과 실제 compiled node ID를 혼동한 fixture 기대값을 수정했다. 첫 전체 S 실행 중 기존 ROS pipe 두 시험이 시작 deadline에 걸렸고, 독립 실행3개 및 동시 빌드가 없는 전체 재실행을 통과했다. production timeout과 시험 deadline은 바꾸지 않았다. 실패 로그도 남긴다.
- P 전체298개·S 전체154개(Host 비교 반례1개 추가)와 양쪽 전체 clippy/format·새 API/CLI 통합이 통과했다. UI production src는 phase70과 같으므로 이전25개/typecheck/build 증거를 보존하고 새 시험으로 세지 않는다. 규범8개·optional6개를 유지하며 shared Host plan을 포함한 SDK97개를 동기화했다. 이미지는 이번 단계에서 재빌드하지 않았다.

[변경 계획](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/DEVICE_CHANGE_PLAN.md), [Host 비교](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/runtime/rx-host/HOST_BINDING_INSPECTION.md), [검증 기록](../../references/implementation/phase71_checks.json).

다음은 Host 설치 identity/기존 원장/현재 소유권을 실제로 확인하는 durable 변경 절차와 결과 조회·복원이다. 개발 API의 준비/전송/적용 거부는 확인했지만 이 신규 통합에서 등록 단말의 Host 변경 적용 인수를 수행한 것은 아니다. Native 변경 효과·unknown 결과·중간 장애와 APPLIED_UNQUALIFIED/qualification 연결 및 R01–R30의 남은 범위는 계속 미완료다. 첫 물리 셀은 NOT_COMMISSIONED다.
