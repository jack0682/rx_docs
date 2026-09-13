# RX 구현 초안 종료 — 독립 읽기 검토

검토일: 2026-09-13. 제품 코드 수정·빌드·시험 없이 기존 문서와 검증 기록을 읽었다.
검토 기준: canonical `rx_docs/docs/implementation/requirements.md` R01–R30, `phase79_checks.json`, `phase80_checks.json`, 제품 정의·범위 문서.
인계 기준으로 지정된 커밋은 P `5f9986b`, S `3d323f7`, D `7c19375`다. 이 검토는 현재 checkout과 해당 커밋의 일치를 새로 검증한 기록이 아니다.

## 1. 초안 종료와 제품 완료의 차이

이번 종료는 **기존에 확인한 범위의 구현 초안·증거·미결을 고정해 인계하는 결정**이다. 사용자 요청대로 고도화를 멈출 수 있으며, 아래 미결을 모두 구현해야 초안을 닫을 수 있다는 뜻이 아니다.
요구표는 PARTIAL 26개, OPEN 3개(R12·R21·R29), FIELD_BLOCKED 1개(R30)다. 전체 요구가 VERIFIED인 행은 없다. 단계별 PASS는 해당 행 전체나 납품 제품 완료를 뜻하지 않는다.
제품 정의는 설치·운영·진단·실패·복구·지원까지 반복 제공할 수 있는 자동화 작업을 목표로 한다. 범위 문서는 실제 시연, 운영 파일럿, 첫 납품, 반복 납품을 분리한다. 현재 인계는 실장비 시연 완료나 어느 납품 단계의 인수를 대신하지 않는다.
첫 물리 셀은 **NOT_COMMISSIONED**다. 구현된 모의 자격 활성화나 시뮬레이션 소재 2개 완료를 실물 운전 허가·무인 생산·품질 합격으로 표현하면 안 된다.

## 2. 이번 초안 인계에 포함할 수 있는 것

- Rust·ROS 비의존 공통 코어와 두 제품 저장소·두 이미지의 구현 기반, 계약/영속성/권한/작업 실행/패키지 검토/운영 UI의 부분 구현 및 각 범위의 기존 시험 기록.
- 실제 제품 P/S 이미지와 두 운전 컨테이너를 사용한 FILE_SIMULATION 납품 연결: 초기 설치, 서명·독립 역할 승인, 자격 활성화, UI 수량 2 시작·응답 유실 회수, native 효과 2회·완료/인계, 동일 E의 Idle 복귀·supervisor 협력 종료. P exit 2는 함께 명시한다.
- phase79: 같은 Host와 P-only restart 조건의 명시 승인 RECOVERY_ONLY 통신, 원 Fence/receipt/native 결과 조회, 실제 API/브라우저의 같은 요청 회수. operating rebind나 생산 재개까지 포함하지 않는다.
- phase79 결과 조회 사례: native submit/effect 각 1회, 반복 capture 회수 시 native 재진입 없음. 성공 capture 뒤에도 후조건 연속성 부족으로 `RECONCILING/UNKNOWN/NONE/QUARANTINED` 유지. known-query Host는 별도 시험 fixture이며 P/E는 제품 binary다.
- phase80: 실제 E 제품 CLI의 network-none 오프라인 원장 점검, 원 attachment/stop/request 보존, DB/WAL 사본 읽기와 제한된 무결성 검사. 두 번의 결과 일치와 원본 bytes·mtime·mode·size, P/H/native 무변경이 확인됐다.
- 기준별 소스·이미지·시험·실패 분류·증거 반출 기록. 자동화된 별도 역할 계정의 검증을 실제 담당자의 인수 승인으로 바꾸지 않는다.

## 3. 핵심 미결 8개 — 후속 작업으로 남길 것

1. **생산용 AuthorityProvider와 실제 장비 제어권 연결** — R07/R13/R22. JTC_PACKAGE의 검사·원장 초기화는 있으나 제품 제어권 제공자가 없어 run은 거부한다. controller lifecycle·세대 fencing·실제 Host 실행 연결을 모의 권한으로 대체할 수 없다. `QualificationAuthority`의 절차 신뢰 연결은 별개 빈자리다.
2. **첫 실장비 셀 입력과 인수 범위** — R30, 제품 범위 §4–5. Q03UDVCPU 확인만으로 로봇 선정·그리퍼/지그·신호 의미·PLC 논리·완료/지지 근거가 확정되지 않는다. ‘빼기’, 가공 책임, 초기/종료 상태, 개입 범위와 실제 commissioning은 미결이다.
3. **운전 등록 재연결·재개·복원·셀 전체 종료** — R05/R07/R09/R10/R23–25. RECOVERY_ONLY와 offline inspect는 새 E 등록, attachment 정리, Host operating rebind, 새 자격/Arm/mandate, Run/part 재개, 실제 교체·복원을 완료하지 않는다. E exit 1/PENDING·ATTENTION과 P exit 2가 남는다.
4. **UNKNOWN의 처분과 현장 개입·복구 절차 연결** — R06/R10 및 phase80 개입 검토. 결과 조회, 조사 처분, 절차/인원 인수, 자원 해제, 비운전 Case 종료, 생산 재개는 다른 단계다. 제품 procedure/close 정책의 신뢰 admission과 전체 재개 경로가 미연결이며 성공 capture나 ACK만으로 불명·격리를 지울 수 없다.
5. **필수 자사 지원과 납품 지원 조합의 검증** — R13/R22/R26. 필수 자사 5개 source·전이 의존성의 pin/compile/load와 arm64 이미지 기동은 포함되지만 모든 backend·variant·실제 모델의 연결/교정/지지·설치·지원 검증은 아니다. 자사 지원 의무는 유지하고 초안 종료를 이유로 선택 사항으로 낮추지 않는다.
6. **제품 운영·편집·배포 경로의 잔여 연결** — R14/R16–22. 전체 supervisor/실행 복구, Event·paging/SSE, 공정·장비 적용, 실제 시작/재개 화면, 배포·지원·계정/단말 관리 조작 등이 부분 상태다. R12 고주기 stream과 R21 외부 UI 패널도 OPEN으로 남긴다. 이를 초안 종료 전 새 필수 개발로 만들지 않는다.
7. **장기 운영과 장애·저장소 한계** — R17/R23/R25/R28. 초당 유휴 publication 감사 비용·보존·부하, 장기 운전, 전체 복원·다중 셀 실제 인수는 미완료다. phase80은 일부 정상/미완료 WAL tail도 `WAL_TAIL_UNPROVEN`으로 거부하며, 전체 파일 삭제·유효 prefix 절단·DB+WAL 동반 rollback 탐지를 보장하지 않는다.
8. **고객 효과·납품/교육·지원 공수 측정과 사업 인수** — R29 OPEN, 제품 정의 §2·4. 측정 정의·입력·근거·인수 결과 연결이 남아 있다. 공통화의 반복 납품 이익, 실제 노동 절감·지원 비용·수익성이 입증됐다고 표현할 근거는 없다.

## 4. 종료 판정에 빠져서는 안 될 증거

- **인계 대상 동일성:** 최종 P/S/D 커밋, phase80 소스 archive와 해시, P/S 이미지 digest, 기존 시험에 직접 대응하는 파일 목록. phase79에서 상속한 검증과 phase80 신규 검증을 구분한다.
- **마지막 통과 범위:** phase79/80 모두 `PASS_FOR_REPORTED_SCOPE`. phase80 S 259 passed/0 failed/15 ignored, 상속 P 390 passed/0 failed/16 ignored와 UI 49 passed. Linux 22개 및 WAL 5개는 겹치므로 별도 제품 시험 수로 합산하지 않는다.
- **실제 실행 결과:** 두 컨테이너·parts/effects 2, 동일 E Idle·협력 종료와 P exit 2; known-query의 UNKNOWN/격리·E PENDING/exit 1을 성공 기록과 같은 비중으로 보존한다.
- **제품/시험 환경 경계:** FILE_SIMULATION, 별도 known-query Host fixture, 실제 제품 P/E 및 오프라인 E CLI를 명시한다. 브라우저의 임시 test CA 허용과 별도 API의 인증서 검증 조건도 원 기록에서 지우지 않는다.
- **검증의 제한:** 원장 점검은 현재 P/장비 상태·정지 완료·실행 권한의 증거가 아니며, WAL 검사의 범위와 탐지 불가능한 rollback 유형을 남긴다. 첫 실물 NOT_COMMISSIONED, R01–R30 상태를 유지한다.
- **WIP 보존·제외:** phase81 조사/변경의 보존 위치와 revision을 인계에 적되, 검증 baseline의 기능·시험 성과로 합치지 않는다. 후속 계획 파일의 제안도 구현 완료 증거가 아니다.
- **종료 선택의 기록:** 이번에는 추가 개발을 수행하지 않고 구현 초안을 마무리한다는 사용자 선택, 위 미결이 다음 착수의 참고라는 점을 적는다. 자동 고도화 재개를 종료의 암묵 조건으로 만들지 않는다.

## 5. 문서 해석상 주의

`01_product_definition.md`와 `03_product_scope.md` 머리말은 2026-09-09의 “설계 문서 작성·구체화 / 코드 착수 전” 설명을 남긴다. 현재 단계의 근거는 2026-09-10 착수를 기록한 AGENTS와 구현 추적·phase79/80 증거다. 종료 문서는 오래된 머리말을 현재 상태로 복사하지 않아야 한다.

참조 원본: `/Users/ojaehong/RX_automation/rx_ws/rx_docs/` 아래 `docs/01_product_definition.md`, `docs/03_product_scope.md`, `docs/implementation/requirements.md`, `docs/implementation/next_steps/phase80_intervention.md`, `docs/implementation/next_steps/phase80_recovery_sequence.md`, `references/implementation/phase79_checks.json`, `references/implementation/phase80_checks.json`.
