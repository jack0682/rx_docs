# RX 설계·검증 문서

RX의 제품 정의, 사업 목적과 범위, 소프트웨어 구조, 계약, 장비·공정·배포 설계, 구현 진행과 검증 근거를 관리한다. **소프트웨어 구현 초안 v0.1은 2026-09-13에 마감했다.** 첫 물리 셀은 **NOT_COMMISSIONED**이며 제품·실장비 납품 완료는 아니다.

## 먼저 볼 인계 문서

- [초안 인계](docs/implementation/draft_handoff.md)
- [핵심 미결 8개](docs/implementation/critical_open_items.md)
- [마감 감사](docs/implementation/draft_closure_audit.md)

## 설계·근거를 읽는 순서

1. [설계 로드맵](docs/00_design_roadmap.md)
2. [제품 정의](docs/01_product_definition.md), [사업 가치](docs/02_value_and_business.md), [제품 범위](docs/03_product_scope.md)
3. [구조 제안](docs/10_structure_proposal.md), [자사 기본 지원](docs/13_robotis_support_matrix.md), [두 이미지](docs/14_image_support_spec.md)
4. [공통 계약 v1.0](docs/contracts/v1.0/README.md), [셀 운영 계약 v1.0](docs/cell_operations/v1.0/README.md)
5. [상세 설계 순서](docs/19_detailed_design_sequence.md)
6. [현재 구현 상태](docs/implementation/README.md), [요구 추적표](docs/implementation/requirements.md), [진행 기록](docs/implementation/progress.md)

## 저장소의 역할

| 저장소 | 내용 |
|---|---|
| 이 저장소 | 전체 설계·조사·검증 문서와 증거 |
| [rx-platform](https://github.com/jack0682/rx-platform) | ROS 비의존 Rust core/runtime, 권위 원장, API와 플랫폼 이미지 |
| [rx-solutions](https://github.com/jack0682/rx-solutions) | ROS/native 장비 연동, 자사 필수 스택, 공정·BT, 운영 앱과 솔루션 이미지 |

제품 소프트웨어는 두 레포·두 이미지 구성을 유지한다. 문서 저장소가 세 번째 제품 프로세스나 이미지를 추가하지 않는다. 소스와 함께 검토해야 하는 모듈 README 및 빌드·검증에 필요한 규범/SDK 사본은 소스 저장소에 남긴다.

## 자료 보존과 현재성

`docs/`는 기존 RX 작업 공간의 설계 문서이며 `references/`는 조사와 구현 검증 기록이다. 과거 source archive와 시험 로그도 증거의 일부로 보존한다. 문서의 구현 완료 여부는 최신 진행 기록과 해당 단계의 검증 범위로 판단한다. 모의 시험은 실물 qualification을 뜻하지 않는다.

규범 원본 8개의 byte와 manifest hash를 유지한다. 초기 문서의 ‘코드 착수 전’ 표현은 당시 계획이며, 구현 착수 이후에는 최신 구현 기록을 함께 읽는다. 기록 속 절대 로컬 경로 및 이전 연구 공간·원본 사진에 대한 링크는 작성 당시 출처로서 남아 있으며 이 저장소가 외부 자료 전체를 포함하는 것은 아니다.

로컬 작업 공간에서 세 저장소를 같은 부모 디렉토리에 두며, 기존 `rx_ws/docs`와 `rx_ws/references`는 이 저장소의 해당 디렉토리로 연결한다. 기존 도구와 증거 경로를 유지하기 위한 연결이다. 문서 본문에서 코드 저장소를 가리키는 링크는 GitHub 경로로 연결한다.
