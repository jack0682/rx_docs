# Phase81 — 조사 포기 절차·서명·사람 attestation의 최소 공급 경로

2026-09-13. `docs/implementation/next_steps/phase80_intervention.md`와 현재 P 소스를 읽었다.
이 문서만 작성했다. 제품 코드 수정·빌드·시험·서버 기동·DB 쓰기는 하지 않았다.
범위: 현재 RecoveryLead + registered terminal의 명시 조사 포기 → UNRESOLVED + QUARANTINED.
outcome 직접 쓰기, 자원 해제, 자동 결론, 물리 procedure/Close/RestartRun 구현은 제외한다.

## 권고

가장 작은 경로는 **startup에서 pin한 조사 서명 자료를 읽는 작은 준비 경계 + 사람 attestation 접수**다.
기존 requalification의 detached-signature 준비 패턴과 package의 파일/서명 primitive를 재사용한다.
새 PackageKind, 범용 artifact registry, 새 review job/state framework는 필요하지 않다.
아래 신규 이름은 구현 후보이며 확정 norm/API 이름을 추가한 것이 아니다. T5 command 계약은 root 소유다.

## 정확히 재사용할 코드

| 기존 type/function | 재사용 목적과 한계 |
|---|---|
| [config::PinnedFile](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-platformd/src/config.rs:16) | 배포 설정의 `path + sha256` 형식을 그대로 사용. 조사용 optional 설정 하나를 추가할 수 있다. |
| [policy::read_with_digest<T>](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-package/src/policy.rs:47) | 고정한 trust/자료 JSON을 strict decode하고 원문 SHA를 대조. 내부 read_regular는 NOFOLLOW/NONBLOCK + 실제 regular-file/길이 확인을 한다. |
| [PackagePath / directory::read_relative_file](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-package/src/directory.rs:170) | 실제 절차 원문/참조 파일을 설정된 로컬 root 아래에서 제한 크기로 취득. HTTP caller의 절대 경로/URL이나 std File::open 별도 구현은 필요 없다. |
| [SignatureEnvelope](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-package/src/model.rs:204) | 기존 `{key,signature}` 형식. private key는 외부 서명자에게만 있고 P는 public key만 읽는다. |
| [verify_detached_message](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-package/src/verify.rs:438) | Ed25519 strict 검증을 직접 호출. 조사 절차가 소유하는 domain-bound message를 넘긴다. 기존 qualification/report message를 재사용해 서명 의미를 혼동하면 안 된다. |
| `rx_package::content_digest`, `canonical::{decode_json,bytes,digest}` | 원문 hash/size/schema 및 canonical typed 내용 검증. procedure_digest는 실제 절차 원문 content digest와 대조하고, signature message domain binding은 별도로 둔다. |
| [requalification::Worker::{new,current_policy,prepare}](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-runtime/src/requalification.rs:14) | pinned trust 파일 재확인, semaphore 1개, spawn_blocking, bounded 파일 취득, 검증된 결과만 반환하는 **구현 패턴**. 이 Worker 자체는 여섯 영역 qualification 전용이므로 그대로 호출할 수 없다. |
| [package_intake::{Ticket,Prepared}](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/package_intake.rs:39) | caller가 Deserialize할 수 없는 writer 발행 ticket/verified 준비 결과 패턴. 실제 타입에는 package/store 전용 의미가 있어 조사 DTO로 재사용하지 않는다. |
| [submit_package_intake](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-api/src/routes.rs:1195) | 현재 인증 → 원래 요청 회수/검증 ticket → off-writer 준비 → 현재 권한/CAS 재검사 commit 순서의 실제 API 예제. |
| [requalification put_blob/read_blob](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/requalification.rs:192) | 원문/내용 주소를 transaction에 보존하고 다시 hash/size를 확인하는 패턴. 함수는 qualification 전용 prefix/private이므로 조사 한두 작은 JSON에 chunk framework를 추가할 이유는 없다. |
| [engine::access::authorize](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/engine/access.rs:3) | 현재 사람 세션·역할·셀·registered terminal 검증. T5/attestation은 `Role::RecoveryLead`, `terminal_required=true`를 사용하고 source/actor를 서버에서 결합한다. |
| [procedure::can_report](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-application/src/procedure.rs:165) | Host/Executor/OperatorApi 서비스 identity를 인간 보고로 격상하지 않는 기존 필터. RecoveryLead 요구를 이 필터만으로 대체하지 않는다. |
| [terminal_https + 기존 HTTP ingress](/Users/ojaehong/RX_automation/rx_ws/rx-platform/crates/rx-api/src/terminal_https.rs:80) | direct mTLS, 사용자 cookie/단말 결합, Host/Origin/CSRF, strict mutation decode를 유지한다. 새 signer login 방식은 필요 없다. |

## 그대로 쓰면 안 되는 기존 경로

- PackageKind는 Device/Process/Ui뿐이다. 조사 문서를 가짜 Process로 포장해 process compiler/review를 통과시키는 것은 작은 재사용이 아니다.
- `Worker::prepare`의 verify_relative → Store::put → Store::verify_owned는 서명 package 보존에 유용하지만, intake receipt의 상태는 **AwaitingReview**이고 승인 권한은 없다.
- `process_review::Authority`는 process validator 목록, `requalification::Policy`는 여섯 영역/profile/environment를 검증한다. 그 schema/서명키 권한을 조사 포기용으로 자동 전용하지 않는다.
- `procedure::Assertions/RecordProcedure`는 Case/action/단계 보고다. 현재 Action에 조사 포기가 없고, ACK는 notification뿐이다. 이를 조용히 포기 attestation으로 해석하지 않는다.
- 제품 `UnconnectedQualification`의 verify_procedure/verify_close_policy는 false다. 이번 좁은 조사를 위해 물리 policy PASS를 만들거나 해당 기본값을 true로 바꾸지 않는다.

## 추가할 최소 두 경계

### 1. 서명된 조사 절차의 제한된 admission 자료

후보 type 묶음: `InvestigationProcedure`와 그 검증된 admission 결과. 범용 절차 interpreter가 아니다.
내용은 실제 조사 절차 ID/revision·원문/참조 ArtifactRef·적용 cell/configuration/profile 범위·허용된 명시 조사 포기 assertion 의미만 고정한다.
허용 효과는 UNRESOLVED + QUARANTINED 하나이며 success/release/Arm/operation kind 선택 필드를 두지 않는다.
trust public key ID/bytes와 허용 절차 ref는 **배포 측 pinned 설정**에서 선택한다. 입력 artifact가 자기 public key를 제공해 스스로 신뢰를 만들면 안 된다.
새 별도 trust 객체 계층 대신 작은 pinned admission 설정 한 파일에 그 제한된 key/ref 목록을 둘 수 있다.
기존 `PinnedFile`로 이 설정을 지정하고 `read_with_digest`로 pin을 확인한다.
실제 자료는 예를 들어 절차 JSON/문서 원문과 `SignatureEnvelope`이며, 참조된 모든 원문 bytes/hash/size/schema를 검증한다.
`verify_detached_message`에 조사용 domain + key ID + 정확한 절차 digest/적용범위를 묶은 메시지를 준다. domain 이름은 root의 신규 계약에서 확정한다.
자료 서명은 절차 버전/적용범위의 provenance이고, 특정 작업을 포기한다는 사람의 현재 의도를 대신하지 않는다.
첫 scope는 startup `Loaded`/setup에서 검증하고 trusted composition command로 원문·signature·trust digest를 영속 보존하면 충분하다.
별도 브라우저 policy-admit endpoint나 intake/review job를 추가할 필요가 없다. 설정 없음/불일치는 해당 처분 기능 미구성으로 남긴다.
runtime 중 재검증이 필요하면 위 Worker 패턴의 작은 method만 사용하고, worker 결과 후 writer에서 현재 trust/configuration과 권한을 다시 대조한다.
기존 package/process/qualification 등록 generation을 조사 admission의 권한으로 오인하지 않는다.

### 2. 명시적 사람 InvestigationAttestation

후보 type: `InvestigationAttestation`. 새 generic EvidenceBody dispatcher 대신 이 한 가지 사람 의도만 받는다.
원 operation과 현재 조사 context/revision, procedure digest, 선택한 **실제 저장 evidence IDs**, 명시적 조사 포기 assertion, 보고 시각을 결합한다.
actor/session/registered terminal/설치·셀 범위는 현재 인증/원장으로 결정하며 HTTP body의 role/actor 자기 주장으로 받지 않는다.
attestation은 원 native capture를 복사하거나 success/후조건 PASS를 만들어 내지 않는다. 조사 결과 불충분과 격리 유지 의도를 명시한다.
원문과 canonical ArtifactRef, 실제 actor/terminal/기록 시각, 원 evidence 상관을 같은 writer transaction에 보존한다.
frozen RecoveryDisposition은 evidence IDs를 참조하므로 **먼저 이 attestation을 저장하는 좁은 API 1개**를 두면 기존 T5 모양을 유지할 수 있다.
구체 endpoint/command 명칭과 T5와의 같은 요청 결합 여부는 root 계약에서 결정한다. 일반 RecordProcedure의 ACK endpoint로 대신하지 않는다.
신규 API가 필요하다면 기존 `Mutation<T>`/request-prior-remember 및 `Preflight::Recorded` 패턴을 재사용한다.
내용·현재 권한·단말·상관 확인 후 같은 key/body는 같은 attestation ID를 회수하고, 다른 내용은 충돌이다.
attestation 접수 자체로 Work outcome을 바꾸지 않는다. root의 T5가 이 보존 원문과 현재 상태를 검증한 뒤 UNRESOLVED를 도출한다.
사람의 별도 private signing key를 요구할 필요는 없다. 현재 registered-terminal mTLS+인증 세션과 durable typed 원문이 사람 의도를 결합한다.
배포 절차 서명 검증과 사람의 매 요청 인증은 서로 다른 검증이다.

## 공급 순서와 최소 반례

1. 배포자가 조사 절차 원문/서명/public trust pin을 제공 → P off-writer에서 실제 bytes 검증 → 원문/admission 영속 보존.
2. 현재 RecoveryLead가 registered terminal로 원 operation/보존 근거/적용 조사 절차를 읽음 → 명시 attestation 제출/동일 key 회수.
3. root T5가 현재 권한·단말·원문 상관·절차 적용범위·operation CAS를 재검사 → 조사 처분만 원자 기록.
4. 기존 source evidence와 native success는 그대로 보존하고, holder/quarantine/permit/mandate/Run/part/budget/blocks/qualification은 그대로다.

- 임의 digest, 누락/변조 원문, 다른 key/domain/절차 범위, self-supplied trust, 과거 configuration에만 맞는 절차는 거부한다.
- 다른 operation/invocation/profile의 evidence, notification ACK, 단말 없음/철회, 역할 회수, 서비스 identity는 포기 attestation이 아니다.
- stale operation/context 또는 worker 중 trust 변경은 새 T5를 막는다. 원래 동일 요청의 회수는 현재 인증 뒤 수행한다.
- reply loss는 같은 ID/원문을 회수한다. attestation만 제출하거나 서명 자료만 설치한 것으로 자동 UNRESOLVED가 생기지 않는다.
- 원 native 기록의 오래된 시각을 현재 상태로 갱신하지 않는다. 이 좁은 처분은 fresh 지지/잔류 명령 확인이나 자원 RELEASE를 주장하지 않는다.

현재 제품에서 위 두 신규 경계는 없다. 재사용 가능한 것은 검증/전송/영속성 primitive와 실행 순서다.
전체 procedure signature admission·Close·RecoveryPlan·Host operating rebind·E recovery를 여기서 추가 설계하지 않는다.
