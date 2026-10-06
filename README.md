# RX — evidence와 역사 기록

이 저장소는 RX의 실행·검증·실패·수락 기록과 그 provenance를 보관한다. RX는 이기종 로봇·설비·서비스를 공통 작업·권한·상태·결과·복구 계약으로 연결하는 vendor-neutral 개인 프로젝트다. 특정 제조사나 고용주를 대표하지 않는다.

현재 제품 source, canonical 문서·계약, SDK와 설치 안내는 [RobotTransformation](https://github.com/jack0682/RobotTransformation)에서 관리한다. 이 저장소의 기존 `docs/`와 `references/`는 과거 evidence가 인용하는 경로·commit·URL의 의미를 유지하기 위해 남긴다. 역사 문서를 현재 제품 계약의 별도 원본으로 수정하지 않는다.

## 읽는 순서

1. 현재 제품을 이해하거나 개발하려면 [canonical 문서 입구](https://github.com/jack0682/RobotTransformation/blob/develop/docs/README.md), [제품 정의](https://github.com/jack0682/RobotTransformation/blob/develop/docs/01_product_definition.md), [core charter](https://github.com/jack0682/RobotTransformation/blob/develop/docs/43_core_charter.md), [계약 소유권·입구](https://github.com/jack0682/RobotTransformation/blob/develop/contracts/README.md)를 읽는다. 이 링크는 현재 `develop`을 가리키는 탐색 입구다.
2. 특정 주장이나 실패를 확인하려면 [evidence index](references/README.md)에서 원 source/artifact/Run과 해당 시점의 검증 범위를 찾는다. 역사 근거에는 mutable `develop` 대신 full commit SHA와 artifact digest를 사용한다.
3. 새 기록을 제출하려면 [evidence charter와 접수 규칙](references/EVIDENCE_CHARTER.md)을 따른다. 기존 실패를 덮거나 새 ID로 바꿔 정상 결과로 만들지 않는다.

## 책임

| 저장소 | 현재 역할 |
|---|---|
| [RobotTransformation](https://github.com/jack0682/RobotTransformation) | 제품 source·canonical 문서/계약·SDK·distribution 및 해당 candidate의 검증 gate |
| [rx_docs](https://github.com/jack0682/rx_docs) | raw evidence, 실패·진단·수락 provenance, source/artifact/Run 연결과 기존 역사 문서 보존 |
| [rx-platform](https://github.com/jack0682/rx-platform), [rx-solutions](https://github.com/jack0682/rx-solutions) | 기존 source history·tag·서명·release와 evidence locator 보존. archive 상태는 별도의 cutover 기록으로 확인 |

이 저장소의 기존 CI는 JSON 문법·local link·고정 규범 hash·문서 내 table 검사·기여 정책을 확인한다. 새 evidence의 모든 주장을 자동 인증하는 검사는 아니다. CI 성공, 문서 merge 또는 source import는 runtime 성공·deployment·physical completion·functional safety·사용자 수락을 뜻하지 않는다.

## 보존 중인 상태

F2′ CP2의 [사용자 미수락·진단 기록](references/2026-10-05-f2-cp2-not-accepted/DIAGNOSIS.md)은 원 Run의 UNKNOWN/QUARANTINED와 이후 RECOVERY_REQUIRED를 보존한다. 이는 2026-10-05 기록이며 현재 runtime을 새로 조회한 결과가 아니다. 문서 publication이나 repository migration으로 Run을 release·재발행·수락하거나 CP3를 시작하지 않는다.

기존 v0.1 및 각 SIM 검증은 당시 source·이미지·환경에만 적용한다. [이전 고정 원본](references/README.md), [역사 제품 정의](https://github.com/jack0682/rx_docs/blob/4384ed49e384c53e645f71757ce597292b928eb6/docs/01_product_definition.md), [역사 core charter](https://github.com/jack0682/rx_docs/blob/4384ed49e384c53e645f71757ce597292b928eb6/docs/43_core_charter.md)를 그대로 읽을 수 있다. 새로운 제품이나 physical installation의 수락으로 소급하지 않는다.

[기여 안내](CONTRIBUTING.md) · [보안 제보](SECURITY.md) · [evidence charter](references/EVIDENCE_CHARTER.md)

## 라이선스

프로젝트 원본은 [Apache License 2.0](LICENSE)을 따른다. 제삼자 자료의 저작권·라이선스·원문 notice는 그대로 보존하며 [NOTICE](NOTICE)를 함께 읽는다.
