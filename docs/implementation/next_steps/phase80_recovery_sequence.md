# Phase80 이후 복구 구현 순서

2026-09-13. phase79의 실제 인수 결과를 바탕으로 한 구현 계획이다. 기존 공통/셀 규범을 변경하지 않는다. 전체 R01–R30을 유지하며, 아래 순서는 미구현 기능을 완료라고 표시하는 기준이 아니다.

## 출발점

phase79에서는 관리자 승인에 따른 Host 결과 조회를 연결했다. 원 native success capture를 회수해도 후조건 연속성이 끊긴 작업은 UNKNOWN/NONE/QUARANTINED다. E는 철회된 세션을 다시 만들지 않고 ATTENTION/PENDING stop·exit1을 남겼다. 이 자료는 다음 단계를 설계할 때 없애야 할 잡음이 아니라 보존할 원본이다.

## 첫 구현 단위: 오프라인 실행기 원장 점검

S 제품 실행파일에 `cell recovery-inspect CONFIG`를 연결한다. 네트워크 연결·새 E 등록·planner·장비 호출 없이 기존 서비스 소유, 설정/설치, attachment·creation marker·Run journal·stop·원 요청을 검사한다. 성공은 검토 가능한 JSON을 읽었다는 뜻이며 원 정리 요청 완료/현재 P 상태/생산 재개를 뜻하지 않는다.

현재 저장소 열기 함수에는 schema 초기화·WAL 설정 경로가 있으므로 원 DB에 그대로 쓰지 않는다. 기존 서비스와 writer lock을 생성 없이 확보하고, 고정된 DB/WAL/SHM을 제한된 임시 사본으로 읽는다. 원본 bytes·mtime과 요청/stop/attachment를 보존하며, 누락·특수파일·변경·잘못된 scope·한도 초과에서는 명시 실패한다. 실제 phase79 미완료 E 원장을 대상으로 network-none에서 두 번 읽고 결정적 결과와 원본 파일 불변, P/H/native 무변경을 대조한다.

이 단위가 끝나도 `recovery-collect`나 새 세션 등록을 실행하지 않는다. 등록에는 아래 별도 판단이 필요하다.

## 다음 경계와 순서 제약

| 경계 | 필요한 기록과 결정 | 다음으로 넘기지 않는 권한 |
|---|---|---|
| E 현재 세션 등록 후 과거 Run 조회 | 원 attachment/stop 불변, 새 peer 등록의 현재 owner·CAS/영향 범위, 현재 읽기와 과거 원문을 구별한 검토 기록 | 과거 Pause ACK, attachment 정상 종료, 원 Run 재개 |
| Host operating registration rebind | 새 명시 승인, before/reserved/confirmed resource fence, 실제 grant receipt, 전체 등록 원자 교체/이력, 실제 서비스 인수 | 기존 qualification/Arm/permit/mandate·제한 해제 |
| 조사 포기 처분 | 현재 운영 책임자의 명시 attestation, 실제 조사 절차 artifact와 저장 evidence, 원 Work/CAS, UNRESOLVED+QUARANTINED의 원자 기록 | 성공 판정·자원 RELEASED·새 생산 |
| 현재 자원 처분/현장 절차와 명시 재개 | 현재 잔류 명령·제어·지지/소재/인원·절차·qualification, 해당 epoch의 clearance, 새 RestartRun·Arm·mandate | 옛 명령 자동 재전송/과거 불명 성공 전환 |

E의 새 Session.Open은 현재 구현에서 AUTHORITY_REVOKED와 epoch/block 변경을 만든다. Host 복구/운전 등록 승인을 먼저 받은 뒤 E를 새로 등록하면 그 승인은 stale일 수 있다. 따라서 필요한 E 등록을 먼저 완료하고 그 뒤 현재 Host 문맥으로 다시 검토한다. OpenCase 등 다른 권한 변경도 같은 CAS 원칙을 적용한다.

공유 Host grant를 여러 cell Plan에 복사한 뒤 각각 갱신하면 H의 grant별 renew_seq와 P의 plan별 seq가 어긋난다. shared grant 지원에는 단일 renewal owner와 원래 sent_at·expiry 보존이 필요하다. 지원 범위를 명시하지 않고 첫 cell만 고르거나 duplicate receipt로 expiry를 늘리지 않는다.

운영 등록 재연결의 최초 양성 인수는 대상 자원에 미결 작업·격리가 없는 P-only restart가 적절하다. UNKNOWN/QUARANTINE 대상의 새 명령권 획득을 이 작은 경로의 성공 조건으로 강제하지 않는다. 조사 처분과 검증된 자원 인계를 먼저 구현해 연결할 별도 경계다. 이는 다중 셀·전체 복구 목표를 삭제하는 결정이 아니다.

## 읽기 검토 자료

- [Host 등록·grant 재연결 검토](phase80_host_rebind.md): 새 grant 예약/확정, 단일 renewal 소유, 기존 서비스 인수, 미구현 Lookup/Revoke 한계.
- [실행기 원장 회수 검토](phase80_executor_recovery.md): offline inspect와 명시 registration/collect, 원 PENDING/attachment 보존, 현재 owner CAS 공백.
- [조사 처분·개입 검토](phase80_intervention.md): 첫 T5와 자원 해제/비운전 Close/Restart를 구별하고 실제 procedure/close authority 미연결을 명시.

세 검토는 규범 문언·현재 소스·설계 제안을 구분한다. 파일 존재는 구현/시험 완료의 근거가 아니며 실제 결과는 각 단계 evidence에 연결한다. 현장 절차/신호를 가상으로 채우지 않고 첫 물리 셀은 NOT_COMMISSIONED로 유지한다.
