# RX — 이기종 로봇 협업 개인 프로젝트

RX는 많은 이기종 로봇과 시설을 공통 작업·권한·관측·결과·복구 계약으로 연결하는 개인 프로젝트다. **door-to-door 전체 작업과 구역·마을·도시 규모의 협업·생태계 확장**을 목표로 한다. 산업 자동화는 적용 사례 중 하나다.

이 저장소는 공개 문서 원본이다. 특정 제조사나 고용주를 대표하지 않으며 특정 회사 제품을 기본 지원 조건으로 삼지 않는다. 실제 장비 지원은 profile과 검증 범위로 선언한다.

## 시작하기

1. [프로젝트 목표](docs/01_product_definition.md)와 [현재 범위](docs/03_product_scope.md)를 읽는다.
2. [아키텍처](docs/05_software_architecture.md)와 [장비 지원 정책](docs/13_device_support_matrix.md)을 확인한다.
3. [공통 작업 계약](docs/contracts/v1.0/README.md)과 [셀 운영 계약](docs/cell_operations/v1.0/README.md)을 읽는다.
4. [현재 구현과 과거 증거의 경계](docs/implementation/draft_handoff.md), [미결](docs/implementation/critical_open_items.md), [후속 방향](docs/00_design_roadmap.md)을 확인한다.

## 저장소

| 저장소 | 책임 |
|---|---|
| [rx_docs](https://github.com/jack0682/rx_docs) | 목표·설계·규범 원본, 결정과 검증 근거의 출처 |
| [rx-platform](https://github.com/jack0682/rx-platform) | ROS 비의존 Rust 코어, 권한·판정·원장·Runtime·API |
| [rx-solutions](https://github.com/jack0682/rx-solutions) | 장비 Host·어댑터·작업 실행기·운영 앱·구성 패키지 |

두 소프트웨어 저장소와 두 제품 이미지의 경계를 유지한다. 이 문서 저장소는 독립적으로 읽을 수 있으며 다른 저장소를 로컬에 복제할 필요가 없다. 소프트웨어 빌드·실행은 각 저장소 README를 따른다.

## 상태와 기록

기존 구현 초안 v0.1의 모의 인수는 2026-09-13에 마감됐다. 그때의 commit·이미지·시험 결과는 [고정 원본](references/README.md)으로 보존한다. 현재 제조사 중립 구성의 새 검증, 실물 운전 승인, door-to-door 구현이나 도시 규모 실증을 뜻하지 않는다. 실물 설치는 **NOT_COMMISSIONED**다.

2026-09-14 문서 개정은 제조사별 기본 포함 정책을 profile별 지원 정책으로 바꿨다. 작업 동일성·UNKNOWN·권한·증거·자원 인계 규칙을 유지하며 [규범 개정과 호환 영향](docs/contracts/v1.0/revision_2026-09-14.md)을 별도로 기록한다.

[기여 안내](CONTRIBUTING.md) · [보안 제보](SECURITY.md) · [문서 결정 기록](docs/09_decisions_and_sources.md)

## 라이선스

프로젝트 원본은 [Apache License 2.0](LICENSE)을 따른다. 제삼자 소프트웨어·문서·자료는 해당 저작권과 라이선스가 유지되며 [NOTICE](NOTICE)를 함께 읽는다.

[첫 DYNAMIXEL Ping 모의 어댑터와 남은 번들 통합](docs/41_dynamixel_ping_adapter.md) · [G5.2 실행 근거](references/dynamixel_ping_2026-09-25/README.md)
