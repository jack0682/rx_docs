# RX 초안 v0.1 — 핵심 미결 항목

2026-09-13. 초안을 마감하면서 다음 착수 때 결정할 항목을 모았다. 우선순위는 **실장비 파일럿을 막는 영향**을 기준으로 하며, 이번 초안에서 모두 구현하겠다는 새 계획이 아니다. 실제 담당자는 미지정이며 아래는 책임 영역이다.

## 우선순위와 종료 조건

| ID·우선순위 | 미결과 현재 사실 | 필요한 결정·다음 최소 확인 | 책임 영역·완료 근거 |
|---|---|---|---|
| O01 · 최우선 | **실제 Authority Provider.** JTC 계약·bridge·native journal은 있지만 제품 factory는 Provider 미설정으로 run을 거부한다. P의 procedure/close authority도 별도 미연결이다. | OMY 세부 모델을 고정하고 controller 관측·실제 command 독점·현지 조건/지지·종료 책임과 원천을 분리. 모델/제어기 세대와 우회 입력을 어떻게 검출·배제할지 결정. | 장비 연동·플랫폼. 실제 source/time/generation/owner 근거와 외부 goal/재load/reboot/종료 반례, 최종 product factory 인수. bool/READY 대입으로 통과시키지 않음. |
| O02 · 최우선 | **첫 셀과 실물 인수 입력.** 레이저 Q03UDVCPU는 확인됐으나 정확한 로봇 구성·그리퍼/지그·신호/극성·PLC 논리·개입·초기/종료 상태는 미확정이다. | 실제 소재 공급의 구간, CNC/레이저와 RX 책임, 완료·지지·잔류 명령·통신 상실 반응, 사람 개입 범위를 정함. | 공정·기구·전장·장비 담당. 실제 signal/profile/교정·위험 검토와 현장 FAT/SAT. 현재 NOT_COMMISSIONED 유지. |
| O03 · 파일럿 전 | **UNKNOWN 조사·처분·현장 절차.** 조회된 capture와 전체 작업 성공은 다르다. 조사 포기 T5는 phase81 WIP이며 초안에 미포함. 제품 procedure/close 신뢰 공급도 없다. | 운영 책임자·조사 절차/서명·human attestation, UNRESOLVED 처분과 검증된 자원 해제를 구분. 무진입 조사에 가짜 현장 작업 기록을 만들지 않음. | 운영·품질·플랫폼. 원 evidence/actor/CAS·원자 회수·격리 보존, 실제 procedure admission과 별도 처분 검증. |
| O04 · 파일럿 전 | **새 운전 등록·명시적 재개·복원.** RECOVERY_ONLY와 offline inspect 이후 E/Host operating rebind·새 자격/Arm/mandate·Run 재개는 미완료다. | E 새 등록의 epoch 변경 순서/CAS, Host 새 grant와 단일 renewal 소유, old attachment/stop 인계, source/Host 교체와 백업 복원의 구별. | 플랫폼·실행기·장비 연동. 원 요청/예산/격리 보존, 실제 재시작·부분 실패·복원·명시적 새 시작. 현재 E1/P2 attention을 숨기지 않음. |
| O05 · 파일럿 전 | **자사 기본 지원과 배포 조합의 실증.** 필수5개 source와 전이 의존성 포함은 확인했지만 모델별 실제 backend/control provider·교정·lifecycle·OS/CPU/GPU 조합 전체를 인수하지 않았다. | 첫 지원 모델/모드/버전을 고정하고 각 조합의 지원 등급과 필수 의존/라이선스·설치 방식을 확정. OMY arm6관절과 follower/gripper 구성을 혼합하지 않음. | 자사 플랫폼·릴리스. 모델/firmware/SDK/ROS/OS/CPU별 실제 지원표와 설치·업데이트·정상 종료 증거. 자사 의무를 선택 모듈로 낮추지 않음. |
| O06 · 운영 제품화 | **운영·편집·관리의 미연결 구간.** 기본 UI/API는 있지만 전체 시각 편집·비교·관리 화면·공개 wire 경로·계정/단말 관리·외부 UI 패널 등이 부분이다. 고주기 stream·외부 UI 패널은 OPEN. | 첫 고객에게 필요한 역할별 완료 흐름과 선택적 확장을 나눔. 초기 범위 밖 기능을 플랫폼의 필수 기반으로 계속 선행 개발하지 않음. | 앱·플랫폼·솔루션. 실제 역할별 end-to-end 시나리오, 오류/접근권/버전 변경 검증. |
| O07 · 운영 제품화 | **장기 운영·저장·진단·전체 종료의 한계.** 빈 publish의 감사 기록 비용, 부하/보존/장기 운전·다중 셀·전체 복원 검증이 부족하다. WAL 점검도 제한된 범위다. | 운영 기간·Host 수·보존량·장애 모델과 지원 가능한 복원 절차를 수치로 정함. 현재 unsupported/attention 경계를 명시. | 플랫폼·운영·검증. 실제 부하/장시간/저장 장애/복원·지원 진단 시험. 일부 정상 WAL tail 거부와 전체 rollback 탐지 한계를 유지. |
| O08 · 사업 파일럿 | **고객 효과·납품/지원 공수.** 인건비 절감이 목적이지만 실제 노동 투입·개입·원가·절감액·수익성은 미측정이다. R29는 OPEN. | 자동화 전후 작업자 투입, 보충/검사/감시/복구/정비, 공급 대기와 납품·보증·지원 비용의 측정 범위·책임·인수 조건 합의. | 사업·생산기술·현장 운영. 실제 관측과 비교 가능한 기준 수량/품목·기여이익. 가공 시간을 노동시간으로 환산하지 않음. |

## Authority Provider를 먼저 다뤄야 하는 이유

현재 가장 큰 간극은 RX 내부의 규율보다 **그 규율에 실제 장비 근거를 공급하는 연결**이다. controller가 active이고 ROS service가 보인다는 사실은 명령 소유자가 하나라는 증거가 아니다. bridge 종료와 DHI/하드웨어 종료도 같은 동작이 아니다.

[재검토 원문](../../references/draft_closure/authority_provider_reassessment.md)은 고정 SDK/DHI/open_manipulator 소스에서 얻을 수 있는 관측과 증명하지 못하는 것을 대조한다. 최소 검토 제안은 ControllerObservation, CommandOwnership, LocalConditionsAndLifecycle 및 별도 Protection 책임의 구분이다. 이것을 새 거대 프레임워크로 확정한 것은 아니다. 기존 인터페이스를 유지하더라도 각 사실의 source·generation·취득 구간·미확인 상태와 책임이 명확해야 한다.

P의 qualification 서명 검증은 위 현지 command ownership Provider와 별개의 문제다. 서명된 절차/공정의 적합성 승인, P의 작업 허가, 현지 독점 제어와 물리 상태 확인을 한 “Authority=true”로 합치지 않는다.

## 후속 착수에 필요한 결정 묶음

다음 개발은 O01/O02의 실제 연결 범위를 먼저 확인한 후, 필요한 O03/O04의 운영 복귀 흐름을 선택하는 것이 현재 권고다. 후속 계획은 [복구 순서 검토](next_steps/phase80_recovery_sequence.md)에 있으며 그대로 구현을 재개하라는 지시는 아니다.

초안 종료 시 유지하는 전체 제품 요구는 [R01–R30 추적표](requirements.md)다. 상태는 PARTIAL26·OPEN3(R12/R21/R29)·FIELD_BLOCKED1(R30)이며 전체 VERIFIED로 승격한 항목은 없다. 미결을 숨기거나 삭제하지 않았고, 그 전부를 이번 초안 종료의 선행 작업으로 확장하지도 않았다.
