# RX 구현 초안 — 진행 기준

2026-09-10 사용자의 명시적 구현 착수 지시에 따른다. 목표는 지금까지의 설계를 두 레포의 실행 가능한 초안으로 연결하고 검증하는 것이다. 첫 현장의 실제 장비 지원 완료·납품 인증을 주장하지 않는다.

## 구현 원칙

- `rx-platform`: Rust domain, application, ports, SQLite adapter, HTTP/gRPC, host maintenance tool. ROS·BT·native driver를 core에 의존시키지 않는다.
- `rx-solutions`: 자사 필수 스택, 장비 Host, ROS/native adapters, 선언형 공정/BT 실행, 패키지, React 구성·운영 앱.
- 두 레포 각각의 이미지. 호스트 관리 도구는 platform 소유이며 제3 레포/이미지가 아니다.
- 하나의 Linux PC·복수 셀·단일 권위 Runtime. 모델별 controller/공유 자원 기준으로 Host를 배치한다.
- 첫 물리 셀은 NOT_COMMISSIONED. 모의 셀과 실물 구성은 분리하고 모의 근거로 실물 qualification을 만들지 않는다.
- 기존 규범 파일과 manifest를 그대로 보존한다. 발견한 규범 공백은 결정 기록으로 남기며, 미구현 기능을 비슷한 구현으로 대체해 완료 표시하지 않는다.

## 작업 순서

1. 계약 표현·검증과 순수 domain의 불변식.
2. 영속 command processing, 원자성, 단일 writer, Host journal 및 장애 복구.
3. 공정·장비·현장 패키지, source 변환과 모의 Host/실행기의 전체 경로.
4. 인증·운영·구성 API 및 시각적 편집/운영/복구 화면.
5. 자사 스택 lock·연동 경계, 두 이미지, 기동/종료/배포/복원 도구.
6. 계약·프로세스·UI·복원 시험, 실제 지원 범위/미결 현장 입력 감사.

순서는 구현상의 의존 순서다. 후반 항목을 목표에서 제외하지 않는다. 완료는 `requirements.md` 전체와 실제 검증 증거로 감사한다.

## 현재 상태

구현 중이다. phase72에서 실제 종료 구성·Host 원장에 묶인 영속 변경 준비/조회/취소와 기동 차단을 추가했다. phase73에서는 S production UI bundle을 P 직접 단말 HTTPS에 연결하고 실제 두 이미지·등록 단말 브라우저로 로그인/표시/CreateRun 응답 유실 회수를 검증했다. P310개·S160개 Rust 시험, UI25개·bundle 생성기3개 및 두 최신 이미지/7개 smoke가 통과했다. 실제 StartRun/상시 실행기 배정·초기 인수와 이상 후 재개, Host 설치 교체·복원은 남는다. 다음 연결 우선순위는 [제품 전체 인수 흐름](product_acceptance_path.md)을 따른다.

ROBOTIS position JTC의 Rust NativeAdapter는 trajectory 원본·controller session·최종 허가 유효기간 검사, 송신 전 영속 기록, 원래 UUID 결과 조회, 분쟁 보존과 child 종료 확인을 제공한다. S가 profile에 결합한 결과 대응표를 생성하고 P는 제조사 비의존 데이터로 성공·실패·취소를 판정한다. Template/Site에서 profile·허용 Intent·결과표와 공통 작업 선언을 작성하는 서명 패키지 도구, Host의 JTC_PACKAGE 검사·metadata 초기화, P의 선언 반입·보관/API/화면까지 연결했다. 제품용 Authority/lifecycle 제공자가 없어 JTC run은 거부한다. 제조사 검증·장비 검토 승인과 실제 셀 구성 변경, controller 교체 차단 및 물리 검증은 남아 있다.

application outbox→Host→T2→자원 인계→두 소재 시도 완료, 로컬 계정/API·운영 화면과 별도 Host 증거 전송을 연결했다. Host의 인증된 상태 조회·초기 등록·사용권 갱신도 연결했으며, 동일 boot의 원장 교체를 거부한다. 연결 등록은 장비 조건의 충족이나 운전 허가를 만들지 않는다. 공개 제어 사건의 전체 wire 매핑, 자동 운영 서비스·공정 편집/BT·복구 전체·제품 배포·자사 스택 지원은 아직 미완료다. 각 변경과 시험의 범위는 `progress.md`에 기록한다. 개발 도구는 workspace `.tools` 아래에 설치해 기존 사용자 shell 설정을 변경하지 않는다.

- [로컬 서비스와 HTTP 경계](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-api/README.md)
- [운영 앱과 브라우저 검증 방법](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/apps/operator/README.md)
- [ROBOTIS JTC ROS 연결 계층](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/native/ros-jtc/README.md)
- [ROBOTIS JTC Rust 어댑터·원장·허가·종료](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/runtime/rx-host/ROBOTIS_JTC_ADAPTER.md)
- [제조사별 결과 대응표·코어 결론 연결](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/NATIVE_OUTCOMES.md)
- [ROBOTIS JTC 패키지 작성·검증·Host 등록](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/runtime/rx-host/JTC_PACKAGE.md)
- [ROBOTIS JTC 모의 작성 예제](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/examples/device/robotis-jtc-simulation/README.md)
- [장비 작업 선언 반입·보관·화면](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/DEVICE_CATALOG.md)
- [장비 패키지 소프트웨어 검증·독립 승인 API](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/DEVICE_REVIEW.md)
- [장비 소프트웨어 검토·승인 화면](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/apps/operator/DEVICE_REVIEW_UI.md)
- [승인된 장비 작업의 연결 변경안·영향 검토](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/DEVICE_BINDING_PLAN.md)
- [장비 변경 계획과 Host별 요구](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/DEVICE_CHANGE_PLAN.md)
- [Host 기동 설정 비교](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/runtime/rx-host/HOST_BINDING_INSPECTION.md)
- [장비 후보 공정의 현재 원본 검토·독립 승인](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/DEVICE_PROCESS_REVIEW.md)
- [장비 변경 후보의 공정 작성·컴파일 출처 연결](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/DEVICE_PLAN_AUTHORING.md)
- [장비 Template/Site 작성·서명·검사 도구](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/runtime/rx-device-package/README.md)
- [오프라인 모의 작성 예제](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/examples/device/melsec-simulation/README.md)
- [서명된 장비 패키지·제품 Host 기동](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/runtime/rx-host/DEVICE_PACKAGE_STARTUP.md)
- [실행파일과 구별한 장비 참조 패키지 v2](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-package/DEVICE_REFERENCE.md)
- [미쓰비시 NativeAdapter·작업 원장·Host 통합](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/runtime/rx-host/MELSEC_ADAPTER.md)
- [미쓰비시 MC3E 통신 라이브러리·모의 검증](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/drivers/rx-melsec-mc/README.md)
- [미쓰비시 Host 어댑터 후속 연결 계획](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/drivers/rx-melsec-mc/HOST_ADAPTER_PLAN.md)
- [제품 Host 실행파일·기동/종료·배포](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/runtime/rx-host/HOST_SERVICE.md)
- [P 자격 발급·영속 조정·전역 활성화](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/QUALIFICATION_ACTIVATION.md)
- [Host 자격 수용·별도 Arm과 최종 gate](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/runtime/rx-host/QUALIFICATION_ACCEPTANCE.md)
- [적용 후 재검증 근거·독립 검토](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/REQUALIFICATION_REVIEW.md)
- [활성 구성 교체·과거 작업의 구성 보존](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/PROCESS_APPLY.md)
- [P Host 구성 전송·결과 조정](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/HOST_CONFIGURATION_DISPATCH.md)
- [Host 공정 문맥·영속 receipt](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/runtime/rx-host/PROCESS_CONFIGURATION.md)
- [변경 계획·영향 검토·staging·준비](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/PROCESS_CHANGE.md)
- [반입·검토·승인 화면](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/apps/operator/PACKAGE_REVIEW_UI.md)
- [공정 검토·소프트웨어 승인](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/PROCESS_REVIEW.md)
- [사용자·셀별 패키지 반입 접수](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/PACKAGE_INTAKE.md)
- [검증된 패키지 보관·현재 정책 재검증](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-package/STORE.md)
- [공정 패키지 조립·외부 서명·내용 검증](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/runtime/rx-process-package/README.md)
- [공정 초안의 장비 작업 바인딩](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/DRAFT_BINDINGS.md)
- [공정 초안·버전·구조 검사](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/PROCESS_DRAFTS.md)
- [솔루션 프로세스 관리](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/runtime/rx-supervisor/README.md)
- [Host 실행 서비스의 현재 진단](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-runtime/HOST_SERVICE_HEALTH.md)
- [운영 화면의 조건·관측 진단](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/OPERATOR_CONDITIONS.md)
- [관측 수집·유지 조건 만료 감시](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/OBSERVATION_INGESTION.md)
- [Host bootstrap·lease 연결](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-host-client/HOST_CONNECTION.md)
- [자사 스택과 솔루션 이미지](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/dependencies/NATIVE_IMAGE.md)
- [플랫폼 실행 파일·기동·종료·첫 이미지](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-platformd/README.md)
- [사용자·등록 단말·HTTPS 신원](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/TERMINAL_IDENTITY.md)
- [셀 상태와 운영 API 서비스 세션](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/CELL_CONTEXT_AND_OPERATOR_PEER.md)
- [비운전 사건 종료](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/NON_OPERATING_CLOSURE.md)
- [절차 사실과 상태 승격](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/PROCEDURE_REPORTS.md)
- [개입 사건과 알림 확인](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/INTERVENTION_CASES.md)
- [직렬 소재 조정](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/runtime/rx-executor/PRODUCTION_COORDINATOR.md)
- [실행 서비스와 중단 기록](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/runtime/rx-executor/SERVICE_LIFECYCLE.md)
- [지속 BT 엔진과 요청 큐](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/native/executor/PERSISTENT_ENGINE.md)
- [실행기의 분기·대기와 복원](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/runtime/rx-executor/DECISIONS_AND_RECOVERY.md)
- [분기·대기 후보와 체크포인트 확정](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/CHECKPOINT_COMMIT.md)
- [기존 작업 조회와 자원 인계](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/RECONCILIATION.md)
- [BT 중단과 PauseRun](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/EXECUTOR_PAUSE.md)
- [S 영속 요청과 유한 worker](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/runtime/rx-executor/JOURNAL_AND_WORKER.md)
- [복원 자료와 현재 실행 상태·Frame 연결](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/EXECUTION_READ.md)
- [실행기 유한 작업 제출·현재 결과 조회](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/EXECUTOR_SUBMISSION.md)
- [실행기 소재 시도·단계 요청](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/EXECUTOR_REQUESTS.md)
- [실행기 세션·원격 Run 조회](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/EXECUTOR_PEER.md)
- [실행 복원 상태와 artifact](https://github.com/jack0682/rx-platform/blob/codex/initial-draft/crates/rx-application/CHECKPOINT_ARTIFACT.md)
- [요구 추적표](requirements.md)
- [진행 기록](progress.md)
