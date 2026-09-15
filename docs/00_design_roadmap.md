# RX의 후속 방향

기준일: 2026-09-16. 목표는 [이기종 로봇과 시설의 협업](01_product_definition.md)이다. 인계 사례의 N1 정의, N2 경계 판정, N3 문서 반례, N4 모의 명령 추적과 N5의 실제 ROS 컨트롤러·모의 하드웨어 시험을 기준으로 후속 구현·검증을 구체화한다.

## 다음 서비스 검증 제안

| 순서 | 할 일 | 확인할 결과 |
|---|---|---|
| N1 | [두 역할의 물품 인계 사례를 정의](20_first_handover_case.md) | 시작·끝·참여자·물품·자원·사람 개입과 최종 완료 조건 |
| N2 | [두 미결의 계약 경계 판정](22_open_items_boundary.md) · [선언·판정 지원도 측정](21_declaration_reuse_measurement.md) | 문서 판정 완료. 이동형 지지는 profile 규범만으로 불충분하며, 인수는 기존 기록과 추가 업무 의미를 구분했다. 두 미결은 open이고 **재사용 계수는 측정 불가**로 남는다. |
| N3 | [유실·경합·거부·인계 불명의 문서 반례 검토](23_handover_counterexamples.md) | 네 후보의 24단계·다섯 축 20개를 구체화하고 네 오독의 규범상 차단 지점과 현장 결손을 연결했다. 거부는 BUSY·오래된 permit 차단에 귀속한다. 실행한 장애 시험은 아니다. |
| N4 | [모의 명령 경로·추적 경계 구현](https://github.com/jack0682/rx-solutions/blob/df3b7416b71acc9cdfbd7a75b0658f88effb889f/examples/process/n1-handover/README.md) | 두 Host의 네 동작이 컴파일되고 모의 입력으로 실제 planner를 실행했다. 성공 뒤 명령 자원 인계를 기다리며, 해제 응답 불명은 원 operation을 보존하고 후퇴를 막는다. 구체 모의 값 8/77, 미충족 69(placeholder만 2 포함). P/Host의 N1 실행·물리 인계·정상 인수·잔여 점유·서비스 완료 검증은 남고 두 미결은 open, NOT_COMMISSIONED다. |
| N5 | [실제 ROS JTC·모의 하드웨어 연결 검증](https://github.com/jack0682/rx-solutions/blob/2548a93c854878c192bc0643e1f326a2a9039b2f/native/ros-jtc/controller_validation/README.md) | GenericSystem 모의 하드웨어에서 goal 수락·결과·UUID 취소·브리지 재시작 후 조회를 실측했다. N5 입력 18/77, N4 대비 추가 대응 ID 15개이며 합집합은 별도 산출물의 가용성이다. 실제 Authority·물리 지지·현장 검증과 N1 실행은 남는다. NOT_PERFORMED·SIMULATION_FIXTURE·NOT_COMMISSIONED 유지. |
| N6 | 여러 작업과 운영 영역으로 확장 | 공유 자원·신뢰·통신 단절·성능 요구의 추가 정의 |

N1–N6는 순서 제안이며 장비·일정·성능 수치를 확정한 계획이 아니다. 먼저 모든 도시 기능을 만들 필요는 없다. 현재 미결 중 선택한 사례에 실제로 영향을 주는 항목을 [미결 목록](implementation/critical_open_items.md)에서 연결한다.

## 설계 판단의 기준

목적과 우선순위는 01, 평가 가설은 [02](02_value_and_business.md), 현재와 목표의 범위는 [03](03_product_scope.md)를 따른다. 작업 의미와 권한은 규범의 명시된 버전 범위를 따른다. 구현·시험은 해당 commit과 증거로 판단한다.

이전 산업 초안의 로드맵과 실행 기록은 [고정 원문](../references/README.md)에 남아 있다. 과거 납품 순서·특정 장비 선택을 현재 모든 연구의 선행 조건으로 삼지 않는다.
