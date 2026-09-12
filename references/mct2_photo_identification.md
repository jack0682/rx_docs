# RX MCT-2 사진 판독 기록 v0.1

## 자료의 범위

2026-09-09 제공된 사진 중 **PLC01–04는 MCT-2이고, HMI는 다른 장비 사진**으로 확인됐다. HMI 사진의 실제 장비명은 미확인이다. 기존 장비현황 표의 MCT-2는 DMG MORI / SIEMENS로 기재돼 있으며, PLC01의 Siemens SINUMERIK 표기와 일치한다. FANUC HMI는 MCT-2 프로파일에서 제외한다.

## 사진별 확인

| 사진 | 직접 읽히는 내용 | 판독 결과와 한계 |
|---|---|---|
| HMI — 다른 장비 | 상단 `Series 31i-MODEL B`, CNC 좌표·프로그램 화면 | FANUC 31i-MODEL B 계열 표기. MCT-2가 아니며 실제 장비명은 미확인 |
| PLC01 | 왼쪽 `SIEMENS SINUMERIK`, 전면 `PN/IE X127 P1`; 오른쪽 `SINAMICS`, LINE/SPINDLE/SERVO 단자 표기 | CNC 제어부와 드라이브 구성이 보인다. 정확한 NCU·드라이브 주문번호와 firmware는 읽히지 않음 |
| PLC02 | `DMG`, L1/L2/L3, 하단 +/− 표기 | 전원 공급 장치로 보인다. 정확한 모델·정격 미확정이며 PLC CPU로 분류할 근거 없음 |
| PLC03 | `IM151 HIGH FEATURE`, 다수의 `8 DI`, `8 DO`, `PM-E`, 노란 `PROFIsafe 4F-DI/3F-DO DC24V/2A` 모듈 | 일반 입출력과 안전 관련 입출력 모듈의 존재를 확인. 각 채널의 문·척·센서 대응은 미확정 |
| PLC04 | `SIEMENS SIRIUS`, `PHOENIX CONTACT`, 두 녹색 모듈의 `max. 2,4 A` 표기 | 주변 전력·제어 부품이 보인다. 회로의 기능과 연결 대상은 사진만으로 확정하지 않음 |

HMI의 모델 계열은 [FANUC 공식 제품 페이지](https://www.fanucamerica.com/products/series/30i-31i-32i-model-b)와 대조했다. PLC03의 노란 모듈에는 `6ES7 138-4FC01-0AB0`로 읽히는 주문번호가 있고, [Siemens 공식 데이터시트](https://support.industry.siemens.com/teddatasheet/?caller=SIOS&format=pdf&language=en&mlfbs=6ES7138-4FC01-0AB0)는 해당 부품을 ET200S PROFIsafe 입출력 모듈로 분류한다. 현장 장착 부품과 주문번호의 최종 일치는 장비 목록으로 확인한다.

PLC01의 외형·포트 배치는 SINUMERIK NCU와 SINAMICS S120 Combi 구성의 후보를 검토할 근거다. 그러나 [Siemens S120 Combi 매뉴얼, 07/2021, p.30](https://cache.industry.siemens.com/dl/files/046/109800046/att_1074289/v1/s120_combi_man_0721_en-US.pdf)은 여러 제어기 조합을 다룬다. 사진의 외형만으로 840D sl·NCU 세부 모델이나 설치 소프트웨어를 확정하지 않는다.

## 현재 확정하지 않는 항목

- MCT-2에서 제외된 HMI 사진의 실제 장비명.
- MCT-2의 정확한 CNC/NCU·PLC CPU 모델, 소프트웨어 버전과 설치 옵션.
- OPC UA·FOCAS 등 외부 API의 활성화·라이선스·권한과 실제 접속 endpoint.
- 문·척·소재 감지의 IO 주소·극성·완료 조건 및 OEM 제어 프로그램.
- PROFIsafe 모듈이 담당하는 실제 안전 기능·배선·검증 상태.

포트의 존재는 RX 연결 허가나 API 지원을 뜻하지 않는다. LED의 순간 상태도 장비 전체의 정상·안전·가공 완료 판정으로 사용하지 않는다. 사진의 NC 프로그램과 좌표는 관측 자료이며 RX 동작 절차로 전용하지 않는다.

## RX 설계에 반영할 내용

MCT-2 프로파일에는 CNC 제어부, 드라이브, 일반 IO, 안전 관련 IO를 구분해 기록한다. 사진 파일명에 PLC가 붙어 있더라도 모든 부품을 PLC CPU로 취급하지 않는다. 실제 장비 측 작업 인터페이스는 OEM이 제공한 제어 경로와 신호표에서 정한다.

MCT-2의 다음 확인 우선순위는 CNC/NCU 주문번호·버전, 외부 연동 옵션, 문·척·가공 완료 신호표다. 첫 레이저열처리 설비의 제어기 정보에는 이번 MCT-2 사진을 적용하지 않는다.

## 원본 출처

1. [HMI — 다른 장비, MCT-2에서 제외](</Users/ojaehong/Downloads/3번장비 HMI.jpeg>)
2. [PLC01](</Users/ojaehong/Downloads/3번장비 PLC01.jpeg>)
3. [PLC02](</Users/ojaehong/Downloads/3번장비 PLC02.jpeg>)
4. [PLC03](</Users/ojaehong/Downloads/3번장비 PLC03.jpeg>)
5. [PLC04](</Users/ojaehong/Downloads/3번장비 PLC04.jpeg>)

원본 경로·해시·장비 분류와 대응 확인 상태는 [사진 출처 기록](/Users/ojaehong/research_RX/research/rx_first_cell_interfaces_2026-09-09/mct2_photo_sources.json)에 보존한다. 이미지 원본은 수정하지 않았다. 본 문서는 사진 판독과 자료 대조 기록이며 현장 접속·동작 시험 결과가 아니다.

분류 정정 근거: 2026-09-09 내부 확인 답변 ‘HMI는 다른 장비 사진’. 파일명과 최초 일괄 분류보다 이 정정 내용을 우선한다.
