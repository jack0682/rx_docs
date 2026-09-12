# Phase75: commissioning 이후 제품 UI의 모의 작업 시작·실행 조회 연결

## 범위와 판단

이 문서는 phase74 검증을 위해 동결된 현재 소스를 읽어 작성한 구현 계획이다. 제품 소스·규범·SDK를 수정하거나 빌드/서버를 실행하지 않았다. 목표는 이미 정상 qualification을 활성화한 SIMULATION 셀에서 등록 단말의 작업자가 수량 2를 명시적으로 시작하고, 실제 Host/실행기 경로의 두 소재 완료를 확인하는 것이다. 물리 셀은 NOT_COMMISSIONED를 유지한다. 재시작 후 Host producer 재연결과 전체 복구는 별도 미완료 범위로 유지하며 시험용 세션/AlwaysTrue authority로 우회하지 않는다.

최소 변경은 **기존 CreateRun·StartRun mutation과 overview 목록을 유지하고, 선택한 Run의 시작 문맥·시작 시도·사람용 실적 조회를 추가**하는 것이다. 이 단계에서 별도의 PrepareStart 권한이나 두 번째 작업 원장을 만들 필요가 없다.

## 1. 이미 존재하는 실제 경로

| 단계 | 현재 코드와 타입 | 실제 의미 |
|---|---|---|
| 실행 기록 생성 | `POST /api/v1/runs` → `Command::CreateRun` → `Engine::create_run` | 현재 cell revision과 recipe/site digest를 검사하고 PREPARED Run과 불변 구성 참조를 기록한다. 장비 동작·자격 발급은 없다. |
| 실행 기록 목록 | `GET /api/v1/overview` → `Engine::overview` → `CellOverview.runs: Vec<Versioned<Run>>` | 셀 권한으로 제한한 최신 최대 50개 목록이다. `runs_truncated`가 있으므로 전체 이력으로 해석하지 않는다. 첫 새 Run 선택은 이 목록을 재사용한다. |
| 시작 | `POST /api/v1/runs/start` → `Command::StartRun` → `Engine::start_run` | 실제 등록 단말의 Operator가 현재 조건을 통과하면 StartAttempt/Arm outbox를 기록한다. 첫 응답은 ARMING이다. |
| 실제 시작 확정 | P delivery → Host Arm → `Command::FinishArm` → `acknowledge_arm_delivery` | 모든 현재 Host ACK와 재검사를 통과해야 STARTED, mandate, EXECUTING을 원자 기록한다. |
| 시작 시도 조회 | `Engine::inspect_attempt(identity, attempt_id)` | Engine helper만 있다. runtime Command와 HTTP GET은 없다. gRPC GetStartAttempt도 unimplemented다. |
| 소재 조정 | `Engine::production_view`, `rx-executor` serial coordinator | 실제 Run/part/예산/완료 조정은 존재하지만 이 조회는 Executor 전용이다. 인간 UI에 그 세션이나 admission 값을 넘겨 사용하게 하면 안 된다. |

근거 파일:

- [workflow.rs](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/workflow.rs)
- [routes.rs](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-api/src/routes.rs)
- [runtime application.rs](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-runtime/src/application.rs)
- [projection.rs](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/projection.rs)
- [production.rs](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/production.rs)
- [production gRPC](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-api/src/grpc/production.rs)

## 2. 정확한 mutation과 시작 검사

기존 mutation 형식을 바꾸지 않는다. Counter 값은 JSON 문자열이다.

```json
{
  "request_key": "<CreateRun UUID>",
  "command": {
    "cell": "<cell>",
    "recipe_digest": "<현재 recipe SHA-256>",
    "site_config_digest": "<현재 site SHA-256>",
    "expected_cell": "<현재 cell revision>"
  }
}
```

```json
{
  "request_key": "<별도 StartRun UUID>",
  "command": {
    "run": "<생성한 Run UUID>",
    "envelope_digest": "<검토한 현재 envelope SHA-256>",
    "purpose": "PRODUCTION",
    "budget_unit": "PART_ATTEMPT",
    "budget_limit": "2",
    "expected_cell": "<시작 확인 시 cell revision>",
    "expected_run": "<시작 확인 시 run revision>"
  }
}
```

CreateRun receipt는 같은 key 회수 시 최초 생성 결과를 반환할 수 있다. 따라서 그 응답만 보고 `expected_run=1` 또는 현재 PREPARED 상태를 가정하지 말고, 새 시작 문맥 조회에서 현재 revision을 다시 읽는다.

StartRun은 현재 Operator·등록 단말의 셀 권한 교집합, cell/run CAS, Run의 불변 구성과 현재 구성 일치, PREPARED, pending attempt 부재, 다른 활성 purpose와 충돌 없음, 올바른 예산 단위·양수·cell.maximum_budget 이내를 검사한다. Run에 이미 budget/purpose가 있으면 그 값은 고정이다. 실패한 기존 attempt 뒤에도 다른 수량으로 바꾸지 않는다.

이어 `ready`가 현재 qualification batch·정책·영향/Host 문맥과 block/open case 부재를 확인하고, qualification의 PRODUCTION 목적과 시작 조건 PASS, 현재 Executor 세션 하나, Host의 현재 epoch/scope·살아 있는 grant를 확인한다. 마지막 Host ACK에서도 사람/단말·revision·조건·Executor 세션·Host boot·deadline을 다시 검사한다. UI 준비 화면의 PASS는 이 재검사를 대신하지 않는다.

제품 `rx-platformd`의 `UnconnectedQualification`은 유지한다. phase74의 pinned policy/원본·서명·독립 승인·Host 수용을 거쳐 활성화한 SIMULATION 자격을 사용한다. qualification 이전에 PREPARED Run을 만들면 기존 quiet barrier가 Busy로 막으므로, 이 사용자 흐름에서는 commissioning 완료 후 CreateRun을 생성한다.

## 3. 추가할 최소 읽기 모델·API

새 application 모듈 제안: `crates/rx-application/src/operator_run.rs`, `src/engine/operator_run.rs`. 기존 model/projection에 무관한 필드를 흩뿌리기보다 사람용 읽기 타입을 모은다.

### A. GET /api/v1/run/start-context?cell=...&run=...

한 transaction에서 다음을 반환한다.

- installation/store_generation/runtime_boot, `checked_at`.
- cell ID/revision/epoch, environment, commissioning, 정확한 envelope/recipe/site/configuration digest.
- Run ID/revision/state, 기존 purpose/budget, pending_attempt.
- 현재 `maximum_budget`, qualification에 허용된 purpose, PRODUCTION의 `PART_ATTEMPT` 단위. 자격이 없거나 현재가 아니면 허용 목적을 임의로 채우지 않는다.
- 시작에 필요한 등록 단말·현재 자격·조건·Executor·Host 준비의 확인 결과와 명확한 차단 이유. native guard가 최종 경계라는 사실도 보존한다.

이 응답은 시작 권한·토큰·새 attempt가 아니다. 읽기에서 budget이나 outbox를 쓰지 않는다. Operator와 셀 접근권을 확인하고, 등록 단말 부재는 읽기 결과에서 설명할 수 있어도 실제 StartRun은 기존 terminal_required=true를 유지한다. 미등록/비활성 계정·단말의 업무 조회 거부는 기존 인증 규칙을 유지한다.

Engine의 기존 시작 검사 중 읽기 전용 부분을 공유 helper로 추출하여, context 표시와 StartRun이 서로 다른 규칙을 복사하지 않게 한다. mutation의 순서인 현재 권한 확인 → 원래 key 회수 → CAS/새 시작 검사는 유지한다. 수량 입력은 UI에서 최대값·기존 고정 budget으로 안내하고, 실제 값은 기존 StartRun이 다시 검사한다.

### B. GET /api/v1/run/start-attempt?cell=...&run=...&id=...

기존 `inspect_attempt`를 runtime Command/Reply와 HTTP로 연결한다. 제공한 cell/run/attempt의 상관관계를 같은 읽기에서 검사하고 다른 셀은 조회 전에 거부한다. 반환은 실제 저장된 `StartAttempt`와 현재 Run 상태를 결합한 사람용 view가 적절하다. required/acknowledged Host 수와 status, 현재 조회 시각·deadline을 보여 주되 ACK 수만으로 STARTED를 추론하지 않는다.

현재 저장 StartStatus는 PENDING/ARMING/STARTED/REJECTED다. UI는 정확한 저장 상태를 유지한다. 단순 deadline 경과는 별도 파생 표시이며, read가 상태를 REJECTED로 바꾸지 않는다.

### C. GET /api/v1/run/production?cell=...&run=...

인간 세션과 셀 접근권으로 Run별 현재 실적을 읽는 별도 projection을 추가한다. 기존 Executor 전용 `production_view`의 권한을 완화하지 않는다. 공통 순수 읽기 helper는 재사용할 수 있지만 `caller_session`, Executor admission, raw control cursor나 permit를 사람 화면에 재사용하지 않는다.

최소 응답: 현재 Run revision/state와 불변 recipe/envelope, 허용 시도 한도·소비·잔여, 실제 part ID/ordinal/disposition, 진행/확인 완료/불명/거부/미처리 수량. 목록을 제한한다면 집계는 전체 원장으로 계산하고 truncated를 명시한다. scope는 선택 Run 하나이며 전역·다른 셀 목록을 읽지 않는다. `CONFIRMED_COMPLETED`만 확인 완료로 집계하고 예산 소비를 완료 수량으로 표시하지 않는다. native operation 결과와 자원 인계는 기존 Work projection을 Run으로 필터해 함께 표시한다.

기존 Run 상태와 parts를 한 transaction cut에서 읽어, 완료 수량·예산·Run 상태가 서로 다른 시점의 값으로 섞이지 않게 한다. 기존 양품 판정 기능은 없으므로 완료 소재를 양품으로 표시하지 않는다.

## 4. UI 연결 위치와 동작

대상은 [App.tsx](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/apps/operator/src/App.tsx), [schema.ts](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/apps/operator/src/schema.ts), [pending.ts](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/apps/operator/src/pending.ts), [views.tsx](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/apps/operator/src/views.tsx)다. 필요하면 `run-start.tsx`와 `run-status.tsx`로 화면을 분리한다.

1. commissioning 완료 셀에서 기존 ‘새 실행 준비’를 수행하고 반환된 Run을 선택한다. overview의 PREPARED 목록에서도 기존 Run을 명시적으로 선택할 수 있게 한다. 자동으로 가장 최근 Run을 시작하지 않는다.
2. start context를 읽고 수량 2·현재 공정/셀·PRODUCTION·현재 자격·차단 이유를 확인한다. 기존 budget이 있으면 수량을 고정한다. 상태가 PREPARED가 아니면 시작 조작을 제공하지 않는다.
3. 확인창을 열 때 정확한 cell/run revision과 시작 본문을 고정한다. 배경 polling으로 그 본문을 자동 교체하지 않는다. stale 거부 후 새 문맥을 읽고 다시 검토한다.
4. pendingSchema의 route에 `/api/v1/runs/start`를 추가하고, 송신 전에 원래 key/body를 저장한다. 현재 principal/installation/store_generation 연결을 유지한다. timeout/reload 후 같은 요청을 회수하며 새 key를 자동 생성하지 않는다.
5. 응답 Run/cell/envelope·purpose/budget·attempt 상관을 검증한다. ARMING receipt를 받으면 HTTP 결과 미확정 상태는 끝내되 시작 확정 대기를 별도 상태로 유지한다. attempt GET으로 실제 상태를 확인하며 POST를 일반 polling에 쓰지 않는다. 응답 유실로 ID조차 모르면 기존 POST key를 먼저 회수한다.
6. STARTED/EXECUTING 이후 사람용 production view와 기존 work 결과/인계 상태를 표시한다. 두 소재가 확인 완료되어도 자원 처분과 Run 완료 조건은 P 기록으로 확인한다.

기존 same-origin cookie·직접 mTLS·CSP·CSRF 정책은 유지한다. 브라우저가 Executor credential·Host credential을 갖거나 Host에 직접 Arm/native 요청을 보내지 않는다.

## 5. 실제 수량 2 인수의 선행 의존과 미완료 경계

현재 `rx-executor-service`의 [config.run/config.visit](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/runtime/rx-executor/src/bin/service.rs) 요구는 기존 실행파일의 제약이다. 이를 새 배정 계약으로 승계하지 않는다. 새 셀 service는 Run이 없는 idle 상태에서 먼저 실제 Executor session을 열고 유지한다. **StartRun이 먼저 요구하는 것은 현재 Executor session이며 특정 Run의 사전 배정이 아니다.** 시작 이후 assignment read에서 ARMING/EXECUTING Run을 발견하여 Attached 상태로 연결하고, 실제 실행 권한은 기존 mandate/세션/조건 검사로 확인한다. UI가 실행기 설정 파일을 만들거나 시험용 세션을 주입해서 이 연결을 대체하면 안 된다. 별도 S 서비스 작업과 결합하지 않으면 이번 UI/API 구현은 ‘시작 접수까지’의 부분 완료다.

실제 compiled process·정확한 Host binding/관측·자격이 선행되어야 한다. 기존 browser fixture의 `process:None`은 실제 BT 실행 입력이 아니다. 성공 인수는 실제 P/S 이미지와 release-owned 제품 entrypoint·FILE_SIMULATION backend·영속 실행기/Host 원장으로 수행한다.

추가로 현재 attempt expiry는 독립 timer로 상태를 끝내는 경로가 없다. ACK가 전혀 오지 않으면 저장 상태가 ARMING/pending인 채 남을 수 있고, 늦은 ACK나 별도 invalidation에서 거부된다. 전달 경로는 만료 Arm을 거부한다. UI는 이 경우 ‘시작 확인 기한 경과/조정 필요’를 보여 주고 자동 재시도·자동 성공·Run 삭제를 하지 않는다. 명시적 만료 조정이 필요한 제품 시나리오는 writer의 별도 bounded expiry/종료 절차로 설계해야 하며, 이번 단순 GET으로 숨기면 안 된다.

## 6. 구현 순서와 필요한 반례

1. P 읽기 helper/DTO/세 API 및 권한·무변경 시험.
2. UI 선택·수량·확인창·StartRun pending 회수·attempt 표시.
3. S 영속 Run 배정/현재 Executor 세션과 결합.
4. 실제 두 이미지·등록 단말 브라우저에서 수량 2 정상 완료 및 응답 유실 인수.

필수 시험:

- 읽기 API는 Run/attempt/budget/outbox/qualification을 생성하거나 수정하지 않는다. 미로그인·다른 셀·다른 설치 cookie·폐기 단말·역할 회수·cell/run/attempt 교차 ID를 거부한다.
- 자격 없음, 현재성 잃은 v2 impact/정책, 남은 RuntimeRestart/OperatorHold/Case, 조건 FAIL/UNKNOWN/expired에서 StartRun을 거부한다. 표시를 위한 context 조회가 이를 승격하지 않는다.
- 0/음수/숫자형 Counter/최대 초과 수량, 잘못된 purpose/unit, 이미 고정된 예산 변경을 거부한다. 수량 2는 두 소재 ‘시도’ 예산이며 실패·불명 시도를 환급하지 않는다.
- CreateRun 이후 구성 변경, 확인창 이후 cell/run revision 변경, Executor session 0개/복수/교체, Host grant/boot/epoch 변경을 거부한다. 재검토 없이 새 revision을 자동 넣지 않는다.
- StartRun commit 전 실패에는 attempt/Arm outbox가 없다. commit 후 응답 유실·브라우저 reload에는 원래 key/body로 같은 attempt를 회수한다. 같은 key에 다른 수량/Run이면 충돌이다.
- 일부 Host ACK는 ARMING이며, 전체 실제 ACK와 현재 조건 재검사 뒤에만 STARTED/mandate/EXECUTING이다. duplicate ACK는 mandate를 추가하지 않는다. 늦은 ACK·기한 경과·시작 중 단말/역할 회수는 성공을 만들지 않는다.
- Start receipt를 다른 Run/cell/attempt의 응답으로 바꾸면 UI가 미확정으로 보존한다. ARMING HTTP 수신과 실제 STARTED를 구별한다. 새 탭/재접속 시 기존 미확정 요청을 다른 작업으로 덮지 않는다.
- 실제 serial coordinator가 두 part만 만들고, 원래 IDs로 native 결과·인계·완료를 연결한다. 독립 FILE_SIMULATION 로그의 효과 수와 P의 두 part/소비2/확인완료2/잔여0/Run COMPLETED를 대조한다. 다음 part는 예산 때문에 거부된다.
- production view는 같은 cut의 상태를 반환하고, COMPLETE/UNRESOLVED/REJECTED/NOT_PROCESSED와 예산 소비를 구별한다. 브라우저는 부분 목록으로 전체 수량을 추정하지 않는다.
- P/Host/실행기 재시작 또는 producer 재연결 실패를 fixture 권한으로 우회하지 않는다. 이 경우 실제 차단과 남은 구현을 기록한다.

이 순서는 첫 운영 연결의 우선순위이며 R01–R30의 나머지 복구·지원·작업지시/품목·전체 이력·다중 셀·native 지원 목표를 제거하지 않는다.
