# 0F 레이저 셀의 버전 있는 데이터 모델

2026-10-01. 이 문서를 갱신하며 모델·API·CLI 우선 세로 경로를 추적한다. 현재는 **M1 로컬 사전 검증 통과·통합 검증 중**이며
사용자 수락·게시·운영·RC 완료를 뜻하지 않는다. [WF 요구](../46_workflow_product_experience.md),
[전체 계획](framework_delivery_plan.md), [코어 헌장](../43_core_charter.md), RF 원장은 변경하지 않는다.

## 범위와 단계

M1은 패키지 적용 → Type/Model/Instance 조회 → 상속/덮어쓰기 출처 → 서버의 슬롯 좌표 계산 →
새 모델을 데이터만 추가 → 같은 API 결과의 UI 표시다. 사용자가 직접 실행해 수락한 뒤 M2의
Task 실행값 해석·제약, M3의 Preview·게시·runtime binding·모의 운전/UNKNOWN 복구를 진행한다.
최종 RC의 Linux 재현 45분, 새 품목/트레이 데이터 추가 10분은 아직 측정하지 않았다.

## 현장 근거와 모의 값

Solutions의 `examples/process/laser-heat-treatment/tooling-reference.json`에는 실제 공정의
ECC_51/ECC_99/CVR_F/FLANGE_L/FLANGE_R 명칭, 14/17형 구분과 지그 대응이 있다.
14/17은 식별자이며 mm 치수가 아니다. 치수·중량·힘·TCP·위치는 원본에서 미정이다.
이번 데이터는 ECC_51-14와 ECC_99-14의 명칭/지그 대응을 근거로 삼고, 수치가 필요한 모든 모델과
인스턴스는 **SIMULATION**으로 표시한다. 모의 수치를 실측값으로 승격하지 않는다.

패키지는 Property, 상속 Type, Model, Instance, 품목별 Property Set, 위치 생성 규칙을 제공한다.
트레이의 높이·너비·행·열·피치·깊이·원점·좌표계, 품목의 치수·중량·허용 힘,
척/지그·단일 그리퍼·문·pick/place station의 선언을 데이터로 둔다.
장비 주소나 실제 동작 권한을 부여하지 않는다. 누락값은 누락으로 반환한다.

## 공통 저장과 계산 계약

- 기존 definition-catalog WIP의 카탈로그 ACL, 단일 writer, CAS, 원 요청 복구,
  불변 `catalog/id/revision/digest`, Property→Type→Model→Instance 상속을 재사용한다.
- 속성은 한 번 정의한 Property를 참조한다. 값의 타입·단위·범위와 출처는 서버가 검사하고 반환한다.
  Instance에는 현장 변경값만 저장하며 Model r2 생성으로 기존 r1 참조를 자동 변경하지 않는다.
- CLI 패키지는 순서 있는 정의 목록과 로컬 참조를 갖는다. CLI는 서버가 반환한 정확한 참조를
  후속 요청에 연결할 뿐 상속·좌표·실행값을 계산하지 않는다. 각 저장은 기존 원 요청/CAS 경로다.
  전체 패키지가 단일 transaction이라는 주장은 하지 않는다. 중단 시 적용된 정의와 미적용 정의를
  구분하고 동일 요청으로 이어간다. 이 단계의 패키지 적용은 저작 자료의 적용이며 실행 패키지 게시가 아니다.
- M1의 위치 생성은 버전 있는 **유한 Cartesian point pattern** 규칙이다. 규칙 데이터가 대상
  Resource Type, 원점·자세·좌표계 필드, 축별 개수·피치 필드와 로컬 방향을 지정한다.
  서버는 `원점 + R(q) × Σ(축 index × pitch × direction)`을 계산한다.
  q는 명시된 unitless 단위 quaternion `[x,y,z,w]`이며 출력 자세에도 보존한다.
  자세가 누락되거나 단위 quaternion이 아니면 오류이며 identity 회전을 추정하지 않는다. 마지막 축이 가장 빠르게 변한다.
  트레이/품목 이름·특정 행열 수·실측값은 알고리즘에 넣지 않는다.
- 원점/피치는 명시된 동일 길이 단위, 축 개수는 양의 정수/unitless, 방향은 단위 벡터를 요구한다.
  누락·단위 불일치·유한성·타입 불일치·과대 개수는 위치를 포함한 오류다. 좌표계를 추정하지 않는다.
  최대 100,000점, 페이지 최대 100점으로 제한하고 정확한 대상/규칙 revision을 페이지마다 고정한다.
- 결과는 대상·규칙 참조, 입력값과 출처, 총 개수, 각 index/축 index/좌표·단위·좌표계 및
  위치 있는 오류를 반환한다. UI는 이 서버 응답을 표시하며 자체 좌표 계산이나 별도 정의 저장소를 두지 않는다.

기존 process-source.v1·실행 wire·원장/인계 의미를 변경하지 않는다. 신규 저작 API와 정의 종류는
현재 미통합 WIP를 기반으로 추가하며 구버전 소비자에게 기존 형식을 다른 의미로 반환하지 않는다.
기존 계약 파괴가 필요해지면 v1.1 영향과 권고를 먼저 사용자에게 보고한다.

## 구현 책임과 검증

Docs는 이 모델과 범위, Platform은 범용 정의/패턴·서버 검사/조회, Solutions는 생성 SDK·기존 `rx`
CLI 클라이언트·셀 패키지·기존 Definitions 화면을 맡는다. 시나리오 전용 코어 코드 0줄을 유지한다.
별도 definition-catalog WIP는 재사용하되 R7·재자격 WIP는 흡수하지 않는다.

M1 검증은 다음을 실행한 근거로만 갱신한다: 모델/인스턴스 상속·덮어쓰기/버전 고정, 새 모델의 데이터
적용, 고밀도 슬롯 전체 페이지/경계, 타입/단위/누락/상한 오류, 권한 격리, 응답 유실 후 원 요청
복구, CLI와 UI의 같은 서버 결과, 서버 재시작 뒤 재조회. 먼저 API·CLI를 구현·검증하고 UI를 연결한다.
사용자가 실행할 정확한 명령과 UI 순서는 검증 후 이 문서에 기록한다.

현재 제품 실행·사용자 수락은 미완이며 코어 변경량/패키지 작성량·설치 시간은 최종 소스로 측정한다.

## M1 첫 구현 체크포인트

2026-10-01. 기존 definition-catalog 브랜치에서 범용 PointPattern 정의·입력 검사·출처를 포함한
페이지 조회 API를 추가했다. 기존 `rx`에 definitions apply/show/points를 연결하고 셀의 모의 정의
54개와 새 트레이 모델 데이터 예시를 작성했다. 이 변경은 아직 코드 PR 통합 전이었다.

API crate의 all-targets check와 개발 API binary build는 통과했다. 카탈로그 대상 시험 7개가
통과했으며, 추가 시험은 고밀도 모델 2,400점의 전체 페이지·마지막 좌표, 상속/덮어쓰기 출처,
새 모델 15점 생성, 과거 revision 보존, 누락·비정수 개수·단위·digest·페이지 범위·카탈로그 격리를
대조했다. 전체 workspace·Linux 설치·UI·Preview·운영 근거는 아니다.

실제 CLI 적용은 개발 API 로그인에서 HTTP 403으로 두 번 거절됐다. 패키지 저장 전에 실패했고,
사용자의 동일 문제 두 번 중단 조건에 따라 인계한다. 서버 Host 정책과 CLI의 transport/public-origin
구성이 어긋난 것으로 정적 분석했다. urllib는 unredirected header를 우선하므로 뒤늦은 일반 Host
header 지정이 이를 교체하지 못한다. 이 시점에는 수정 후 실행을 하지 않았다.
다음 한 단계는 서버 정책을 유지한 채 CLI 개발 transport를 수정·검증하는 것이다.
M1 사용자 실행 준비·SDK 동기화·UI 연결·사용자 수락은 계속 미완이다.


## M1 API·CLI·UI 사전 검증

동일한 2026-10-01 후속 작업에서 Host 헤더 문제를 수정했다. 공개 host/origin과 실제 연결 주소를
구분하며 서버 ingress 정책과 TLS Terminal 경계를 유지한다. urllib의 실제 header 우선순위를
재현하는 테스트와 새 API 설치의 실제 요청이 통과했다.

- Platform 소스: `aee48699acd879c8f6bf84dd38c994909a7d7d66`.
- Solutions 소스: `dca80d659f5b2fa036fa3eb49ea3d23cafa18a8e`.
- [셀 패키지와 CLI 순서](https://github.com/jack0682/rx-solutions/blob/dca80d659f5b2fa036fa3eb49ea3d23cafa18a8e/examples/definitions/0f-laser-simulation/README.md).
- [API 실행 검증 결과](../../references/cell_model_m1_2026-10-01/api-acceptance.json).
- [CLI와 UI의 동일 revision·행 대조](../../references/cell_model_m1_2026-10-01/ui-cli-match.json).

셀 패키지는 58개 정의이며 0F 품목 ECC_51-14/ECC_99-14, 일반/고밀도 트레이,
척, PART1/14 지그, 단일 그리퍼, 문, pick/place station과 품목별 Property Set을 제공한다.
Task 실행값 해석과 장비 운전은 포함하지 않았다. 일반 트레이 24점, 고밀도 2,400점,
별도 JSON으로 추가한 새 모델 15점을 같은 서버 규칙으로 생성했다.

실제 새 SQLite/API 프로세스에서 전체 데이터 적용·같은 요청 재적용·상속과 덮어쓰기 출처,
고밀도 전 페이지·회전된 모델·잘못된 quaternion 거절·digest 변조 거절을 확인했다.
실제 서버 commit 뒤 클라이언트에 응답 유실을 주입하고 동일 요청으로 revision 하나를 복구했다.
서버 프로세스를 종료·재시작한 뒤 같은 pinned pose report가 바이트 의미상 일치했다.
장비/executor 결함 주입과 UNKNOWN 복구(M3)는 아직 수행하지 않았다.

기존 Definitions 화면에서 CLI 자료를 열고 별도 검증용 인스턴스의 원점과 높이를 수정·저장했다.
서버가 만든 r2의 24개 좌표를 CLI 응답과 전부 대조했고, 좌표계·quaternion·주체/규칙 revision이
일치했다. UI는 API 결과를 표시하며 자체 좌표 계산을 추가하지 않았다.

현재 로컬 검사: P 전체 workspace 541 passed / 0 failed / 19 ignored 및 Clippy 통과;
S UI 68시험·번들 3시험·타입/format/build 통과; 정의 CLI 4시험·기존 runtime CLI 8시험 통과;
생성 SDK 133파일 원본 일치와 저장소/계약/불변식 참조/경계 검사를 확인했다.
19개 제외 시험, Linux CI 결과, 최종 RC 설치와 사용자 수락을 이 로컬 결과로 대신하지 않는다.

공통 코어에 추가한 것은 카탈로그 ACL·불변 정의/참조 저장·타입 상속/값 출처·유한 Cartesian pose
규칙과 조회다. 트레이·척·품목 이름/치수/작업 순서에 따른 분기는 없으며 셀 자료는 S 패키지에 둔다.
기존 Definitions WIP를 재사용했고 이번 작업에서 새 시각 디자인·CSS 개선을 하지 않았다.
WF/RF 장기 항목은 완료로 표시하지 않는다. 사용자 M1 수락 전 M2를 시작하지 않는다.
