# RX 소프트웨어 구현 초안 v0.1 — 마감·인계

마감일: 2026-09-13. **초안 작성 종료, 후속 고도화 대기.**

사용자가 “초안 마무리단계를 확인한 후 핵심 미결을 모아 정리하고 초안을 마무리하라”고 지시했다. 이에 새 기능 추가를 중단하고, 검증된 phase80 구현을 초안 기준으로 고정했다. 이번 인계는 제품 구조와 실행 가능한 모의 운영 초안, 시험 근거와 핵심 미결을 넘기는 것이다. 실제 설비 시연·고객 인수·무인 운영·완제품 출시의 완료 선언은 아니다.

## 1. 무엇을 만드는 제품인가

RX는 여러 로봇과 생산설비의 기능을 공통 작업 계약으로 연결하고, 현장 공정을 구성·검증·실행·운영·유지보수하는 소프트웨어다. 회사는 로봇 선정·배치, 지그·그리퍼, 장비 연동과 공정 설계를 함께 수행해 솔루션으로 납품한다. 첫 고객 목적은 인건비 절감이며 절감액·수익성·운영 배치는 아직 검증하지 않았다.

소프트웨어 자산은 다음과 같이 나눴다.

| 소유 | 역할 | 현재 초안 |
|---|---|---|
| rx-platform | 공통 작업 의미·권한·판정·원장·운영 API | Rust 코어/Runtime. ROS·BT·제조사 SDK와 분리 |
| rx-solutions | 장비 Host·통신/제어 연동·공정/BT·운영 앱·현장 패키지 | ROS/native 연결 계층, 자사 필수 스택, 모의 장비·공정 실행 |
| rx_docs | 제품·사업·설계·계약·검증·인계 기록 | 문서 원본. 세 번째 제품 이미지 없음 |

코어가 맡는 것은 작업 동일성, 불명/결과/무결성/자원 처분, 허가와 기록의 일관성이다. 실제 제어권·장비 동작·관측의 원천은 장비 연동 계층이 책임진다. 코어 또는 Provider 하나가 모든 장비의 물리 상태를 대신 판단하지 않는다.

## 2. 이번 초안에 포함된 연결

- 두 제품 이미지로 새 설치·초기화·기동하고 등록 단말에서 로그인하는 경로.
- 서명된 공정 반입·검토·구성 적용·재검증·자격 활성화와 실제 운영 화면의 시작 요청.
- 모의 소재2개 처리, 서로 다른 operation/effect2회, 결과 확인·자원 인계, 동일 실행기의 다음 작업 대기, supervisor 협력 종료.
- 응답 유실 뒤 같은 요청 key/body로 원래 기록을 회수하는 API/UI 경로.
- 같은 Host가 유지된 P-only 재시작 후 관리자 승인에 따른 RECOVERY_ONLY 통신과 원래 Fence/receipt/native 결과 조회.
- 실제 실행기 미완료 원장을 변경 없이 점검하는 오프라인 명령과 DB/WAL 검증.
- 자사 필수 DynamixelSDK·DHI·open_manipulator·ai_worker·ai_sapiens 및 필요한 전이 의존성의 포함·pin·빌드/기본 확인. 실제 모델별 지원 완료와는 구별한다.

첫 레이저 셀은 **NOT_COMMISSIONED**다. 현재 양성 운전 인수는 FILE_SIMULATION이며, known-query의 Host는 결과 반환 유실을 만드는 별도 시험 fixture다. 자동화된 서로 다른 역할 계정은 실제 사람의 독립 검토를 대신한 인수 주장이 아니다.

## 3. 고정한 코드와 이미지

제품 동작 기준은 아래 phase80 커밋이다. 인계 시 추가되는 README·인계 문서 변경은 런타임 기능 변경이 아니다.

| 대상 | 검증 기준 |
|---|---|
| P 코드 | `5f9986beb951b28c960860bb53a1b4673bdb14ac` |
| S 코드 | `3d323f717af074ce147bfca2ff7a5668c4b2a36c` |
| phase80 문서·증거 | `7c193755dd1878a30eab0a5496451faf27a71840` |
| P 이미지 | `sha256:1830a7ac22a91dd5d4b5e4dd8ea683e64e9d481f1f7b46fc7b80ae88f51e71c0` |
| S 이미지 | `sha256:b32a6bfc4573ab59ec198fb838ed8498e189a1fccc9a87a8f6d3c84c5d5131a1` |

현재 검증 대상은 Linux arm64 조합이다. Rust의 다른 OS 빌드 가능성과 Windows·amd64·GPU 납품 조합의 검증 완료를 혼동하지 않는다. 이미지 digest는 현재 로컬 검증 이미지의 식별자이며 공개/고객 레지스트리에 배포했다는 뜻이 아니다.

## 4. 마감 검증

마감 시 위 기준의 작업 트리·소스/이미지·규범/SDK 일치를 다시 확인하고 **새 임시 설치로 두 컨테이너 공정 인수를 재실행해 통과**했다. 설치 → 서명/승인 → UI 시작·응답 유실 회수 → 소재2/effects2 → 동일 E Idle → 협력 종료를 확인했다. P exit2의 잔여 attention은 유지했다.

| 근거 | 확인된 범위 |
|---|---|
| [마지막 새 설치 인수](../../references/implementation/draft-v0.1-final-acceptance/result.json) | 위 두 이미지, 두 운전 컨테이너, 소재/effect2, 실제 UI와 종료 경로 |
| [phase79](../../references/implementation/phase79_checks.json) | P390·UI49 및 복구 API/브라우저·원래 결과 조회. 해당 단계의 범위 |
| [phase80](../../references/implementation/phase80_checks.json) | S259, Linux 명령/원장22와 WAL 검사, 실제 오프라인 점검·정상 공정 회귀 |
| [마감 감사](draft_closure_audit.md) | 초안 종료 조건과 R01–R30의 현재 상태·근거·미결 |
| [마감 manifest](../../references/draft_closure/closure_manifest.json) | 고정 commit/image, 파일 hash, 마지막 검증과 WIP 보존 위치 |

Linux22개와 WAL unit5개는 다른 suite와 겹치므로 시험 수에 더해 완성도를 부풀리지 않는다. P390·UI49는 변경 없는 phase79 근거이며 S259는 phase80의 최종 회귀다. 지금 전체 suite를 새로 실행했다고 표현하지 않는다.

## 5. 그대로 넘기는 한계

- native 성공 capture를 얻어도 후조건의 실행 연속성이 없으면 작업은 UNKNOWN/NONE/QUARANTINED다. 조회 성공으로 운전을 재개하지 않는다.
- P 재시작 뒤 E는 원 PENDING stop·ATTENTION을 남기고 exit1을 반환할 수 있다. P exit2도 전체 현장 정상 종료를 뜻하지 않는다.
- 오프라인 원장 점검은 현재 장비 상태·현재 P 상태·정리 완료의 증거가 아니다. 일부 정상/미완료 WAL tail도 WAL_TAIL_UNPROVEN으로 거부한다. 삭제·완전한 과거 prefix 절단·DB/WAL 동시 rollback의 완전 탐지는 보장하지 않는다.
- Authority Provider와 제품용 절차 신뢰 연결, 실제 장비·개입·명시적 재개·전체 복원은 핵심 미결이다.

핵심 미결의 우선순위·책임 영역·필요 결정·완료 조건은 [미결 항목](critical_open_items.md)에 모았다. 이 항목을 모두 해결하는 것은 이번 초안 종료의 선행 조건이 아니다. 후속 개발은 별도 착수 범위로 정한다.

## 6. 진행 중이던 phase81의 보존

검증되지 않은 조사 처분 구현을 초안에서 분리했다. 소스를 삭제하지 않고 두 저장소의 `codex/investigation-wip` 브랜치에 보존했다.

| 저장소 | WIP commit | 상태 |
|---|---|---|
| rx-platform | `42ce1ea7e6d104000402155efdf069d8bf6edde5` | 조사 모델/core/API/runtime/config 초안. 전용 core14개 중9개 통과·5개 fixture writer 잠금 실패. 전체 빌드/서비스 통합 미검증 |
| rx-solutions | `3d5f6d09058a44ff9706924cabf3adf50616e828` | 조사 절차 조립/서명 도구 초안. 공유 SDK 동기화·빌드·시험 미실행 |

이 코드는 현재 초안의 기능 목록·통과 시험·이미지에 포함하지 않는다. [실패 로그](../../references/implementation/phase81_investigation_core_tests.log), [보존한 admission 검토](../../references/draft_closure/phase81_wip_admission_notes.md)를 함께 넘긴다. 별도 결정 없이 이 WIP를 다시 합치거나 고도화를 재개하지 않는다.

## 7. 다른 담당자의 확인 방법

세 저장소를 같은 부모 아래 두고 `rx_ws/docs`·`references`의 호환 링크를 문서 저장소로 연결한다. 현재 workspace의 Rust/browser 실행 환경은 `.tools`에 있으며 코드 저장소와 별도다. 새 개발 PC의 환경 설치·배포는 각 README/이미지 명세를 따르는 후속 준비다.

검증된 이미지가 로컬에 있을 때 다음 명령으로 독립 모의 인수를 재현할 수 있다. 새 evidence 디렉토리를 지정해야 하며 실행은 임시 모의 컨테이너·원장·서명 자료를 만들고 종료 시 정리한다. 실제 장비나 기존 운영 DB를 연결하지 않는다.

```sh
cd /Users/ojaehong/RX_automation/rx_ws/rx-platform
CARGO_INCREMENTAL=0 ../.tools/browser-python/bin/python tools/test_cell_delivery.py \
  --composition supervisor \
  --release-evidence ../references/implementation/phase80_delivery_release_preflight.json \
  --evidence-dir ../references/implementation/NEW_DRAFT_ACCEPTANCE
```

코어 시험은 P에서 `CARGO_INCREMENTAL=0 ./tools/cargo test --workspace --all-features`, 솔루션 시험은 S에서 같은 명령을 사용한다. Docker 이미지의 전체 재빌드는 [두 이미지 명세](../14_image_support_spec.md)와 각 `docker/`·native image 문서를 따른다. 필수 ROBOTIS/BT 소스는 pin에 맞게 준비되어야 한다. 위 인수 명령은 고객용 무설정 설치 프로그램이 아니다.

제품 목적·범위 → [현재 초안](draft_handoff.md) → [핵심 미결](critical_open_items.md) → 필요한 계약/모듈 문서 순서로 읽으면 된다. 과거 roadmap의 “코드 착수 전” 문장은 당시 계획으로 보존되며 현재 작업 상태의 판정 기준은 이 인계 문서다.
