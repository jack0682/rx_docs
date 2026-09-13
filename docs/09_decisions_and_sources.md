# 09. 사실·설계 결정·미결 사항·출처

현재 인계 상태: **소프트웨어 구현 초안 v0.1 마감(2026-09-13)**. 아래 내용은 선행 제품·설계 기준이며, 확인된 구현과 미결은 [초안 인계](implementation/draft_handoff.md)와 [핵심 미결](implementation/critical_open_items.md)을 기준으로 읽는다.

[전체 문서 안내](/Users/ojaehong/RX_automation/rx_ws/README.md) · 2026-09-09 기준

## 1. 문서 상태와 적용 방법

이 묶음은 RX를 처음부터 다시 정의하기 위한 제품·소프트웨어 구축 기준안이다. **확인된 요구사항·관측 사실**과 **채택을 권하는 설계 제안**, **추가 결정 사항**을 구별한다. 이 문서의 작성이나 검토 통과를 회사의 제품 결정 승인으로 간주하지 않는다.

제품 정의·범위·구축 계획은 이번 묶음에서 종합한다. 장비의 정확한 인터페이스 사실은 최신 현장 자료와 해당 모델·버전의 제조사 문헌을 따른다. 상세 상태·계약 설계는 첫 셀 계약 초안과 함께 검토하며 차이가 발견되면 사실·결정 기록을 먼저 수정한다.

기존 소프트웨어 문서는 배경 자료다. 과거의 PLC 의존성·저장소 분리·코어 선택·전체 OS 지원 계획을 이번 기준의 확정 전제로 자동 승계하지 않는다. 기존 코드의 가치·재사용 여부는 별도 검증 대상으로 남긴다.

## 2. 확인된 요구사항

| ID | 요구 | 근거·상태 |
|---|---|---|
| R01 | RX 머신텐딩 솔루션을 사업화 | 직접 제공된 사업 방향 |
| R02 | 신뢰성 최우선, 유지보수성 중요 | 직접 명시된 우선순위 |
| R03 | 자사·타사 로봇과 여러 생산설비로 확장 | 장기 사업 목표, 현재 지원 완료 아님 |
| R04 | 지그·그리퍼·공정·로봇 선정·배치를 직접 수행 | 솔루션 제공 범위 |
| R05 | 공통 프레임워크와 고객 납품 앱이 함께 필요 | 소프트웨어 제품 요구 |
| R06 | 공정관리까지 확장 | 향후 제품 범위, 최초 모든 기능 필수 아님 |
| R07 | 메인 PC는 장비 저수준 구현을 직접 모르면서 조정 | 공통 계약과 연동 경계 요구 |
| R08 | ROS 외 SDK·fieldbus·Modbus·TCP·DYNAMIXEL 수용 | 이질적 장비 연결 방향 |
| R09 | OS 이식성과 Windows/Linux 지원을 고려 | 목표, 전체 조합 납품 검증은 별도 |
| R10 | 첫 시연은 레이저 설비 소재 공급 | 첫 적용 범위 |
| R11 | 이상 확인·복구 필요, 작업자 개입은 미정 | 자동화·운영 범위의 미결 |
| R12 | 첫 도입의 주된 이유는 인건비 절감 | 고객 효과의 목표, 금액·실제 효과 미측정 |
| R13 | 외부 미니컴퓨터는 PLC형 부속 장치 | 원격 RX worker 요구로 해석하지 않음 |
| R14 | RX 두 레포는 각각 자기 컨테이너를 가짐 | 후속 명시·범위 확인. 자사 원본 레포별 컨테이너 요구 아님 |
| R15 | 자사 다섯 레포와 실제 필요한 전이 의존성을 기본 지원에 포함 | 후속 명시. 코어 대신 다른 레포에 모두 둘 수 있음 |
| R16 | 코어 언어로 Rust 선택 | 후속 답변 ‘Rust좋아’. 세부 라이브러리·버전까지 확정한 뜻은 아님 |

요구사항 출처는 이 대화의 직접 설명과 정정이며 [사업 기준 정리](/Users/ojaehong/research_RX/RX_machine_tending_business_baseline_v0.2.md)에 관련 맥락이 보존돼 있다. 과거 파일에 남은 장비 미확인 정보는 아래 후속 관측으로 보완한다.

## 3. 현장 관측과 기술 사실

| ID | 확인 내용 | 확정하지 않는 것 | 출처 |
|---|---|---|---|
| F01 | 첫 레이저 설비 PLC Q03UDVCPU, QJ61BT11N, Q64DAN, Q64AD | 실제 통신 설정·PLC 논리·레이저 가공 제어부 관계 | [레이저 자료](/Users/ojaehong/RX_automation/rx_ws/references/laser_plc_interface.md) |
| F02 | Q03UDVCPU 내장 Ethernet과 MC 통신의 제조사 경로 | 현장의 활성 설정·권한·접속·물리 완료 | [공식 사양](https://www.mitsubishielectric.com/fa/in_en/products/faspec/detail.page?formNm=QnUDVCPU_Q03UDVCPU_3827&kisyu=%2Fplcq&lang=2&popup=1), [공식 매뉴얼 §5.1](https://www.mitsubishielectric.com/dl/fa/document/manual/plc/sh080811eng/sh080811engy.pdf) |
| F03 | 레이저 자료는 AJ65SBTB1-32DTE1과 CC-Link IO 구성을 설명 | 도식의 모든 국·장치·신호가 실제 설치됐는지 | [사진 보존·해시](/Users/ojaehong/research_RX/research/rx_first_cell_interfaces_2026-09-09/laser_photo_sources.json) |
| F04 | 로봇 후보 OMY·UR5e·FR3 | 첫 투입 모델·설치 버전·gripper·교정 | 직접 지정·[연구보고서 §2](/Users/ojaehong/research_RX/RX_first_cell_interface_research_v1.0.md) |
| F05 | MCT-2 제어반은 SINUMERIK/SINAMICS·IO 구성 | 정확한 NCU·옵션·외부 API | [MCT-2 기록](/Users/ojaehong/RX_automation/rx_ws/references/mct2_photo_identification.md) |
| F06 | FANUC 31i-MODEL B HMI 사진은 다른 장비 | 해당 HMI의 실제 장비명 | 같은 기록의 분류 정정 |
| F07 | 장비현황 표는 10개 항목, FANUC 표기 6·Siemens 2 | 실제 대수 10대·60% 비율·지원 장비 수 | [장비표 전사와 근거](/Users/ojaehong/research_RX/RX_first_cell_interface_research_v1.0.md) |
| F08 | 파트별 2분 30초~8분은 레이저 가공 시간 | 노동·전체 사이클·절감액·대표 평균 | [사업 기준 §3.1](/Users/ojaehong/research_RX/RX_machine_tending_business_baseline_v0.2.md) |
| F09 | OMY 로컬 설정과 공식 네이티브·ROS 경로, UR·FR3·CNC 자료 조사 | 실물 연동·해당 조합 지원 완료 | [인터페이스 연구와 출처](/Users/ojaehong/research_RX/RX_first_cell_interface_research_v1.0.md) |

장비 사진·시각 자료·SDK 설치 흔적은 지원 완료와 다른 수준의 근거다. 기존 PDF의 레이저 제어기 공란은 원본 기록이고 현재 사실은 F01로 갱신됐다.

## 4. 채택을 권하는 설계 결정

다음 항목은 **권고·검토 중**이며 조직의 승인된 결정이 아니다. 담당 역할과 근거를 연결해 채택·수정한다.

| ID | 권고 | 이유 | 다시 검토할 조건 |
|---|---|---|---|
| D01 | 솔루션 납품과 재사용 소프트웨어 제품·현장 패키지를 구분 | 고객 약속·공통 투자·현장 비용을 명확히 함 | 판매·파트너 구조 변경 |
| D02 | platform은 ROS 비의존, solutions에는 ROS·자사 스택 필수 | 두 컨테이너 경계와 기본 지원 요구 충족 | 사용자 요구·검증된 배포 경계 변경 |
| D03 | 코어와 공정 실행기 경계 분리 | 작업 의미를 공유하면서 공정 표현 변경 | 실제 변경·시험 결과에 따른 경계 조정 |
| D04 | 어댑터와 기계 프로파일 분리 | SDK와 OEM 신호·공정 차이를 구분 | 프로파일로 표현할 수 없는 검증된 장비 논리 발견 |
| D05 | 소수 프로세스의 모듈식 서비스로 시작 | 설치·운영 복잡도 제한 | SDK 충돌·blocking·장애 격리 요구 발생 |
| D06 | Rust 코어는 선택 완료. Tokio/gRPC, C++/Jazzy 연동·BT, TypeScript UI는 세부 스택안 | ROS 경계 분리로 코어 안전성·자사 코드 재사용을 함께 고려 | 선택된 Rust 기준으로 도구·버전·운영 역량·통합 비용을 구체화 |
| D07 | 첫 납품 OS 조합을 좁히고 Windows 코어 검증 병행 | 지원 비용과 이식성 관리 | 첫 계약이 Windows 현장 실행을 요구 |
| D08 | 작업별 능력·UNKNOWN·중복·재시작 의미를 초기부터 구현 | 물리 동작의 불확실성과 지원 가능성 관리 | 실제 장비 증거에 맞춘 상세 의미 조정 |
| D09 | 레이저 PLC 내장 Ethernet MC 통신을 우선 검토 | 확인된 제조사 기능과 기존 PLC 활용 | OEM 접근 제한·부하·설정·운영 조건이 부적합 |
| D10 | 시연→파일럿→납품→반복 적용 단계로 확장 | 현장 검증과 공통 제품 비용을 함께 평가 | 현장·계약 범위 변화 |

대안 비교는 [05 소프트웨어 구조](/Users/ojaehong/RX_automation/rx_ws/docs/05_software_architecture.md), 경제적 판단은 [02 사업 가치](/Users/ojaehong/RX_automation/rx_ws/docs/02_value_and_business.md)를 따른다.

스택·컨테이너·자사 필수 의존성의 최신 근거와 변경 판단은 [12 문서](12_stack_and_container_proposal.md)와 [자사 코드 조사](../references/stack_research_2026-09-09.md)를 따른다. 후속 답변으로 코어 Rust 선택은 확정됐다. 나머지 도구·버전·실물/이미지 지원은 설계·검증 대상이다. [13 기본 지원표](13_robotis_support_matrix.md)를 우선 구체화하고 [14 이미지 명세](14_image_support_spec.md)에 연결한다.

## 5. 착수 전에 필요한 미결 사항

| ID | 결정·확인할 것 | 담당 역할 제안 | 언제까지 필요한가 | 독립적으로 진행할 일 |
|---|---|---|---|---|
| O01 | 첫 품목·기준 수량·사이클 시작/끝·‘빼기’ 의미 | 제품·공정·현장 | G0 범위 완료 | 공통 작업 모델·모의 시험 명세 |
| O02 | 첫 로봇·gripper·tool·교정·설치 SDK | 로봇·기구 | G2 해당 장비 시험 전 | 후보별 계약 검토 |
| O03 | Q03 통신 설정·PLC 프로젝트·OEM 변경 권한 | PLC·OEM·현장 | G2 PLC 연동 전 | MC 인터페이스 명세·상태 모델 |
| O04 | 문·척·가공·소재 관측과 책임·제어권 | 공정·PLC·로봇·전기 | G2 해당 동작 시험 전, G3 전체 결합 전 | 책임표·불명·개입 시나리오 |
| O05 | 안전 기능·일반제어 경계와 시험 방법 | 적합한 안전·기구·전기 책임자 | 관련 물리 시험 전 | 소프트웨어 계약·모의 시험 |
| O06 | 작업자 개입·복구·재개 권한 | 현장 운영·지원·제품 | G2 해당 작업 시험 전, G3 시연·G4 운영 확대 전 | 역할별 화면 초안 |
| O07 | 반복·시간·품질·개입의 단계별 판정 목표 | 고객·제품·검증 | G2 단위 시험·G3 시연·G4 파일럿 각각 사전, G5 계약·인수 시험 전 | 지표 정의·계측 기능 설계 |
| O08 | 첫 OS·CPU·패키징·공정 엔진·구현 언어 | 기술·릴리스 | 해당 구현 착수 시 | 논리 계약·검증 사례 |
| O09 | 견적·직접비·지원 범위·SLA·데이터 보존 | 사업·제품·지원·고객 | G5 납품 계약·인수 전 | 원가·진단·지원 항목 정의 |
| O10 | 기존 코드 재사용과 이전 범위 | 기술·장비·검증 | 구현 계획 구체화 시 | 신규 제품 경계·적합성 기준 |

미결 사항을 추정값으로 채워 실제 동작을 허가하지 않는다. 현재는 그 항목에 의존하지 않는 계약 명세·모의 시험 시나리오·화면 흐름·진단 설계를 계속 작성할 수 있다. 코드·프로토타입 구현은 설계를 정리한 뒤 후속 단계에서 진행한다.

## 6. 주요 위험과 대응

| 위험 | 결과 | 대응 |
|---|---|---|
| 실물 경험 없이 공통화 확대 | 구현은 엄밀해도 실제 작업과 불일치 | 작은 실장비 경로를 초기에 연결 |
| 첫 셀만을 위한 규칙이 코어에 누적 | 다른 현장 추가 때 전체 수정 | 변경 원인·두 번째 구현으로 경계 검증 |
| 모든 장비·OS를 초기 지원 | 시험·유지 비용 급증 | 검증 조합을 명시하고 단계 확대 |
| 명령 성공과 물리 완료 혼동 | 잘못된 후속 동작·실적 | 작업별 완료·관측·요청 연관성 계약 |
| 자동 복구 범위 과장 | 중복·지연 실행·소재 상태 불명 | 미결·잔류 명령·사람 개입을 포함한 재조정 |
| 숨은 상시 감시·정비·지원 노동 | 고객 효과·RX 수익 감소 | 파일럿 노동·개입·지원 공수 측정 |
| 모듈·패키지·장비 버전 불일치 | 재현 어려운 현장 장애 | 배포 명세·변경 관리·복원 시험 |
| 불명·실패 사건의 집계 누락 | 성과 과장·개선 실패 | 모든 시도와 상태·사유 보존 |

## 7. 출처와 문서 간 관계

| 자료 | 사용한 내용 | 적용 주의 |
|---|---|---|
| [사업 기준 v0.2](/Users/ojaehong/research_RX/RX_machine_tending_business_baseline_v0.2.md) | 사업·인건비·시연·가공 시간·장비표 | 장비 후속 사실은 최신 사진 기록 우선 |
| [설계 계획 v0.2](/Users/ojaehong/research_RX/RX_software_design_plan_v0.2.md) | 책임→모델→계약→작은 경로의 설계 순서 | 제품 전체 범위·실행 방안은 이번 묶음에서 종합 |
| [인터페이스 연구 v1.0](/Users/ojaehong/research_RX/RX_first_cell_interface_research_v1.0.md) | 제조사별 접수·상태·완료·OS·옵션 차이 | 버전·라이선스·설치·실물 조건 확인 |
| [첫 셀 계약 v0.2](/Users/ojaehong/RX_automation/rx_ws/docs/11_first_cell_contract.md) | 요청·관측·결론·복구·검증 초안 | 실제 첫 작업 전이표는 후속 개발 |
| [레이저 PLC 기록](/Users/ojaehong/RX_automation/rx_ws/references/laser_plc_interface.md) | 첫 PLC 모델·MC 연동 후보·미확정 신호 | 사진과 도식의 설치·신호 의미 구별 |
| [MCT-2 사진 기록](/Users/ojaehong/RX_automation/rx_ws/references/mct2_photo_identification.md) | Siemens 구성과 HMI 다른 장비 정정 | 정확한 NCU·옵션·API는 미확정 |
| [출처·주장 대장](/Users/ojaehong/research_RX/research/rx_first_cell_interfaces_2026-09-09/source_claim_ledger.md) | 원문·버전·주장 범위·해시 연결 | 과거 자료와 최신 정정 구분 |
| [ROBOTIS SDK](https://docs.robotis.com/docs/software/dynamixel_sdk/overview/) | ROS 외 네이티브 사용 경로 | 완성 로봇 제어·OS 납품 보장 아님 |
| [UR Client Library](https://docs.universal-robots.com/Universal_Robots_ROS_Documentation/rolling/doc/ur_client_library/doc/installation.html) | ROS 밖의 라이브러리 사용 | 설치·지원 조합 검증 별도 |
| [SQLite Transaction](https://www.sqlite.org/lang_transaction.html) | 저장 구현 후보의 트랜잭션 의미 | 제품 저장·복구 요구 충족 여부는 시험 필요 |

외부 문헌은 기술 경로·제약의 근거다. 제품 정의, 아키텍처 경계, 단계별 구축·지표·운영 모델은 RX를 위한 분석과 제안이다. 고객 조사·매출·성능·안전 인증을 이미 확보한 것으로 표현하지 않는다.

## 8. 개정 규칙

새 현장 사실은 F 항목과 원문 출처에 추가한다. 제안이 채택되면 D 항목의 상태·결정자·범위·근거·날짜를 기록한다. O 항목이 해결되면 영향을 받는 계약·프로파일·개발 단계·납품 범위를 함께 수정한다.

전체 안내로 돌아가기: [RX 제품 정의와 소프트웨어 구축 기준](/Users/ojaehong/RX_automation/rx_ws/README.md).

## 9. 새 작업 공간의 진행 지침

2026-09-09 후속 지시를 반영해 현재 작업 공간을 `RX_automation/rx_ws`로 정했다. 설계 문서를 단계적으로 구체화하고 코드 구축은 가장 나중에 수행한다. 두 레포의 논리 경계는 설계하되 실제 레포·빌드·프로토타입은 아직 만들지 않는다. 현재 순서는 [설계 로드맵](00_design_roadmap.md)을 따른다.
