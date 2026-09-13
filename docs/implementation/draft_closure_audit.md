# RX 초안 v0.1 마감 감사

2026-09-13. 사용자의 최신 지시는 추가 고도화를 멈추고 초안·핵심 미결을 정리해 마감하는 것이다. 이 감사는 완제품 완료 기준을 낮추는 기록이 아니다. 원 제품 요구 R01–R30은 아래 상태로 그대로 유지하며, 초안 인계 조건을 별도로 확인한다.

## 초안 인계 조건

| 조건 | 권위 근거 | 판정 |
|---|---|---|
| 제품 목적·공통/현장 경계·두 이미지·자사 의무를 설명할 수 있음 | 제품 정의/범위·인계 문서·요구표 | 확인 |
| 검증된 코드와 미검증 WIP의 위치가 명확함 | phase80 baseline commit, 별도 investigation-wip commit | 확인 |
| 검증 코드/이미지로 정상 모의 흐름이 재현됨 | 마감 새 설치 인수 result: 두 컨테이너·parts/effects2 | PASS 범위 확인 |
| 복구·유지보수의 확인 범위와 미완료가 구분됨 | phase79/80 결과와 UNKNOWN·E1/P2·WAL 한계 | 확인 |
| core·SDK·규범의 일치와 시험 증거를 다시 추적할 수 있음 | phase80 source/evidence hash 재검사·규범8/SDK101 | 확인 |
| 실물/사업 미결과 다음 결정·책임 영역이 정리됨 | critical_open_items O01–O08·Provider 재검토 | 확인 |
| 사용자 지시대로 새 개발을 멈추고 기준판을 인계함 | 동결된 작업 트리·WIP 보존·마감 manifest | 마감 commit/ref의 서명·원격 일치로 확인 |

마지막 항목은 코드·문서의 서명된 마감 commit/tag와 원격 일치를 확인하는 절차로 확정한다. 기준 자료는 [closure manifest](../../references/draft_closure/closure_manifest.json)에서 확인한다. 최종 코드 동작은 [새 설치 인수](../../references/implementation/draft-v0.1-final-acceptance/result.json), 세부 재현 근거는 [phase79](../../references/implementation/phase79_checks.json)·[phase80](../../references/implementation/phase80_checks.json)을 따른다.

## R01–R30의 인계 상태

아래 “현재 증거”는 해당 요구의 부분 구현 근거다. 한 행 전체를 VERIFIED로 판정하지 않는다. 상세 테스트/소스 연결은 원 [요구 추적표](requirements.md)와 단계별 evidence에서 추적한다.

| ID | 요구 | 제품 상태 | 현재 증거 | 초안 종료 시 처리 |
|---|---|---|---|---|
| R01 | 두 독립 레포·두 이미지·Rust ROS 비의존 core | PARTIAL | 두 레포·두 이미지/phase80 및 새 설치 인수 | 초안 구조 확인. 전체 OS/variant 인수 미결 |
| R02 | 공통·셀 v1 schema와 strict codec, 정확한 enum/optional/정규화 | PARTIAL | 규범8·SDK101·codec 시험/phase79 | 부분 codec 검증. 공개 RPC 전체 미결 |
| R03 | intent 동일성·key/activation/slot 유일성 | PARTIAL | phase79 key/body 회수·마감 UI 응답 유실 | 해당 유일성/회수 확인. 전체 상황은 후속 |
| R04 | T1–T5, SQLite 단일 writer·WAL/FULL | PARTIAL | phase79 원자성·phase80 WAL 반례 | T1–T4 등 부분. T5는 WIP로 제외 |
| R05 | Host PREPARED/SEND_ENTERED/VOIDED 및 별도 evidence journal | PARTIAL | phase79/80 known-query native1/publisher | Host 전달/조회 부분. 전체 restart/복원 미결 |
| R06 | 결과/지식/무결성/자원 처분 분리 | PARTIAL | native 성공 회수 후 UNKNOWN/격리 보존 | 상태 축 분리 확인. 최종 조사/해제 미결 |
| R07 | grant/fence/epoch/permit와 native gate | PARTIAL | grant/fence/permit core·모의 Host 인수 | 운전용 rebind/실제 authority 미결 |
| R08 | 조건 평가·관측 age/source/단위·세대 | PARTIAL | source/age/clock 반례 및 현재 Host 읽기 | 모의/계약 범위. 실제 sensor 원천 미결 |
| R09 | RunMandate·part/operation 예산·activation/checkpoint | PARTIAL | 소재2 예산·ID·checkpoint와 E 원문 점검 | 정상 흐름/보존 부분. 명시 재개 미결 |
| R10 | 개입·절차·복구·재시작·비운전 종료 | PARTIAL | RECOVERY_ONLY·Case/절차 core 일부 | 전체 T5/현장 절차/RestartRun 미결 |
| R11 | 여러 셀의 장비·제어기·소재 지지 자원 공유 | PARTIAL | 공유 closure·별도 core 반례 | 전체 다중 셀 실측·shared lease 미결 |
| R12 | 고주기 stream latest-only·expiry·단일 consumer | OPEN | 구현 인수 증거 없음 | 고주기 stream은 후속 범위 |
| R13 | 제품군+모델/모드 profile·필수 자사 지원표 | PARTIAL | 필수 catalogue/SDK/ROS 및 adapter 경계 | 실제 AuthorityProvider·모델 인수 미결 |
| R14 | 선언형 공정·현장 binding·resolved plan·BT 변환 | PARTIAL | 실제 S BT/executor·소재2 흐름 | 부분 공정/실행. 전체 오류·재개 미결 |
| R15 | 독립 검증 패키지·유형별 권한·변경 영향 | PARTIAL | signed commissioning·분리 역할·자격 활성화 | FILE_SIMULATION에서 검증. 전체 정책/실물 미결 |
| R16 | HTTP/gRPC 동일 application·mTLS/현장 계정/단말 | PARTIAL | terminal mTLS/HTTP/gRPC·계정 역할 시험 | 연결된 경로 검증. 공개 API 전체 미결 |
| R17 | 일관 snapshot·SSE·권한별 UI projection | PARTIAL | snapshot/projection 일부 및 상태 조회 | SSE·paging·부하/보존 전체 미결 |
| R18 | 시각적 공정 편집·새 초안·검증·비교·변환 | PARTIAL | 초안·버전·binding/compile 소스와 관련 시험 | 전체 시각 편집/비교 UX 인수 미결 |
| R19 | 운영/실적/조건/개입/복구 화면 | PARTIAL | 실제 UI 시작·상태·복구 조회/기록 발견 | 운영/복구 UI 일부. 실제 재개 UX 미결 |
| R20 | 구성·검증·배포·지원·계정/단말 화면 | PARTIAL | 구성/검토/승인 일부 UI와 API | 관리·배포·계정/단말 화면 전체 미결 |
| R21 | 등록된 외부 UI 패널·제한된 메시지 API | OPEN | 구현 인수 증거 없음 | 외부 UI 패널은 후속 범위 |
| R22 | 프로세스·권한·volume·network·variant 구성 | PARTIAL | 실제 두 컨테이너 supervisor/권한/volume | 현재 모의 조합. 전체 배포 variant 미결 |
| R23 | 정상 종료·부분 장애·제한 재시작 | PARTIAL | 정상 협력 종료·E PENDING/exit1 보존 | P exit2·전체 현장 종료/재기동 미결 |
| R24 | 호스트 관리 도구·고정 작업·유지보수 journal | PARTIAL | 유지보수 준비 일부·offline recovery-inspect | 실제 설치 교체·원장 인수 미결 |
| R25 | 백업·복원·binary rollback 구별 | PARTIAL | snapshot/backup 기초·WAL 무결성/한계 | 전체 백업복원·binary rollback 인수 미결 |
| R26 | 자사 5개 필수 source 및 전이 의존 lock | PARTIAL | 자사5개+전이 source pin/빌드/기본 확인 | 필수 의무 유지. 모든 모델 운전 완료 아님 |
| R27 | 모의 환경과 실장비 접근 분리 | PARTIAL | FILE_SIMULATION·network-none·물리 시작 거부 | 마감 인수의 환경 구분 확인 |
| R28 | 통합 시험·판정·독립 oracle·증거 반출 | PARTIAL | 단계별 소스/hash/log·독립 effects/oracle | 증거 보존 확인. 전체 SC/CO/현장 인수 미결 |
| R29 | 납품/운영교육/인건비·지원 공수 측정 구조 | OPEN | 사업 지표/측정 정의 문서 | 사업 운영 측정 기능·실측 인수 없음 |
| R30 | 첫 현장 미확정 값 및 실제 commissioning 경계 | FIELD_BLOCKED | Q03UDVCPU 자료·물리 NOT_COMMISSIONED | 현장 입력/실장비 인수 대기 |

집계: PARTIAL26, OPEN3(R12/R21/R29), FIELD_BLOCKED1(R30), VERIFIED0. 제품 완성률을 산출하지 않는다. 신규 기능 파일이 존재하거나 일부 시험이 통과했다고 미검증 조합을 완료로 올리지 않았다.

## 검증 선택과 제한

마감에서 변경한 것은 인계·상태 문서와 미검증 WIP의 보존 위치다. 런타임 코드는 검증된 phase80으로 복구했고 전체 소스 hash/이미지와 규범·SDK를 대조했다. 기능을 고도화하기 위한 새 시험 묶음을 만들지 않고, 실제 납품 흐름에 가까운 기존 두 컨테이너 인수를 새 설치로 재실행했다. P390/S259/UI49의 원 시험 범위와 ignored 항목은 원 evidence에 남긴다.

모의 qualification, 자동화된 별도 역할 계정, 파일 기반 native 효과, 시험용 Host, P/E 종료 attention을 실제 현장의 물리 허가·사람 인수·안전 성능으로 바꾸지 않는다. R30 현장 미결은 초안 작성 자체의 차단이 아니라 후속 실물 착수 조건이다.

[독립 읽기 검토](../../references/draft_closure/independent_closure_review.md)는 초안/완제품의 구분·WIP 제외·미결8개·종료 한계를 재확인했다. Provider 재검토 역시 구현이 아니라 미결의 실제 소스 근거다.
