# 05. 소프트웨어 구조와 레포·컨테이너 경계

[작업 공간 안내](../README.md) · 현재는 설계 단계 · [스택 비교·근거](12_stack_and_container_proposal.md)

## 1. 현재 구조

**rx-platform은 ROS 없는 공통 실행 제품, rx-solutions는 ROS·자사 플랫폼·실행기·앱·현장 구성을 제공하는 제품**으로 나눈다. 두 레포는 각각 자기 컨테이너를 가지며, 함께 RX 납품 소프트웨어를 구성한다.

자사 DynamixelSDK·dynamixel_hardware_interface·open_manipulator·ai_worker·ai_sapiens와 필요한 전이 의존성은 solutions의 필수 기본 구성이다. 자사 제품을 타사 선택 모듈과 동일하게 취급하지 않는다. 기본 지원 목표와 실제 모델·공정의 검증 완료는 구별한다.

이번 경계에서 코어 언어는 Rust로 선택됐다. 자사 제어·BT는 C++/ROS 2 Jazzy, UI는 TypeScript를 현재 스택안으로 구체화한다. 코드·컨테이너는 아직 구축하지 않는다.

## 2. 책임과 소유

| 구성 | 배치 | 책임 |
|---|---|---|
| 공통 계약 | platform | 장비·작업·관측·결과·공정 실행기의 언어 독립적 의미 |
| Core 라이브러리 | platform, Rust 선택 | 작업 동일성·상태·조건·증거·자원·복구 판단 |
| Runtime/Operation Service | platform | 작업 수락·장비 전달·기록·상태 배포·재시작 조정 |
| 운영 API·기록 | platform | 권한·작업지시·공정 실행·상태·실적의 원본 |
| 공정 실행기 | solutions, C++ BT 권고 | 순서·분기·병행·공정별 복구 경로를 제안·진행 |
| 장비 Host/Adapter | solutions | ROS·SDK·PLC 통신, 원본 관측·오류·요청 연관 |
| 자사 제어 스택 | solutions, 필수 | 기존 controller_manager·hardware plugin·SDK·모델 구성 활용 |
| 구성·운영 UI | solutions | 공통 화면과 현장별 확장, platform API를 통한 조작·조회 |
| 현장 패키지 | solutions에서 제공 | 장비·공정·tool·교정·신호·검증·운영 절차 |

solutions 레포는 현장 데이터만 담는 레포에서 역할이 넓어졌다. 공통 장비 연동·UI와 현장 전용 자산을 내부 패키지로 나눠 관리한다. platform은 특정 모델·ROS 패키지를 import하지 않는다.

## 3. 소스 의존성과 실행 메시지

소스 의존은 `rx-solutions → rx-platform의 버전 있는 공개 계약`이다. C++/TypeScript 소비자는 Protobuf·API 명세로 연결하며 Rust 내부 타입을 링크하지 않는다. 플랫폼 저장소는 원본 ROS 코드가 없어도 독립적으로 빌드·시험할 수 있게 설계한다.

실행 메시지는 양방향이다. platform이 공정 실행을 허가하면 solutions의 BT가 단계를 진행하고 platform에 작업을 요청한다. platform이 조건·기록을 처리한 뒤 지정된 solutions Adapter에 명령을 전달한다. 관측·결과는 platform에 모이고 BT·UI가 같은 원본을 조회한다.

공정·장비 명령의 접수와 장기 실행을 분리해 양쪽 RPC가 서로 완료를 기다리는 구조를 피한다. BT·Adapter가 platform을 우회해 자동 공정의 새로운 동작을 임의로 실행하지 않도록 실행 세대·권한·operation ID를 연결한다.

## 4. 코어와 ROS의 관계

코어 라이브러리는 상태·판정 규칙이며, Runtime은 통신·저장과 그 규칙을 조립한 서비스다. ROS·BT·SDK 구현은 solutions에서 사용한다. 선택된 Rust를 기준으로 코어 계약과 구현 명세를 구체화한다.

제품 전체에서는 자사 지원을 위해 ROS가 필수다. ROS를 코어 레포에 넣지 않는 것은 소스·빌드 의존성과 변경 영향을 제한하는 선택이다. solutions에 포함되는 ROS·controller·firmware·SDK 버전의 유지보수 책임은 그대로 남는다.

## 5. 레포·이미지·프로세스 구분

| 단위 | 의미 |
|---|---|
| 레포 2개 | 코어 제품과 ROS·장비·앱 제품의 개발·버전 경계 |
| 기본 이미지 2종 | 각 레포가 제공하는 독립적인 설치·실행 환경 |
| 기본 컨테이너 2개 | 같은 현장 PC에서 위 두 이미지를 조합한 배포안 |
| 내부 프로세스 | Runtime, BT, 장비 Host, ROS 제어 등 필요한 실행·장애 경계 |

SDK와 hardware_interface를 별도 컨테이너로 분리하지 않는다. 제어 라이브러리는 ros2_control의 기존 플러그인·프로세스 구성을 존중한다. 물리 장치 접근은 solutions가 소유하고, 원본 자사 컨테이너와 중복 제어하지 않도록 한다.

CPU/GPU·보드별 이미지 variant는 같은 레포에서 관리한다. 컨테이너가 호스트 커널·USB·GPU 드라이버·실시간 조건까지 같게 만드는 것은 아니므로, 실제 지원 환경과 기능을 모델별로 명세한다.

## 6. 변경 위치

| 변경 | 우선 수정할 곳 |
|---|---|
| 요청 식별·공통 상태·복구 의미 | platform 계약·Core·Runtime |
| ROS 배포판·DYNAMIXEL SDK·controller 변경 | solutions의 필수 의존 집합·연동·지원표 |
| 새 자사 모델 | solutions의 기본 모델 registry·실행 구성·작업 매핑·검증 |
| 타사 로봇·PLC 추가 | solutions의 추가 어댑터·프로파일 |
| 문 센서·척 신호·지그·tool 변경 | solutions의 현장 패키지와 필요한 장비 프로그램 |
| UI 변경 | solutions의 공통 UI 또는 현장 확장 |

양쪽의 호환 버전과 컨테이너 digest를 납품 명세에 묶는다. 자사 필수 지원은 버전 불일치를 무시한다는 뜻이 아니다. 지원 기능의 실패·부족을 숨기지 않고 해당 자동 실행 범위를 제한한다.

## 7. 다음 설계

이미지 구성·권한·네트워크·volume·프로세스 생명주기, 자사 제품군별 기본 지원표, WorkflowExecutorPort·DevicePort·운영 API를 문서로 구체화한다. 상세 스택 판단은 [12 문서](12_stack_and_container_proposal.md), 실행·복구 경계는 [10 문서](10_structure_proposal.md)를 따른다.

이전 C++ 중심·단일 Runtime 내부 BT 구성은 [이전안](../references/previous_design/05_software_architecture_before_container_split.md)에 보존했다.
