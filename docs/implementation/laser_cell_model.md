# 0F 레이저 셀의 버전 있는 데이터 모델

2026-10-02. **M1 사용자 수락 완료, M2 로컬 사전 검증 통과·통합 검증 중**이다.
M2 사용자 수락·게시·운영·RC 완료를 뜻하지 않는다. [WF 요구](../46_workflow_product_experience.md),
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

## M1 사용자 수락과 M2 전 보완

2026-10-01 사용자가 M1 정상 동작을 직접 확인했다. 사용자 보고는 CLI apply 재적용의
idempotence, supply 24 / dense 2400 / my-tray 20, UI Calculate points와의 결과 일치다.
이는 M1 수락이며 M2/M3·최종 RC 수락을 뜻하지 않는다.

사용자는 다음 세 항목을 M2 전 검토 대상으로 지정했다.

1. **높이의 의미.** 현 PointPattern은 `origin + R(q) × offset`만 사용하며 legacy
   `surface_height`는 계산 입력이 아니다. 기본 모델의 origin.z=0 / surface_height=900은
   두 값의 관계가 정의되지 않은 공백을 보여준다. M2의 새 해석에서는 슬롯 기준면 pose를
   위치의 원본으로 삼고 슬롯별 표면 위치를 여기서 파생한다. 독립 측정 높이가 필요하면
   동일 frame/unit과 허용 오차를 명시한 제약으로 대조한다. 기울어진 트레이에서 모든 슬롯에
   동일한 world-z를 강제하지 않는다. 부품 높이·깊이·접근 여유를 적용할 기준점과 로컬 방향도
   Task 계약으로 명시해야 한다. 기존 M1 저장본·규칙·출력은 소급 변경하지 않는다.
2. **읽을 수 있는 출처.** UI는 UUID 대신 정확한 참조 revision의 label과 revision을 표시하고
   원 UUID/catalog/digest는 세부정보로 보존한다. 최신 label을 과거 참조의 이름으로 사용하지 않는다.
   key는 현재 CLI 패키지의 별칭이므로 서버의 전역 식별자로 가장하지 않는다. CLI는 선택적
   `--format text`에서 alias/label과 출처를 표시하며 기본 JSON과 원 참조는 유지한다.
3. **생성 충돌 진단.** expected=null은 create-only이며 기존 ID에 대한 새 요청은 거절해야 한다.
   STALE_REVISION 뒤 동일 권한의 현재 조회로 존재/현재 revision을 확인하여 원인을 보충한다.
   이 조회는 거절 당시의 원자적 snapshot이 아니므로 'current read'로 표시한다. 조회를 못 하면
   원래 오류를 유지하며 원인을 추정하지 않는다. 자동 upsert·expected 교체·재시도를 하지 않는다.
   원 응답이 불명인 요청의 복구 의미와 동일 요청 idempotence도 유지한다.

②③은 기존 API의 클라이언트 표시·진단 보완이다. 공개 응답 형태, 코어/SDK, 기존 저장본의 의미를
변경하지 않는다. ①의 실제 파생 계산·정합 제약은 M2 구현에 남으며 문서 결정만으로 완료 처리하지 않는다.

## M2 구현 경계 — 버전 있는 Workflow 모델과 해석 보고서

2026-10-02, 로컬 사전 검증 완료·통합 중. 기존 M1 Definition/PointPattern JSON과 API는 그대로 유지한다.
M2는 같은 카탈로그 권한·writer 위에 별도의 versioned Workflow 모델을 추가한다. 기존 Task
선언을 실행 계약으로 소급 해석하지 않는다. 새 모델은 명시적인 schema로 Task 계약·규칙·제약과
순서 있는 node→Task 참조를 저장한다. 각 member의 신원은 Workflow의 정확한 revision/digest와
member ID로 고정한다. 다른 규칙을 수정해도 기존 Workflow revision의 member는 변하지 않는다.

- Task 계약: 사용 context 슬롯/허용 type/단일·다중, Property Registry 참조와 순서 있는 source
  chain, required capability, Skill→primitive/parameter mapping, timeout 속성, done 관측 계약,
  알려진 실패의 stop과 UNKNOWN의 hold/reconcile 정책. 지원·완료 관측은 선언이며 실제 권한이 아니다.
- 규칙: 이름 있는 유한 DAG. field/property/rule lookup, 같은 단위의 덧셈·뺄셈·min/max,
  unitless 배율, vector 성분, 명시된 quaternion을 따르는 pose offset만 지원한다.
  임의 스크립트·네트워크·시간·수식 문자열 평가는 없다. cycle·복잡도 초과는 오류다.
- 값: 단위와 scalar/vector/text/bool을 구별한다. 수치 구간은 min/max를 유지하고 제약은
  가장 불리한 조합으로 검사한다. 제공된 잘못된 Override/입력을 낮은 우선순위 값으로 덮지 않는다.
- 출처: 선택된 source tier, 정확한 정의/Workflow/member 참조, 사용한 입력과 규칙을 보존한다.
  제약은 Override 선택 이후 검사하고 node/property 위치와 이유를 반환한다.
- 슬롯 위치·표면 z는 M1의 full pose에서 얻는다. 접근은 선언한 로컬 방향과 part/clearance로
  계산하고 그 결과의 z를 읽는다. legacy surface_height를 추가 offset이나 실행값 원본으로 쓰지 않는다.
- M2 해석 요청은 선택한 part/model·resource·property set·Override·실행 입력과 slot index를
  고정한다. 한 부품의 모든 node 값을 해석한다. N개 부품의 순서·runtime binding·실행은 M3에서
  각 부품의 동일한 해석 경로와 원 보고서 참조로 연결한다.

새 `/api/v1/workflow-models`, `/api/v1/workflow-model`은 원 요청/CAS/불변 revision으로 모델을
저장·조회한다. `/api/v1/workflow-resolutions`는 권한을 확인한 정확한 자료로 계산하고 immutable
보고서를 저장하며, `/api/v1/workflow-resolution`은 같은 보고서를 조회한다. 새 자료는 별도 record
schema/index를 사용하여 M1 목록·decoder에 새 enum/필드를 섞지 않는다. 카탈로그 권한·원장·DB를
따로 만들지 않는다. 모든 CLI/UI는 이 API를 사용한다. M2 사전 검증 근거는 아래에 제한하며 사용자 수락을 대신하지 않는다.

## M2 데이터와 사전 검증

M1 58개 정의를 보존하고 M2 정의 46개를 추가했다. Workflow 데이터는 Task 8개, 규칙 23개,
제약 23개이며 pick→load→clamp→close-door→process→open-door→unload→place를 선언한다.
타입·속성·품목·트레이·지그·그리퍼·기계 이름과 수치는 Solutions 패키지에만 있다. Platform은
자료 조회·단위/타입/frame 검사·유한 규칙 해석·구간 제약·권한/불변 보고서 저장만 제공한다.
레이저 전용 코어 분기는 추가하지 않았다. 기존 Normative v1.1 계약의 의미·해시는 변경하지 않았다.

### 슬롯 높이와 접촉 기준

새 M2 트레이 Type은 legacy surface_height를 포함하지 않는다. Model은 TRAY_LOCAL의 슬롯
입구 원점 [0,0,0]과 형상을, Instance는 world frame·origin·orientation을 함께 선언한다.
슬롯 입구 pose를 위치 원본으로 삼으며 z는 파생 성분이다. 지그 표면은 지그 원점에서 명시한
로컬 법선 방향으로 지그 높이만큼 이동한다. 별도 독립 높이 측정값은 이번 데이터에 없다.

접촉 위치는 모의 부품 중심을 datum으로 하여 `입구 + 법선 × (부품 높이/2 - 안착 깊이)`,
접근 위치는 `입구 + 법선 × (부품 높이 - 안착 깊이 + clearance)`다. 실측 TCP·기하 적합성·충돌
검증을 뜻하지 않는다. 힘/폭/질량·피치·트레이/지그 크기·안착 깊이·planning frame·동작 시간·지그
family 제약은 Override 적용 후 평가한다. 범위 연산은 외향 반올림하고 독립 최악 조합으로 검사한다.

### 실행한 반례와 경계

- ECC_51-14 / ECC_99-14의 pick 폭 47/77 mm, 힘 25/17.5 N, 접근 z 795/825 mm와 load
  접근 z 885/915 mm를 독립 기대값과 대조했다. open-door의 false와 수치 0을 누락으로 바꾸지 않는다.
- dense tray, 힘 60 N/0 N, 폭 70..130 mm, 잘못된 힘 단위 kg, 상충 Property Set를 위치와
  함께 차단했다. 폭 100 mm Override가 그리퍼 최대폭 검사만 통과했던 반례를 발견하고 **패키지
  제약**에 슬롯 pitch 검사를 추가했다. 코어에 트레이 전용 조건을 넣지 않았다.
- 안전 구간 20..40 N도 concrete=false / BOUNDED_INPUT_NOT_EXECUTABLE로 보존한다.
  값이 모두 고정되고 제약을 통과해도 RESOLVED_NOT_QUALIFIED다. 게시·운전 권한이 아니다.
- 세 번째 Object Type/Model과 회전한 트레이 Model/Instance를 데이터로만 추가하고 같은
  Workflow revision/rules로 재해석했다. 개발자의 실제 10분 측정과 실행 증거는 아직 없다.
- 실제 임시 SQLite/API 서버에서 커밋 후 응답 유실·원 요청 복구·프로세스 재시작·저장 보고서
  재조회/목록을 확인했다. 해석 중 권한 철회, 잘못된 digest·타 catalog 참조는 별도 시험으로 거절했다.
  이 응답 유실은 저작 API 시험이며 장비 UNKNOWN/자원 보유/운전자 복구 시험이 아니다.
- UI는 CLI가 저장한 같은 보고서를 재열어 8개 노드의 101개 값·단위·선택 source를 대조했다.
  정의/규칙의 pinned 이름과 입력 출처, 위반 클릭의 node 이동을 확인했다. report 목록은 서로
  구분되는 전체 ID를 표시한다. UI 계산 경로는 없다.

Platform 전체 workspace 시험·Clippy, SDK 137개 파일의 원본 일치, CLI 요청 복구 6개 시험,
UI 77개 시험·typecheck/build와 실제 API 회귀가 통과했다. PR의 정확한 head CI와 통합 상태는
병합 결과로 따로 기록한다. 사용자 M2 수락, Preview/게시/actual-part runtime binding/모의
운전·UNKNOWN 복구, 최종 RC와 Linux 45분 재현은 미완이다. 기존 RF/WF 완료 판정은 올리지 않는다.

## M2 사용자 CLI 확인과 인계 보완 — 2026-10-02

사용자는 A/B 값·상태, dense/60 N/100 mm/kg의 BLOCKED(rc=2), 20..40 N의 구간 상태,
report와 resolve 출력 일치, 기존 출력 파일 보호를 직접 확인했다. UI는 인계용 M1/M2 리스너
네 개가 종료되어 확인하지 못했다. crash 로그 없이 함께 종료된 현상은 exec 수명 연동이
의심되지만 원인으로 확정하지 않는다. 따라서 M2 전체 수락과 M3 시작 조건은 아직 미충족이다.

CLI 출력 보호의 시점을 보완했다. `resolve --output` 대상이 이미 있으면 로그인·조회·해석 요청
전에 rc=1로 거절하고 출력 경로 충돌임을 설명한다. 서버에 보고서를 만든 뒤 파일 충돌을 알리는
기존 동작과 구별된다. 요청 이후 발생하는 별도 I/O 실패는 원 요청 journal로 복구한다.
유효한 고정값은 rc=0, BLOCKED는 rc=2, BOUNDED_INPUT_NOT_EXECUTABLE은 rc=3으로 구별한다.
report/recover도 같은 상태 코드를 사용한다. text는 고정값·구간을 읽기 쉽게 표시하고, 한 속성의
동일 provenance만 중복 표시하지 않는다. 저장 JSON·규칙·계산 결과는 변경하지 않는다.

macOS 개발 인계 서비스는 사용자 launchd domain에서 실행하여 터미널/exec 수명과 분리했다.
기존 DB를 재사용하고 네 프로세스의 parent PID=1·HTTP 응답을 확인했다. 로컬 RUN_M2에는
정확한 시작·상태·종료 명령과 로그 위치를 기록한다. 로그인 시 자동 시작·물리 장비 연결은 없으며
로그아웃/재부팅 후 다시 시작해야 한다. 이는 최종 Linux RC 설치 방식에 대한 증거가 아니다.

출력 경로의 일반 파일·디렉터리·dangling symlink를 접속 전에 거절하는 시험과 text 보존 시험을
포함해 workflow CLI 8개 시험이 통과했다. 실제 임시 API/CLI 시험에서 기존 출력 충돌 전후의
서버 보고서 목록이 동일했고, concrete/blocked/bounded 종료 코드 0/2/3 및 구간 보고서 재조회가
일치했다. 사용자 UI의 보고서 선택·위반 이동·새로고침 재열기는 재확인 대기다.
