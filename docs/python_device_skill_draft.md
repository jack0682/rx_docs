# Python 함수와 장비 SDK를 사용하는 스킬 초안

2026-09-28 사용자 선택: 신규 스킬의 기본 작성 방식은 **Python 함수 + 필요한 장비 SDK**다. 이 문서는 다음 구현의 요구와 미결을 고정하며, 아직 구현·지원된 기능을 뜻하지 않는다. 전체 완료 기준은 [스킬 프레임워크 감사](skill_framework_draft_audit.md)를 따른다.

개발자는 Python 동작과 입출력, 필요한 SDK를 작성한다. RX는 스킬 버전과 설치된 의존 환경을 고정하고 서버에서 등록·실행·결과·복구·KPI를 관리한다. 공정에는 등록된 스킬 호출과 업무 데이터 연결을 작성한다. 내부 권한·기록·대기 절차를 호출마다 BT에 전개하지 않는다.

## 현재 코드에서 확인한 연결점

- LOCAL_SIM은 `main(inputs)`를 지원하지만 runner의 `-S` 및 고정 실행 환경 때문에 일반적인 외부 SDK 설치·로딩을 제공하지 않는다. 이 worker를 그대로 장비 실행 경로라고 표시하지 않는다.
- 기존 Host에는 NativeAdapter와 release-owned AdapterFactory가 있다. 현재 제품 Backend는 FILE_SIMULATION, 기존 DYNAMIXEL 경로, MELSEC/JTC 패키지이며 임의 Python 구현을 등록하는 Backend는 없다.
- 기존 ProgramGoal은 program과 parameter_set의 ArtifactRef를 갖는다. 새 프로그램 실행 계약을 만들기 전에 이 경로의 검증·등록·전송 경계를 활용할 수 있는지 구현으로 확인한다.
- P에는 공정 초안, Step binding 선택, 패키지 심사·구성 적용·활성화 경로가 있다. 실제 온라인 공정 작성부터 모의 Host 실행까지 연결된 증거는 있으나 새 Python 구현 등록 증거는 아니다.

## 이번 구현이 충족해야 할 사용자 흐름

1. `main(inputs)` 형태의 Python 스킬과 입출력 선언, SDK 의존성을 작성한다. SDK별 코드가 RX 코어의 분기문으로 추가돼서는 안 된다.
2. 등록 시 코드·의존 환경·스키마·장비 역할·완료 판정 정의를 하나의 불변 버전으로 묶는다. 사이트의 장비 주소와 자원 연결은 재사용 가능한 코드에서 분리한다.
3. 실행은 기존 P/Host의 허가를 거친 뒤 고정된 Python 환경에서 수행한다. SDK import 또는 모듈 로딩의 부작용도 허가 전 장비 동작을 일으키지 않도록 실행 시점을 다룬다.
4. 동적 입력은 원 실행에 고정한다. 선행 출력에는 스킬 버전·원 실행·원 관측을 연결하고, 장비 관측의 유효성/보정/출처가 필요한 경우 단순 JSON 값으로 대체하지 않는다.
5. timeout, 프로세스 종료, SDK 예외는 물리적인 실패나 정지를 자동 증명하지 않는다. 원 실행을 조회·조정하며 같은 장비 명령을 자동 재전송하지 않는다. Python의 반환값은 선언된 완료/후조건 검사와 연결한다.
6. 동일 실행 기록에서 스킬 버전별 성공·실패·불명, 소요 시간과 누락을 집계한다. P 원장과 다른 완료 원장을 만들지 않는다.
7. 외부 개발자가 공개 설치 명령으로 설치한 뒤 새 SDK 스킬을 등록·조합·실행할 수 있는 배포물로 릴리스한다.

## 검증할 반례와 완료 근거

- 실제로 별도 배포된 테스트 SDK를 import하는 Python 스킬을, RX 코어 수정 없이 등록한다. 표준 라이브러리 함수나 SDK 이름만 있는 선언으로 대신하지 않는다.
- 등록 후 코드/환경 바꿔치기, 잘못된 입력·출력, 만료된 관측, 자원 충돌을 거절한다.
- SDK 명령 직전/직후와 결과 저장 직전의 프로세스 종료를 주입한다. 독립된 모의 장비 효과 기록과 P/Host 실행 ID를 대조해 재실행/누락/불명을 구분한다.
- 새로 등록한 서로 다른 스킬을 조합해 실행하고, 선행 출력이 후속 입력에 들어간 원인을 원 실행 기준으로 추적한다.
- 설치·재시작·업데이트 후 같은 버전과 환경이 실행됐음을 확인한다. 테스트 키와 모의 SDK의 통과를 실제 장비 자격으로 확대하지 않는다.

다음 구현의 첫 작업은 기존 Host의 ProgramGoal에 연결할 Python 실행·원 요청 조회 경계를 만드는 것이다. SDK 환경의 획득/고정과 native 완료/관측 전달이 함께 검증돼야 하며, LOCAL_SIM에 import만 허용하는 변경으로 전체 요구를 대체하지 않는다. Python 프로세스 종료는 장비의 물리 정지 증거가 아니므로 독립된 현장 보호와 자원 인계의 의미를 보존한다.

## 진행: SDK 환경 준비 CLI

`rx skill prepare-environment`와 `verify-environment`를 구현했다. 별도 fixture SDK wheel을 실제 CLI로 오프라인 설치하고, 테스트 스킬이 그 SDK를 import해 값을 반환하는 시험을 실행했다. 기존 출력 덮어쓰기와 파일 변경, wheel 시작 훅·상위 경로를 거절하는 시험도 통과했다. 준비 과정 자체는 스킬/SDK를 import하지 않는다.

이 결과는 환경 준비의 근거이며 Host 등록/실행 근거가 아니다. 가상환경은 현 경로와 플랫폼에 고정되고, base Python 전체·native system library의 release pin은 아직 연결되지 않아 결과에 미검증 상태를 표시한다. 다음 작업은 이 환경을 기존 ProgramGoal과 Host 허가·원 실행 조회에 연결하는 것이다. SDK 의존성 완전성, 임의 장비 제어와 동적 입출력이 지원됐다고 주장하지 않는다.

## 진행: 실제 Host gate 뒤의 Python adapter

Rust PythonSkill adapter를 기존 Host gate에 연결해 준비 단계·잘못된 호출자에서는 SDK 효과가 없고, 올바른 허가 이후에만 실행되는 것을 확인했다. 반복 허가/조회는 효과를 반복하지 않았다. 시간 초과는 SendEntered를 유지하고 인계를 거절하며, 코드 변경과 만료된 dispatch도 거절했다. [검증 기록](../references/python_host_gate_2026-09-29/README.md)을 참조한다.

현재는 Host 라이브러리의 실제 gate 시험이다. 제품 service Backend/Factory 등록 경로, P 등록, 출력/관측 전달과 운영자 조정은 아직 미완료이며 모의 support만 허용한다. 이 결과를 전체 설치 경로 또는 실제 장비 실행 지원으로 확대하지 않는다.

## 진행: 제품 Host 서비스 로딩

제품 Builtin factory와 설정 로더에 Python 등록을 연결했다. 설치·Host·셀·Intent·환경 digest를 대조하고 실행 파일/보조 코드는 릴리스 경로에서 고정한다. 실제 이미지의 rx-hostd 초기화·기동·정지에서 SDK/스킬 import가 없었고, 물리 binding과 변조 입력은 거절됐다. [검증 기록](../references/python_host_service_2026-09-29/README.md)을 참조한다.

이제 제품 서비스가 등록 파일을 로드하지만, 파일은 아직 시험 도구에서 준비했다. P의 사용자 등록 명령과 배치, 실제 P/Executor/Host Python 실행 및 출력 연결은 다음 작업으로 남는다.

## 진행: 기존 서명 장치 패키지 경로 재사용

Python 등록을 DEVICE_REFERENCE와 공통 operation catalog로 묶는 python-assemble을 추가했다. 서명 검증·원본 재조립·현재 정책과 선택 manifest 검증을 기존 경로에 연결했고, CLI와 변조/신뢰 키 제거 반례 시험을 통과했다. [검증 기록](../references/python_device_package_2026-09-29/README.md)을 참조한다.

P에 별도 스킬 DB나 새 패키지 ABI를 추가하지 않았다. 다만 이번 시험은 metadata 패키지 fixture이며 실제 P 접수 및 설치된 signed-package Python 실행은 아직 다음 검증으로 남는다.

## 진행: 실제 P 접수와 소프트웨어 보고서 확인

실제 Linux 이미지에서 SDK 환경을 준비하고 생성·서명한 Python 장치 패키지를 별도의 P에 공개 API로 접수했다. AWAITING_REVIEW 기록과 원본 catalog 일치, 동일 요청의 같은 접수 기록을 확인했다. P의 원 심사 요청을 실제 S 검증기가 검사하고 외부 테스트 서명자가 서명한 보고서를 P가 ready_for_software_approval로 기록했다. [검증 기록](../references/python_package_p_review_2026-09-29/README.md)을 참조한다.

아직 심사 결정은 없고 활성화 허가는 false다. 이 결과는 SDK 배치·binding 적용·실행이나 독립 승인으로 확대하지 않는다. 다음 단계는 승인된 Python 패키지의 실제 Host 배치와 공정 실행·출력 연결이다.

## 진행: 별도 계정 승인과 검토된 binding의 CLI 조합

실제 P에서 제출자의 자기 승인은 거절됐고 별도 테스트 검토 계정이 현재 보고서를 승인했다. Python binding 계획의 영향 검토 후 설치된 CLI가 그 계획을 선택해 공정 초안을 저장하고 v2 컴파일 입력에 원 계획/binding 출처를 보존했다. compose-recover도 같은 결과였다. [검증 기록](../references/python_reviewed_composition_2026-09-29/README.md)을 참조한다.

최종 활성 구성은 바뀌지 않았고 Run/자격도 없었다. 별도 테스트 계정을 독립된 사람의 심사로 표현하지 않는다. 다음 남은 작업은 실제 배치·공정 적용/활성화·Python 실행과 출력/KPI 연결이다.

## 진행: 공정 staging과 기존 Host 교체 미구현 경계 확인

검토된 Python binding으로 작성한 공정을 실제 도구로 패키징·검증하고 별도 테스트 계정의 승인과 staging까지 진행했다. P는 Host binding 변경 계획을 만들었지만 적용 준비를 HOST_BINDING_CHANGE_REQUIRED / CAPABILITY_MISSING으로 거절했다. [실행 증거와 다음 전환 요구](../references/python_deployment_boundary_2026-09-29/README.md)를 참조한다.

이는 배치 완료가 아니다. 기존 Host maintenance는 준비/취소까지만 있어, 원 저널·정상 정지 증거를 보존하는 교체 commit과 P의 실측 확인을 구현해야 한다. 해당 거절을 없애서 통과시키거나 별도 DB 수정으로 우회하지 않는다.
