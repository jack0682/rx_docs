# 두 이미지의 구성·지원 명세 v0.1

> 2026-09-10 현재 계약의 규범 기준은 [RX 계약·프로토콜 v1.0](contracts/v1.0/README.md)이다. 이 문서의 선행 제안·예시는 v1.0과 충돌하면 대체된다. 자사 기본 지원 의무·두 이미지 경계는 유지하며, 실제 구현·실물 검증은 별도다.

## 1. 목적과 범위

[자사 기본 지원표](13_robotis_support_matrix.md)를 입력으로 두 RX 레포의 이미지 구성을 정의한다. `rx-platform`은 선택된 Rust 코어·Runtime, `rx-solutions`는 ROS 2·자사 필수 스택·BT·Adapter·UI·현장 패키지를 제공한다.

이 문서는 포함 패키지·실행 프로세스·volume·장치·네트워크·CPU/GPU variant·종료·재시작 정책의 설계 초안이다. Dockerfile·Compose·제품 코드·이미지는 아직 만들지 않는다. 실제 빌드·시간·실물 지원은 검증 전이다.

## 2. 이미지 구성

| 항목 | rx-platform 이미지 | rx-solutions 이미지 |
|---|---|---|
| 기준 OS 안 | Ubuntu 24.04 userland, ROS 미포함 | Ubuntu 24.04·ROS 2 Jazzy 기반 |
| 주 구현 | Rust Core·Runtime·API | C++ ROS/BT/Adapter, Python launch, TypeScript UI |
| 필수 구성 | 공통 계약·세대/작업 관리·기록/복구·API·진단 | 자사 다섯 레포·전이 의존성·모델 registry·공통 UI·BT·장비 Host |
| 데이터 처리 | SQLite 단일 writer·작업/결과/checkpoint·버전 기록 | 현장 설정·교정·정책 assets·관측·진단, 작업 원장은 platform 참조 |
| 장비 접근 | 없음 | 등록된 실제 장비/제어기 경로만 소유 |
| ROS/RMW | 없음 | 명시한 RMW·domain·namespace·router 설정 |
| 빌드 도구 | Cargo·선택 toolchain·Protobuf 생성 | colcon·ament·CMake, ROS 의존성, UI 빌드 도구 |
| 운영 시 패키지 변경 | 금지, 새 검증 이미지로 교체 | 금지, 새 검증 이미지/현장 패키지로 교체 |

개발·시험용과 배포용은 같은 레포의 stage/target으로 구분할 수 있다. 배포용에서는 개발 소스 bind mount나 실행 중 git clone·패키지 설치를 기본 제공 경로로 사용하지 않는다. 이미지 digest와 두 레포의 호환 조합을 명세에 고정한다.

자사 모듈은 기본 포함 대상이다. startup에서 모든 모델의 제어기를 동시에 실행하지 않으며, 선택한 장비 프로파일에 필요한 프로세스만 활성화한다. 한 모델의 기능이 특정 board·추론·센서를 요구하면 그 지원 조건을 registry와 variant에 명시한다.

## 3. 실행 프로세스

| 이미지 | 프로세스·역할 | 기동 정책 |
|---|---|---|
| platform | Core를 포함한 Runtime·Operation Service | 저장 상태와 미결 작업을 확인하고 API 제공 |
| platform | HTTP/gRPC·상태 통지·진단 | 같은 프로세스의 모듈로 시작할 수 있음. 실제 장비 준비와 별도 상태 |
| platform | SQLite writer 경로 | 논리 상태 변경·checkpoint의 일관성 관리 |
| solutions | UI·설정·진단 서비스 | platform이나 장비가 미준비여도 제한된 진단 화면 제공 |
| solutions | BT 실행기 | 등록·연결 가능, 유효한 run 세대·허가 전에는 작업 진행 금지 |
| solutions | 장비 Host/Adapter | 모델·역할·driver 소유 방식에 따라 준비 |
| solutions | controller_manager·robot_state_publisher·필요 controller/broadcaster | 실제 제어를 소유할 때만 기동. 시작/종료 효과의 사전 조건 필요 |
| solutions | 모델별 부가 서비스 | Nav2·카메라·lidar·sim2real·정책 실행 등 선택된 기능의 필수 집합 |
| solutions | ROS router·프로세스 supervisor | 시작 순서·자식 종료·오류·재기동 상태 관리 |

한 레포의 컨테이너 안에 여러 프로세스가 있을 수 있다. SDK·DHI 라이브러리를 레포별 서버로 쪼개지 않는다. controller_manager가 로드하는 하드웨어/controller 플러그인 경계를 유지한다. UI만 응답하는 상태와 실제 작업 실행 준비 상태를 구분한다.

이미 실제 로봇 컨트롤러에서 driver가 구동되는 구성에서는 solutions가 같은 하드웨어를 다시 열지 않고 상위 ROS/API에 연결한다. 이 경우 `driver_owner=external_controller`로 구분하고 장치 직접 매핑을 생략한다. 해당 방식도 식별·버전·관측·제어권 검증이 필요하다.

### 지원 ID에서 이미지 요구로 연결

아래는 [기본 지원표](13_robotis_support_matrix.md)의 ID·DEP 묶음을 사용하는 연결표다. variant는 후보이며 빌드·실물 지원 검증 전이다. 모든 행에 선택 모델의 ROS 제어·Adapter와 기본 registry가 필요하다. external_controller 방식에서는 이미지의 기본 자사 패키지는 유지하면서 현장 driver를 중복 실행하지 않는다.

| 지원 ID·구성군 | 필수 DEP 묶음 | 직접 제어 시 필수 프로세스/기능 | 장치 역할·자산 | variant 후보·외부 제어 차이 |
|---|---|---|---|---|
| OM-01·02·03 | BASE·OM | controller_manager·RSP, 해당 arm/gripper controller·JSB | USB serial, 모델·joint/tool·교정 | CPU amd64/arm64 후보. 외부 제어 시 ROS endpoint·상태 대조 |
| OM-04·08·09 | BASE·OM | leader controller·command broadcaster·JSB, 승인된 teleop 세션 | 모델별 USB/UART, leader 방향·offset·effort 설정 | CPU 후보. 외부 leader 명령원과 자동 공정 제어권 배타 |
| OM-05·06·07 | BASE·OM | 팔 및 필요 end-unit·GPIO/gripper controller·JSB | 팔 UART·툴 UART 역할, tool·end-unit 매핑 | 실제 보드에서 직접 제어하면 해당 arm64/장치 조합. 외부 연결은 host CPU와 별도 검증 |
| OM-10 | BASE·OM | follower JTC·JSB | USB serial, L100 follower 교정·그리퍼 매핑 | CPU 후보, 외부 ROS 제어기 연결 별도 |
| FFW-01·02 | BASE·FFW | 양팔·head·lift JTC·JSB | follower serial, revision별 모델·tool·교정 | CPU 후보, 센서/추론 모드 요구 시 SENSOR/GPU 추가 |
| FFW-03 | BASE·FFW | 팔·손/head/lift 제어, position/effort 모드 관리 | follower·손 연결, hand transmission·자세/힘 설정 | CPU 후보, 선택된 실제 손/센서에 따른 자산 추가 |
| FFW-04·05·06 | BASE·FFW·MOBILE | 조작·swerve·robot manager·JSB, SH5 pressure, navigation 사용 시 Nav2 | follower/base/sensor 역할, 조향·geometry·지도; SH5 손 압력 교정 | CPU 또는 필요한 GPU/센서 variant. 외부 base controller의 소유권 확인 |
| FFW-07 | BASE·FFW | leader·spring·joystick·command broadcaster·JSB | 좌/우 leader serial, offset·teleop 매핑 | CPU 후보, 자동 공정과 배타적인 입력 세션 |
| FFW-08 | BASE·FFW·MOBILE | base 관련 controller와 선택 navigation/lidar | base serial·센서, geometry·지도 | 구성 참조·launch 인자 검증 후 후보 확정 |
| AS-01 | BASE·AS의 기본 제어 | controller_manager·impedance·JSB·IMU/RC broadcaster | 역할별 e2d2udp, 관절 배열·IMU/RC 교정 | CPU 후보, 실제 host의 1 kHz 설정 요구 시험. 외부 제어 방식은 관측·명령 연동 시험 |
| AS-02 | BASE·AS 전체 | AS-01 + sim2real·mode·정책 추론 | 위 구성 + ONNX/policy·정규화·mode/authority 자산 | ONNX CPU 경로 후보. GPU 필요성은 정책·장치·시간 요구로 결정 |

BASE 등은 DEP-BASE 등의 축약이다. RSP는 robot_state_publisher다. 모델·정책·지도·교정은 아래 `/etc/rx/site`·`/opt/rx/assets`에 버전 있게 연결하고, 진단·준비 산출물은 `/var/lib/rx-solutions`에서 관리한다. 필수 DEP의 패키지는 모델별 프로세스 기동 여부와 별개로 기본 지원 집합에 포함한다.

## 4. volume·파일 접근

다음 경로는 배포 설계의 제안명이며 현재 생성한 디렉토리가 아니다.

| 목적·제안 경로 | platform | solutions | 정책 |
|---|---|---|---|
| `/etc/rx/platform` | 읽기 전용 | 불필요 | API·저장·운영 설정과 적용 버전 |
| `/etc/rx/site` | 등록된 manifest·관련 정책을 보존/조회 | 읽기 전용 | 활성 현장 패키지·장비 매핑·운영 범위 |
| `/var/lib/rx` | 읽기/쓰기·영속 | 직접 접근 금지 | DB와 관련 WAL/SHM·checkpoint·작업 증거를 같은 저장 범위로 관리 |
| `/var/lib/rx-solutions` | 직접 접근 금지 | 읽기/쓰기·영속 | 패키지 준비·진단·캐시. 독립적인 작업 완료 원장으로 사용하지 않음 |
| `/opt/rx/assets` | 필요 manifest·해시만 | 활성 자산 읽기 전용 | ONNX·모델·지도·교정 등 정확한 버전 보존 |
| `/run/secrets` | 해당 서비스 비밀만 읽기 | 해당 서비스 비밀만 읽기 | 패키지·로그와 분리, 두 이미지에 불필요한 비밀 공유 금지 |
| 로그·진단 출력 | bounded 기록·내보내기 | bounded 기록·내보내기 | 용량·보존·누락 표시·반출 범위 설정 |

수정 중인 설정·교정·모델은 staging 영역에서 검토하고, 활성 버전을 덮어쓰지 않는다. 승인된 package manifest와 해시를 platform에 등록한 후 사용한다. 두 컨테이너가 같은 DB 파일을 동시에 쓰는 구조로 만들지 않는다. 백업 복원도 실제 장비·소재·미결 작업 대조를 거쳐야 한다.

## 5. 장치와 권한

| 자원 | 접근 주체·설계 |
|---|---|
| serial/UART/USB | solutions에서 선택한 장비 역할만 매핑. OMY 팔/툴, FFW follower/base/sensor·좌우 leader 등을 구분 |
| K1 e2d2udp | solutions의 지정 네트워크 경로. 현재 코드의 endpoint를 현장 값으로 자동 확정하지 않음 |
| 카메라·lidar | 해당 모델·기능에서 필요한 장치와 driver에 한정 |
| GPU | 필요한 variant의 solutions 프로세스에 한정. platform에는 기본 GPU 권한 없음 |
| 실시간 스케줄링·메모리 잠금 | 필요가 확인된 제어 프로세스의 권한·ulimit·CPU 배치를 프로파일별 지정 |
| host 파일시스템·Docker socket | 기본 공유하지 않음 |

기존 자사 Compose의 privileged·전체 /dev·host IPC/network는 관측된 개발 설정이다. 그대로 제품 최소 권한으로 확정하지 않는다. 필요한 host udev/group·장치 식별·커널·드라이버와 권한은 모델별 배포 명세에 포함한다. 컨테이너만으로 실제 제어 주기와 안전한 정지를 보장할 수 없다.[^1]

장치 매핑은 고정 번호의 USB 장치를 임의로 선택하는 대신 실제 식별·역할과 연결한다. 같은 장치/로봇을 RX와 원본 컨테이너가 동시에 소유하지 않도록 준비 단계에서 확인한다.

## 6. 네트워크 명세

| 연결 | 목적 | 기본 정책 |
|---|---|---|
| UI ↔ platform API | 운영 요청·조회·상태 | 인증·권한·요청 식별, 공개 범위 제한 |
| platform ↔ BT/Adapter | 공정·장비 작업 계약 | 전용 서비스 경로·호환 버전·세대·기한·상태 스트림 |
| solutions ↔ ROS 제어기 | 자사 관측·제어 | RMW·domain·namespace·router endpoint를 명시 |
| solutions ↔ 장비 Ethernet/UDP | K1·레이저 PLC·타사 장비 | 승인된 장비 endpoint·프로토콜에 한정 |
| 빌드/배포 ↔ 저장소·이미지 registry | 의존성 확보·업데이트 | 운영 제어 네트워크와 역할 분리; digest·버전 고정 |

같은 PC에서는 Docker 사용자 정의 네트워크를 서비스 연결의 기본 후보로 둔다. ROS/장비 경로가 bridge 구성에서 요구 조건을 만족하지 못하면 제한된 host-network variant를 검토하고 이유·포트·노출 범위를 기록한다. core까지 일괄 host network로 올리지 않는다.

포트 숫자·subnet·실제 RMW·보안 설정은 다음 프로파일 명세에서 고정한다. 컨테이너 health나 RPC 연결만으로 장비 관측·제어권·작업 실행 준비를 판정하지 않는다.

## 7. CPU/GPU variant

| variant 후보 | platform | solutions | 모델 지원의 판단 |
|---|---|---|---|
| Linux amd64 CPU | Rust Runtime·저장·API | 기본 자사 패키지, CPU 경로·장비 연결 | 선택 모델·기능의 의존·시간·실물 검증 필요 |
| Linux arm64 CPU | 같은 계약의 arm64 빌드 | arm64 기본 패키지와 장치 경로 | OMY 보드 등 실제 host/driver 조합과 검증 |
| Linux arm64 Jetson/GPU | GPU 비의존 코어, 배치 CPU에 맞춤 | 해당 JetPack/L4T·CUDA·카메라·추론 의존 variant | AI Worker 기존 arm64 Docker의 GPU/보드 조건을 대조 |
| Linux amd64 GPU | CPU variant와 같은 코어 책임 | 요구가 확정된 GPU·추론/카메라 구성 | 실제 사용할 모델·가속 기능이 정해진 뒤 확정 |

GPU 이미지가 존재한다는 이유로 모든 AI Worker나 K1 기능에 GPU가 필수라고 선언하지 않는다. 반대로 CPU 이미지의 빌드만으로 GPU·특정 카메라 기능을 지원한다고 표시하지 않는다. 기본 자사 패키지를 누락하지 않으면서 해당 하드웨어에 필요한 기능을 검증해 지원표에 연결한다.

컨테이너의 CPU architecture와 제어 대상 로봇의 CPU는 같을 필요가 없다. 외부 컨트롤러에 상위 API로 연결하는 방식인지 RX host에서 직접 제어기를 실행하는 방식인지에 따라 필요한 variant가 달라진다. 에뮬레이션 빌드·모의 시험은 실제 제어 시간 검증으로 취급하지 않는다.[^2]

## 8. 시작 상태

| 상태 | 허용 범위 | 다음 상태 조건 |
|---|---|---|
| SOFTWARE_READY | UI·API·필수 모듈/모델 목록·진단 | 구성과 버전 일치 |
| PROFILE_BOUND | 장비 식별·driver 소유 방식·관측 경로 설정 | 실제 기동 효과·교정·모드·제어권 조건 확인 |
| CONTROL_PREPARED | 검증된 절차로 driver·controller 준비 | 유효한 관측·필수 기능·운영 조건 확보 |
| EXECUTION_ALLOWED | 허가된 run·operation 수행 | 모든 관련 조건의 지속 확인 |
| RECONCILING/BLOCKED | 조회·진단·정해진 중단/복구 | 미결 작업·잔류 명령·물리 상태 조정 |

SOFTWARE_READY에서는 전체 자사 launch를 자동 실행하지 않는다. DHI와 일부 FFW launch에 장치 쓰기·torque·초기 자세 효과가 있으므로 driver 준비는 이미 물리 효과가 있는 단계일 수 있다.[^3] default launch 값에 기대지 않고 실제 활성화·init_position·real/mock·mode를 명시한다.

UI·진단은 platform/장비가 준비되지 않아도 필요한 상태를 보여줄 수 있게 한다. 서비스 시작 순서와 건강 상태 확인은 Compose의 역할이지만, 실제 실행 허가는 RX 계약의 역할이다. Compose는 기본적으로 컨테이너 시작을 기다리며 애플리케이션 준비를 자동 보장하지 않는다.[^4]

## 9. 종료·재시작 정책

| 사건 | 기본 처리 |
|---|---|
| 정상 현장 종료 | 새 작업 허가 중단 → 미결/진행 작업 확인 → 모델별 정지와 지지·소재 이관/외부 유지 확인 → 토크 해제·driver 종료 가능 판정 → 결과/잔류 상태 보존 → 종료 |
| platform 재시작 | 기록·세대 복원, solutions와 기존 run/operation·checkpoint·현재 장비 상태를 조정한 뒤 신규 허가 |
| BT만 재시작 | 기존 run·단계 활성화·operation ID 복원. 완료 후 결과 통지를 잃은 작업을 새 작업으로 재실행하지 않음 |
| Adapter·controller 재시작 | 해당 관측·작업을 재조정 대상으로 전환. 자동 driver 재활성화·초기 자세 이동을 하지 않음 |
| solutions 컨테이너 재시작 | SOFTWARE_READY 또는 진단 상태부터 재진입. 물리 준비는 별도 조건 확인 |
| 급정전·강제 종료·연결 유실 | 소프트웨어 종료 hook이 수행됐다고 가정하지 않음. 장비 측 정의된 단절/보호와 복구 확인 필요 |

일반 서비스 자동 재기동은 제한 횟수·backoff·운영 경고와 함께 설계할 수 있다. 제어 프로세스 재활성화와 자동 공정 재개를 같은 restart policy에 묶지 않는다. 반복 실패 시 진단 상태를 유지하고 운영자가 원인을 확인할 수 있게 한다.[^5]

정상 종료 동안 platform과 solutions의 통신을 필요한 시점까지 유지한다. 단순히 Compose가 컨테이너를 역순 종료하는 것에만 의존하지 않고, 계획된 현장 종료·중단 절차를 먼저 수행한다. 저장 장애가 이미 진행 중인 작업의 중단 요청을 막지 않게 하되, 실제 정지 성공은 관측으로 확인한다.

stop grace 시간·제어 중단 기한·재기동 최대 횟수·backoff는 모델별 실패 영향과 측정 계획을 보고 다음 명세에서 수치화한다. 값이 없는 상태로 생산 운전 허가를 내리지 않는다. 모든 모델에 일괄 torque off를 정상 종료 규칙으로 적용하지 않는다.

DHI는 stop과 소멸 경로에서 torque disable을 호출하므로, 토크 유지가 필요한 상태에서는 정상적인 DHI/solutions 종료를 보류한다. 제어를 유지하거나 검증된 외부 유지 수단에 넘기고, 해제가 가능한 상태를 확인한 후 종료한다. 운영자가 강제 종료하거나 전원이 사라지는 상황은 이 정책만으로 방지할 수 없으므로 장비 측 보호·물리 유지 조건을 별도로 확인한다.[^3]

## 10. 이미지 지원을 선언할 증거

기본 지원표의 V0–V6를 이미지 digest·레포 버전·모델 profile ID·driver 소유 방식·CPU/GPU variant와 연결한다. 필수 모듈·정책 자산 누락, 모델/명령 배열 불일치, 미검증 시작 효과, 기준을 벗어난 관측·중단 경로가 있으면 해당 기능의 실행·지원 선언을 제한한다.

현재 두 이미지의 빌드·기동·장치 접근·실시간·복원·실물 시험은 모두 미수행이다. 이번 산출물은 그 시험에 필요한 명세 초안이다. 다음 단계는 기본 지원표에서 선정한 한 프로파일을 예로 들어 패키지·프로세스·장치 역할·시간 조건·검증표의 필드를 끝까지 채우는 것이다.

## Sources

[^1]: [기존 자사 컨테이너 조사](../references/stack_research_2026-09-09.md), Docker [자원·실시간 조건](https://docs.docker.com/engine/containers/resource_constraints/). 실제 host·모델에서 검증 전.
[^2]: Docker [multi-platform builds](https://docs.docker.com/build/building/multi-platform/), [Desktop USB/IP](https://docs.docker.com/desktop/features/usbip/). 2026-09-09 확인. native Linux와 Desktop/에뮬레이션의 실제 장치 검증을 구별.
[^3]: [자사 기본 지원표 §8](13_robotis_support_matrix.md), 해당 DHI start/stop·FFW launch 소스. SDK·컨테이너·장비 명령 실행은 하지 않음.
[^4]: Docker [Compose startup/shutdown order](https://docs.docker.com/compose/how-tos/startup-order/), 2026-09-09 확인. 서비스 순서와 RX의 실행 허가를 구분.
[^5]: Docker [자동 재시작 정책](https://docs.docker.com/engine/containers/start-containers-automatically/), 2026-09-09 확인. RX의 구체 재시작 제한·기한은 본 설계에서 별도 결정.
