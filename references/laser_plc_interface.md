# RX 첫 레이저열처리 설비 PLC와 연동 경로 v0.1

## 1. 확인된 설비 PLC

2026-09-09 제공된 자료는 첫 레이저열처리 설비의 PLC와 CC-Link 입출력 구성에 대한 사진·설명이다. CPU 전면과 주석에서 **Mitsubishi Electric MELSEC-Q `Q03UDVCPU`**가 확인된다. 기존 장비현황 PDF의 제어기 공란은 원본 기록으로 유지하되, 현재 설비 PLC 식별 정보는 이번 사진으로 보완한다.[^1]

이 확인은 설비 PLC에 관한 것이다. 레이저 발진기·가공 제어부의 모델이나 이 PLC와의 세부 제어 관계까지 확정한 것은 아니다.

| 구성 | 모델 | 근거와 확인 범위 |
|---|---|---|
| PLC CPU | Q03UDVCPU | 사진 전면 모델명·설명 일치. 설치 firmware·프로그램 버전 미확인 |
| CC-Link 통신 모듈 | QJ61BT11N | 사진·주석에서 확인. 실제 국번·통신 속도·설정은 미확인 |
| 아날로그 출력 | Q64DAN | 사진·주석에서 확인. 연결 대상과 신호 스케일 미확인 |
| 아날로그 입력 | Q64AD | 사진·주석에서 확인. 연결 대상과 신호 스케일 미확인 |
| CC-Link 입출력 장치 | AJ65SBTB1-32DTE1 | 두 번째 자료의 제목과 장치 사진. 개별 설치 수량·국번·채널 매핑 미확인 |
| 확장 공간 | 자료상 예비 슬롯 2개 | 빈 위치와 설명이 보임. 필요한 모듈의 전력·호환성·현장 적용 검토는 별도 |

QJ61BT11N의 공식 사양은 CC-Link master/local 모듈과 RS-485 기반 버스를 설명한다.[^4] CPU 전면의 `CC-Link IE Field Basic` 표기와 별도 QJ61BT11N이 담당하는 CC-Link를 같은 통신 경로로 합쳐 해석하지 않는다.

## 2. CPU 내장 Ethernet을 통한 연동 후보

Q03UDVCPU 공식 사양에는 내장 Ethernet과 MC 프로토콜 연결이 명시돼 있다.[^2] QnUCPU 내장 Ethernet 매뉴얼은 PC에서 CPU device data를 읽고 쓰는 MC 통신, TCP/UDP 설정, QnUDVCPU의 SLMP Connection 설정을 설명한다. RUN 중 쓰기와 사용 frame은 설정·CPU 조건에 영향을 받는다.[^3]

따라서 **추가 Ethernet 모듈 구입을 전제하기 전에 CPU 내장 포트를 통한 연동을 검토할 수 있다.** 사진에는 이 포트에 케이블이 이미 연결돼 있으므로 기존 연결 대상·용도와 통신 설정을 확인해야 한다. 물리 포트와 제조사 지원 기능의 존재는 현재 RX 연결이 허용·구성됐다는 뜻은 아니다.

권하는 검토 경로는 다음과 같다. 이는 설계 후보이며 아직 구현·실물 시험한 경로가 아니다.

**RX 메인 PC → Mitsubishi 연동 모듈 → Ethernet/MC 통신 → Q03UDVCPU의 작업 요청·상태 영역 → PLC 프로그램 → 기존 CC-Link 입출력 → 현장 장치**

RX는 셀 작업을 요청하고 결과를 관리한다. PLC는 합의된 요청을 해석하고, 실제 설비 조건을 확인하며, 문·척 등 자신이 담당하는 국소 동작을 실행한다. 어떤 장치가 실제로 이 PLC의 제어 대상인지는 프로그램과 배선 자료로 정해야 한다.

이 경로에서 PC는 연결된 CPU에 접근한다. CPU를 통해 CC-Link의 다른 CPU로 MC 메시지를 자동 중계할 수 있다고 가정하지 않는다.[^3] 원격 IO의 상태는 해당 PLC가 사용하는 메모리 매핑·프로그램을 통해 의미를 확인한다.

## 3. PC와 PLC 사이에 정할 작업 계약

단순한 register 쓰기 성공과 장비 작업 완료를 구분한다. 예를 들어 RX가 문 닫기를 요청할 때, PLC의 요청 접수와 실제 문 닫힘·필요한 잠금 조건이 각각 무엇인지 정의해야 한다.

다음은 PLC 프로그램을 검토한 뒤 합의할 **논리 필드 제안**이다. 실제 X/Y/M/D 주소나 배선을 지정하지 않는다.

| 방향 | 필드 후보 | 의미 |
|---|---|---|
| RX → PLC | 요청 세대·요청 번호, 작업 종류·입력, 요청 게시 표시 | 어떤 요청을 이번에 처리할지 식별 |
| PLC → RX | 접수한 요청 번호, 수락·거부 및 사유 | PLC의 요청 접수 확인 |
| PLC → RX | 현재 요청·실행 상태 | 접수 이후 진행 중인지 확인 |
| PLC → RX | 완료 요청 번호, 결과 코드, 완료 근거 | 이번 요청과 결과를 연결 |
| 양방향 | 연결 생존·기동 세대·운전권 정보 | 재부팅·단절·수동 조작 후 과거 요청 혼동 방지 |

여러 필드의 쓰기를 PLC가 하나의 일관된 요청으로 인식하는 방법도 필요하다. payload와 요청 게시를 구분하고, PLC가 입력을 일관되게 복사·검증한 뒤 접수하는 등의 방식을 검토한다. 통신의 일괄 쓰기가 PLC scan과 물리 작업 전체의 원자성을 보장한다고 가정하지 않는다.

요청 번호·결과를 전원 차단 후 얼마나 보존할지, 번호 재사용과 PC 재시작을 어떻게 처리할지 정해야 한다. PLC에 결과 보존이 없으면 PC 기록만으로 물리 exactly-once를 보장할 수 없다. 응답 유실 후에는 미결 요청·잔류 명령·현재 상태를 확인하는 복구 경로가 필요하다.

기존 PLC 프로그램이 이미 제공하는 handshake가 있다면 먼저 재사용 적합성을 검토한다. 새 handshake를 개발할 필요가 있는지, OEM이 PLC 프로그램을 변경할 수 있는지도 아직 결정되지 않았다.

## 4. 제공된 도식의 적용 한계

두 번째 자료는 CC-Link를 통해 IO를 관리한다고 설명하고, CNC·핸들링 로봇·주변장치 및 사이클·문·척 등의 신호 예시를 제시한다.[^1] 그러나 그림만으로 실제 원격국이 세 개라고 확정하거나, 그 신호가 모두 구현·배선돼 있다고 기록하지 않는다. 사진의 선번도 해당 PLC 프로젝트의 논리 주소·작업 의미와 대조해야 한다.

자료의 ‘예비 접점에 배선하고 PLC 주소를 할당하면 된다’는 문장은 확장 가능성에 대한 검토 의견으로 취급한다. 추가 작업에는 미사용 여부, IO 전기적 적합성, PLC 논리, 제어권·인터록, 완료 관측, 단절 동작의 확인이 함께 필요하다.

특히 제조사 FAQ는 `AJ65SBTB1-32DTE1`의 source형 IO와 `-32DT1`의 sink형 IO를 구별한다.[^5] 모델명이 비슷하다는 이유로 같은 배선·입출력 조건을 가정하지 않는다. 공정용 통신·일반 IO handshake와 비상정지·보호 기능의 안전 경로도 구분해야 한다.

## 5. 다음에 확인할 자료

| 우선순위 | 확인 대상 | 설계에서 결정할 내용 |
|---|---|---|
| 1 | PLC 프로젝트·기존 외부 인터페이스 설명 | 재사용 가능한 요청·상태 영역과 OEM 변경 가능 범위 |
| 2 | 현재 Ethernet 연결·IP·포트·통신 설정·CPU 버전 | 내장 포트의 RX 연동 가능 여부와 지원 frame |
| 3 | CC-Link 국 구성·IO 매핑·배선표 | 실제 장치별 신호 주소·방향·극성·갱신 의미 |
| 4 | 문·척·가공 시작/완료·이상 정의 | 작업별 접수·성공·실패·접근 가능 조건 |
| 5 | 기존 로봇·PLC·작업자 제어권과 단절·재시작 동작 | 자동 처리와 개입·복귀 경계 |

그다음 작은 작업 하나를 골라 읽기 관측과 실제 상태를 대조하고, 합의된 명령·완료 경로를 검증한다. 사진만을 근거로 PLC 설정 변경, 출력 쓰기, 배선 추가 또는 운전 명령을 수행하지 않는다.

이번 확인으로 첫 설비 PLC 연동 연구의 우선 대상은 Mitsubishi MELSEC-Q가 됐다. FANUC·Siemens 연구는 회사의 다른 CNC 장비 확장에 그대로 사용한다. 공통 Runtime 계약을 바꾸기보다 Mitsubishi 어댑터와 이 레이저 설비 프로파일로 차이를 수용하는 방향이다.

## Sources

[^1]: 첫 레이저열처리 설비 PLC·CC-Link 설명 이미지 2장, 2026-09-09 내부 제공. [PLC 구성 원본 보존본](/Users/ojaehong/research_RX/research/rx_first_cell_interfaces_2026-09-09/sources/laser_plc_overview.png), [CC-Link IO 설명 보존본](/Users/ojaehong/research_RX/research/rx_first_cell_interfaces_2026-09-09/sources/laser_cclink_io.png). [원본 경로·해시·확인 범위](/Users/ojaehong/research_RX/research/rx_first_cell_interfaces_2026-09-09/laser_photo_sources.json). 임시 경로의 이미지를 변경 없이 보존했다.
[^2]: Mitsubishi Electric, [Q03UDVCPU Specifications](https://www.mitsubishielectric.com/fa/in_en/products/faspec/detail.page?formNm=QnUDVCPU_Q03UDVCPU_3827&kisyu=%2Fplcq&lang=2&popup=1), 내장 Ethernet 사양. 2026-09-09 확인.
[^3]: Mitsubishi Electric, [QnUCPU User's Manual — Communication via Built-in Ethernet Port](https://www.mitsubishielectric.com/dl/fa/document/manual/plc/sh080811eng/sh080811engy.pdf), SH-080811ENG-Y, 2026/05, §5.1, 인쇄 pp.52–54, 60–62; PDF 순번은 인쇄 +2. 접속 설정·접근 범위·frame 조건. 지원 기능과 실제 설치 설정은 구분한다.
[^4]: Mitsubishi Electric, [QJ61BT11N Specifications](https://www.mitsubishielectric.com/fa/in_en/products/faspec/detail.page?category=ex&formNm=QJ61BT11N_QJ61BT11N_3870&id=spec&kisyu=%2Fplcq&lang=2), CC-Link master/local, RS-485 사양. 2026-09-09 확인.
[^5]: Mitsubishi Electric, [Difference between AJ65SBTB1-32DTE1 and AJ65SBTB1-32DT1](https://fa-faq.mitsubishielectric.com/faq/show/23022), FAQ 23022, 2018-09-26 갱신, 2026-09-09 확인. 모델별 IO 전기적 차이.
