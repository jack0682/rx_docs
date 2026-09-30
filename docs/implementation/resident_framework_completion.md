# 상주 프레임워크 초안 완료 원장

기준일 2026-10-01. 목표는 사용자의 “상주 프레임워크로써의 완전한 모델”과 “진짜 초안을 완성”이다.
기존 제품의 도입·운영·유지보수 목적, [마스터 플랜](../42_framework_master_plan.md)의 요구와 검증 게이트를 유지한다.
이번 원장은 범위를 작은 demo나 릴리스에 맞춰 줄이지 않는다. 상태는 실제 코드·실행 근거가 바뀔 때만 갱신한다.

## 작업 범위와 기준선

- 모델 원본: [실행 모델 revision 1](../45_resident_framework_execution_model.md), 개념 명세 CN01–CN22·AC01–AC18.
- 제품 기준선: Platform `9e12a624ed2b3e3e9bd0d150db23632590cf0be0`, Solutions `ea5b53f933d04a60f6bdbd7ee833a232c97d2d25`.
- 기존 릴리스 근거: [0.4.0-rc.1 결과](https://github.com/jack0682/rx_docs/releases/download/v0.4.0-rc.1/VALIDATION.json).
  15분·7 Run·14 FILE_SIMULATION 효과는 당시의 범위이며 아래 전체 완료를 증명하지 않는다.
- 이 단계의 쓰기 범위: rx_docs의 모델·완료 원장·관련 안내. 구현 단계는 해당 코드 저장소의 별도 feature PR과 검증 근거로 연결한다.
- 다른 작업 트리의 미커밋 재자격 작업과 설계 원칙 초안은 보존한다. 연구 backup 브랜치를 통째로 병합하지 않는다.

## 완료 요구와 현재 증거

| ID | 완료 요구 | 완료를 입증할 근거 | 현재 상태 |
|---|---|---|---|
| RF01 | OD08·RR01–RR03과 공통 신원/수명/판단 모델 완결 | 상태·전이·소유자·부분 실패·양성 복귀를 CN/AC/MC와 대조한 검토 및 구현 대응 | 실행 모델 r1 작성, 검증 미완 |
| RF02 | P 등록 소유와 S 실행 관리의 단일 연결 | 외부 작성자의 등록→실행→상실→조회·복귀, stable ID/이력 이행, 이중 writer 반례 | 공통 값 타입 R1 통합. P의 새 선언 저작 경로 R2 구현·검토 중; S 실행 연결·기존 신원 이행 미완 |
| RF03 | 논리·호스트·장비 자원 묶음 수락 | 실제 집행과 준비/commit/유실/거절/회수 행렬, 두 작업의 충돌·진행 가능성 | 요구 타입과 부분 OS 집행 존재; 전체 경로 미완 |
| RF04 | 공통 의존 결합과 관측 전용 참여 | 매 사용 검증, provider 교체·stale·상실 전파, 제어권 없이 관측 등록 | 부분 모델 존재; 공통 연결 미완 |
| RF05 | 작업·권한·결과·인계 계약 충족 | 양성 업무 완료 및 실제 반례, OI08/11/17 포함 책임별 검증 | 모의 경로 있음; 계약 공백 남음 |
| RF06 | 운영 중 추가·교체·제거 | A 실행 중 B 추가, 다음 작업부터 전환, 기존 결과·의무 보존, 부분 적용 복귀 | Cell/Host 변경 경로 일부; 일반 구성요소 경로 미완 |
| RF07 | 장애 후 같은 설치의 운영 복귀 | P/S/Host/Executor 각각의 상실·동시 상실·정산·재자격·새 업무, 원 수행 미재생 | 일부 재수용·복구 존재; 전체 행렬 미완 |
| RF08 | 코어 upgrade/restore의 연속성 | schema migration, Host 최대 epoch, old ACK/refusal, 의무·신원 보존, 이전 버전 이행 | backup/restore 있음; OI11/17 및 전체 이행 미완 |
| RF09 | 열린 확장·개발 도구 | 외부 프로세스와 컴파일 확장, manifest/선언 API, 코어 수정 없이 두 작성자 기능 통합 | 닫힌 backend, 일부 SDK/저작 도구; 일반 경로 미완 |
| RF10 | 지속 설치·운영·원격 유지보수 | 같은 설치의 시작/중지/진단/변경/upgrade, UI·CLI·인증·감사 및 응답 유실 | 새 모의 session 설치됨; 일반 지속 운영 미완 |
| RF11 | 표준 패키지와 기본 개발 번들 | DYNAMIXEL/MELSEC/JTC·Python/BT/UI·ROBOTIS 선정 다섯 프로젝트의 범위별 설치·연결·검증 | 부분 모의 자산; 전체 번들 완료 아님 |
| RF12 | 품질·재사용·작성 비용 증거 | 30 불변식의 책임별 의미 시험, 속성 시험, 10k seed, 결함 행렬, 처리량·24h soak, 이기종 두 계열·두 번째 사이트, C1–C5 기준선 비교 | 부분 시험과 15분 관찰만 확인; 전체 미완 |
| RF13 | 운영 영역·원격 시간·위임·단절의 모델과 지원 경계 | 단절/재합류/중복 권한 반례, 선언한 지원 범위의 실제 시험 | 개념 요구 존재; 광역/분산 구현 완료 아님 |
| RF14 | 현장 제품 적용과 물리 게이트 보존 | 실제 대상·설치·작업·보호·입회·commissioning 근거와 유지보수 인수 | NOT_COMMISSIONED; 별도 명시적 장비 운전 승인 필요 |

RF14와 광역 규모 실증을 소프트웨어 모의 시험으로 닫지 않는다. 반대로 외부 사실이 필요한 항목이 있다는
이유로 소프트웨어 모델·코드·모의 반례 작업 전체를 멈추지 않는다. 전체 Goal 완료를 주장할 때는 사용자가
요청한 범위와 이 원장 전부를 다시 대조하고, 미완·간접 증거·외부 대기 항목을 숨기지 않는다.

## 첫 변경과 확인 순서

1. 실행 모델 r1의 네 미결을 반례·기존 계약·현 코드에 대조하고, 애매한 전이와 이행의 충돌을 수정한다.
2. 등록/실행 신원에서 기존 S 모델을 재사용할 경계를 정하고 P의 단일 application 경로에 연결한다.
3. 준비·자원·의존·업무 사용의 실제 경로를 연결한다. 새 관리 서비스나 별도 권한 원장을 먼저 만들지 않는다.
4. 재자격 WIP는 원본을 보존한 채 독립 이식·검증한다. ACTIVE까지의 기록을 이후 Run 실행의 증거로 쓰지 않는다.
5. 장애·교체·복원·확장·저작·운영 검증을 이어 간다. 쉬운 정상 경로만을 완료 기준으로 재정의하지 않는다.

다음 실제 구현 대상으로 RF02를 선택한다. RF01 문서 검사는 RF02 구현 완료를 뜻하지 않는다.

## R1 — 공통 구성요소 신원 값 타입

2026-10-01. [Platform 변경](https://github.com/jack0682/rx-platform/commit/8a178fa4f412747383c1d63ff10a72a1acab34b6)과
[Solutions 변경](https://github.com/jack0682/rx-solutions/commit/88903c6ccf26ef9ba8a53f48bcda98575e8b0ad2)은 Supervisor에 있던
CatalogReference·Declaration·RegistrationState·Registration·VersionedRegistration·Binding을
`rx-domain::component` 원본과 생성 SDK로 공유한다. 기존 Supervisor import 경로는 re-export로 유지한다.
새 API, 등록 소유권 이행, 실행 권한 또는 persisted schema 변경은 아직 없다.

실행한 로컬 검증: rx-domain 전체 시험과 v1 JSON 호환/권한 필드 거절 시험, rx-supervisor의
all-features 시험·doctest, 두 패키지의 all-targets/all-features clippy, formatter, 저장소·기존 계약
해시·SDK export 회귀·120개 파일 source 비교. 명령들은 성공했다. 실행 환경은 macOS이며 Linux 전용
시험은 로컬 결과로 주장하지 않는다. 이후 두 코드 PR의 Linux 전체 workspace CI와 DCO도 통과했고, 문서 → Platform → Solutions 순서로 develop에 통합했다. 이는 등록 writer 이행의 근거가 아니다.

관련 PR: [Platform #61](https://github.com/jack0682/rx-platform/pull/61),
[Solutions #71](https://github.com/jack0682/rx-solutions/pull/71).
이 단계는 타입의 원본을 공유한 것이며 RF02 전체 완료가 아니다. 후속 P 등록 트랜잭션·API·S 실행 보고·
기존 등록 ID 이행·단일 writer 보장·positive 사용 경로가 필요하다.

통합 커밋: Platform `ba621747203861a8612c88f34fe35f54204b0e25`,
Solutions `f08dd8846ca4b727e41f357fc149291bab571e51`. 통합 후 원본과 SDK 120개 파일 일치를 다시 확인했다.

다음 작업은 RF02의 P 등록 소유 경로다. 공개 등록 명령의 권한/내용 수용, 기존 S 등록의 이행 차단,
P 등록과 S 실행 보고의 연결을 함께 설계·구현한다. 등록만으로 실행·업무 권한을 만들거나
P와 S가 같은 등록을 독립적으로 변경하는 경로를 내놓지 않는다. 이미 확인한 재자격 WIP는 별도로 보존한다.

## R2 — Platform 원장의 새 등록 선언

2026-10-01. [후보 계약](../contracts/resident-registration/v1/README.md)과
[Platform 구현](https://github.com/jack0682/rx-platform/commit/7608043ee50137fd2736a064728e0b6a37388131),
[PR #62](https://github.com/jack0682/rx-platform/pull/62).

Cell 없이 새 구성요소 ID를 만들고, 작성자/관리자의 현재 권한으로 조회·변경·퇴역한다.
선언·과거 버전·감사·원 요청 결과는 기존 application writer의 한 트랜잭션에서 기록한다.
응답 유실 후 원 요청 복구, 재시작 후 기존 ID 유지, stale revision·다른 작성자·권한 철회·client namespace
별칭 공격, 퇴역 후 재활성화와 권한 필드 주입을 검사했다. 실제 HTTP ingress에서 같은 writer로 연결된다.

로컬 macOS 검증: 전체 workspace/all-features 시험 501 passed / 0 failed / 16 ignored.
추가 owner/ID 거절 단언 뒤 대상 application·HTTP 시험을 재실행해 통과했다. 전체 workspace/all-targets/
all-features clippy, formatter, 저장소 검사/시험, 기존 계약 hash, SDK 120개 일치가 통과했다.
기존 Engine 역방향 경계 18곳/31회는 늘지 않았다. Linux PR CI 결과는 별도 확인한다.

Accepted는 작성자의 선언이 기록됐다는 뜻이다. 패키지 내용 검증·프로세스 소유·업무 허가는 응답에
NOT_ESTABLISHED/NOT_ESTABLISHED_BY_REGISTRATION/NOT_EVALUATED로 명시한다.
기존 S UUID 수입, S 실행 보고·배정, 검증된 package 내용 수용, 발견/페이지 조회가 아직 남아 있으므로
R2를 RF02 완료나 상주 프레임워크 전체 완성으로 표시하지 않는다.

후속 연결의 조건: Supervisor에는 작성자의 일반 Engineer 계정을 넘기지 않는다. 설치가 신뢰한 서비스
신원과 구성요소별 보고/실행 범위로 연결하고, 등록 변경 권한과 실행 관측 보고 권한을 분리한다.
기존 S 등록의 이행은 이전 writer의 등록 쓰기 차단, 원본 ID/버전/이력, P 수용, 확인 응답 유실과 재시작을
함께 검증해야 한다. 출처·권한 세대를 표시하지 않은 두 원장의 단순 복제는 대안으로 채택하지 않는다.
