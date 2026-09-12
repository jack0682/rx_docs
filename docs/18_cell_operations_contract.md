# 셀 운영 계약 기준판 v1.0

2026-09-10 · 설계 기준판. [전체 계약](cell_operations/v1.0/README.md) · [조사·선택 근거](../references/cell_operation_research_2026-09-10/research_and_decisions.md)

RX의 셀 운영 계약은 **검증한 사용 범위 안에서 자동 운전을 이어가고, 조건 상실·사람 개입·변경이 생기면 관련 작업을 제한하며, 근거를 확인한 뒤 다시 시작하는 규칙**이다.

## 확정한 규칙

| 구분 | 결정 |
|---|---|
| 운전 조건 | 장비/tool/지그/소재/모드/환경의 검증 범위와 현재 조건을 구별. 필요한 값의 미확인은 허용으로 바꾸지 않음 |
| 정상 자동 실행 | 범위·예산이 있는 RunMandate 안에서 연속 실행. 소재 시도와 여러 node activation을 구별 |
| 작업 전달 | 매 operation은 내용·Host·epoch·조건에 결합된 1회 permit와 Host의 최종 gate를 통과 |
| 일시 보류 | 정상 대기·단순 응답 유실은 연속성과 원 결과를 확인하면 기존 run을 이어갈 수 있음 |
| 철회·재시작 | 사람 개입·안전정지·세대/구성 변경 등은 이전 mandate를 철회. 새 epoch에서 재확인·clearance 후 새로운 시작 의도 |
| 소재 지지 | 그리퍼/척 공동 지지를 표현하고, 같은 소재의 양쪽 해제를 공통 자원으로 충돌 처리 |
| 개입·복구 | 알림 확인·접근 절차·수동 조치·재확인·처분·재시작을 구별. 복구 step도 유일 ID와 guard를 적용 |
| 변경·퇴역 | 검증 의존 관계를 재검토. 재시작하지 않고 종료하는 경우에도 out-of-service 제한 유지 |
| 실제 보호 기능 | RX의 GOOD·DB 기록·Arm ack가 물리 정지/지지/접근 안전을 보장하지 않음. 필요한 기능 경로·성능은 별도 할당·검증 |

## 구현으로 연결되는 범위

공통 `rx.contract.v1`은 유지하고, 셀 정책을 `rx.cell.v1` extension으로 정의했다. 두 계약을 지원하는 platform/solutions 조합만 사용하며 기존 직접 쓰기 API로 셀 허가를 우회할 수 없게 한다. 세 번째 레포·컨테이너를 추가하는 결정은 없다. 자사 필수 플랫폼 전체의 지원 의무도 유지한다.

첫 레이저 셀의 실제 로봇·tool/지그·신호·개입 절차·안전기능 성능은 아직 미확정이다. 현재 commissioning 상태는 NOT_COMMISSIONED이며, 누락한 값이 있는 상태에서 운전/접근 허가를 발급하지 않는 규칙까지 계약에 포함했다. 코드·실물 운전은 수행하지 않았다.

## 문서와 검증

[28개 문서 trace와 요구별 감사](cell_operations/v1.0/05_validation_audit.md), [독립 문서 검토](cell_operations/v1.0/review_record.md), [manifest](cell_operations/v1.0/protocol_manifest.json)를 함께 관리한다. 여기의 검토는 설계 정합성 검토이며 후속 구현·실물·기능안전 검증 OV01–OV11을 대신하지 않는다.
