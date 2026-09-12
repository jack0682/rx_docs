# 자사 기본 지원표 v0.1

> 구현 진행 보충(2026-09-12): 아래 표는 최초 source 관찰 기준판이다. 필수 스택의 이미지 빌드와 ROS JTC 연결 계층의 모의 검증은 이후 단계에서 진행했다. 현재 16개 지원 구성의 51개 JTC 선언을 자동 선택할 수 있으며, controller/action 통신 시험과 물리 검증은 구분한다. [현재 JTC 구현](https://github.com/jack0682/rx-solutions/blob/codex/initial-draft/native/ros-jtc/README.md), [전체 구현 진행](implementation/progress.md)을 따른다. V3/V6 현장 검증 완료를 의미하지 않는다.

> 2026-09-10 현재 계약의 규범 기준은 [RX 계약·프로토콜 v1.0](contracts/v1.0/README.md)이다. 이 문서의 선행 제안·예시는 v1.0과 충돌하면 대체된다. 자사 기본 지원 의무·두 이미지 경계는 유지하며, 실제 구현·실물 검증은 별도다.

## 1. 적용 기준

자사 기본 지원표를 먼저 정의하고 [두 이미지 명세](14_image_support_spec.md)의 패키지·프로세스·장치 요구를 이 표에서 도출한다. 코어 언어는 Rust로 선택됐으며, 실제 코드·이미지·장비 시험은 후속 단계다.

자사 지정 레포와 실제 필요한 전이 의존성은 `rx-solutions`의 필수 구성이다. 지원 단위는 **제품군 + 코드 모델/revision + 역할·제어 모드 + 연결 방식 + 검증 조합**으로 둔다. 같은 모델의 일반 제어·leader·AI follower를 동일 프로파일로 취급하지 않는다.

아래 모델 ID는 로컬 코드의 구성 식별자다. 공식 판매 모델 목록이나 보유 실물 목록을 확정하는 자료는 아니다. 기존 구성은 기본 registry에 수록할 대상으로 관리하고, 실제 출하 모델·revision과 대조한다. 파일 존재를 실행·완료·물리 안전 검증으로 확대하지 않는다.

## 2. 공통 기반

| 기반 | 역할 | 기본 포함 |
|---|---|---|
| DynamixelSDK | 직렬·지원 통신 경로의 DYNAMIXEL 접근 | 필수 |
| dynamixel_hardware_interface + dynamixel_interfaces | ROS 제어 하드웨어 플러그인·진단/관리 형식 | 필수 |
| ROS 2 Jazzy·ros2_control·ros2_controllers·pluginlib | controller_manager와 controller/broadcaster 구성 | 필수 |
| open_manipulator·ai_worker·ai_sapiens | 모델·제어·launch·상위 기능 | 필수 |
| robotis_interfaces·robotis_hand 등 | 모델별 메시지·손 제어·관측 등의 전이 의존 | 필요한 기본 기능과 함께 필수 |

기호: **DHI** = DynamixelHardware 플러그인, **JTC** = JointTrajectoryController, **JSB** = JointStateBroadcaster. 목록의 update_rate와 명령 배열 길이는 설정값이다. 실측 주기나 독립 구동기 수를 뜻하지 않는다.[^1]

## 3. OpenManipulator·OMY·OMX

모든 행은 기본 통합 대상이다. 현재 증거 수준은 코드/구성 확인이며 빌드·실물·RX 계약 검증은 미수행이다.

| 지원 ID | 모델·제어 구성 | driver/controller | 상위 작업·관측으로 연결할 후보 | 주요 검증·구분 |
|---|---|---|---|---|
| OM-01 | `open_manipulator_x` 일반 | DHI, arm JTC, gripper action, JSB | 팔 trajectory, gripper 명령, 관절 상태 | 팔 명령 4항목; gripper 보유 판정은 별도 |
| OM-02 | `omx_f` 일반 | DHI, arm JTC, gripper action, JSB | 팔·gripper 작업 | 팔 5항목. OM-03과 명령 집합 구별 |
| OM-03 | `omx_f_follower_ai` | DHI, arm JTC, JSB | 6항목 trajectory·관측 | gripper 포함 방식과 팔 자원 공유 검증 |
| OM-04 | `omx_l_leader_ai` | DHI, gravity compensation, trigger position, command broadcaster | leader 관절·입력, 수동 유도/teleop 역할 | 생산 작업을 직접 수행하는 follower로 자동 분류하지 않음 |
| OM-05 | `omy_3m` 일반 | DHI, arm JTC, JSB | 6항목 팔 trajectory | end-unit 구성은 있어도 gripper action을 기본 가정하지 않음 |
| OM-06 | `omy_f3m` 일반 | DHI, arm JTC, gripper action, JSB | 6항목 팔과 `rh_r1_joint` gripper | 팔·툴 연결, TCP·gripper·완료 근거 |
| OM-07 | `omy_f3m_follower_ai` | DHI, 7항목 arm JTC, GPIO command, JSB | follower trajectory·툴 GPIO | OM-06의 별도 gripper action과 다른 계약 |
| OM-08 | `omy_f3m_leader_ai` | DHI, gravity compensation, command broadcaster, JSB | leader 입력·관절 상태·명령 스트림 | effort 모드·접촉/수동 개입과 동작 주체 |
| OM-09 | `omy_l100_leader_ai` | DHI, gravity compensation, spring actuator, command broadcaster | leader 입력·gripper spring·관절 상태 | follower로 전환되는 제어권·offset·방향 |
| OM-10 | `omy_l100_follower_ai` | DHI, 7항목 arm JTC, JSB | follower trajectory·관절 상태 | OM-09와 운영 모드·인터페이스 구별 |

관측된 일반 설정 주기는 OpenManipulator-X/OMX 100 Hz, OMY-3M/F3M 400 Hz, OMY-L100 300 Hz다. 같은 관절을 여러 controller나 leader·RX 명령원이 동시에 소유하지 않도록 모드별 활성 controller 집합을 명세한다.[^1]

## 4. AI Worker / FFW

| 지원 ID | 모델·구성 | driver/controller | 상위 작업·관측 후보 | 주요 검증·구분 |
|---|---|---|---|---|
| FFW-01 | `ffw_f1_follower` | DHI, 좌/우 arm JTC, head/lift JTC, JSB | 양팔·head·lift trajectory | 각 팔 8항목에 gripper 포함; 팔/gripper의 controller 공유 |
| FFW-02 | `ffw_bg2_rev2/3/4_follower` | 위와 같은 controller 구성 | 양팔·head·lift 작업 | revision마다 독립 registry·시험 결과 필요 |
| FFW-03 | `ffw_bh5_rev1_follower` | 양팔 JTC, 양손 JTC·effort controller, head/lift, JSB | 팔·손 자세/힘 모드·상태 | 손별 20개 명령 항목을 독립 actuator 수로 해석하지 않음; position/effort 모드 소유권 |
| FFW-04 | `ffw_f2_follower` | 양팔/head/lift JTC, swerve drive, steering init JTC, robot manager, JSB | 조작·베이스 속도·odometry·운영 모드 | 여러 하드웨어 연결, 조향 초기화·제어권 전환 |
| FFW-05 | `ffw_sg2_rev1_follower` | F2와 유사한 controller 종류 | 조작·베이스·관측 | 모델별 geometry·신호·교정은 F2와 별도 |
| FFW-06 | `ffw_sh5_rev1_follower` | swerve/robot manager, 양팔·양손/head/lift, pressure broadcaster | 이동·조작·손 압력 관측 | 손별 position/effort 전환, 압력 calibration·갱신·접촉 판정 |
| FFW-07 | `ffw_lg2_leader` | DHI, command broadcaster, 좌/우 spring, joystick, JSB | leader 입력·teleop 명령·관절 상태 | `/dev/left_leader`, `/dev/right_leader` 역할 분리 |
| FFW-08 | `ffw_mobile_base` 부속 구성 | DHI와 base launch; SG2 설정 파일을 참조하는 경로 | 베이스 단독 연결·속도·odometry 후보 | 독립 판매 SKU로 확정하지 않음. launch 인자·참조 controller의 일치 검증 필요 |

표의 FFW controller 설정은 100 Hz다. 베이스가 있는 설정에서 `cmd_vel_timeout`은 1.0초로 명시돼 있지만, 이것을 셀의 정지 시간·정지 거리 보장으로 사용하지 않는다. navigation 패키지에는 Nav2·SLAM/지도 구성 경로가 있으나 `cmd_vel`만으로 목표 위치 도달이나 docking 완료가 확보되는 것은 아니다.[^2]

FFW-02는 설명을 줄이기 위해 revision을 묶었다. 실제 registry에서는 rev2·rev3·rev4 각각을 다른 profile ID로 만들고, 실제 모델 식별과 교정·시작 동작·시험 결과를 구분한다.

## 5. AI Sapiens

| 지원 ID | 모델·모드 | driver/controller | 상위 작업·관측 후보 | 주요 검증·구분 |
|---|---|---|---|---|
| AS-01 | `k1_rev1` 기본 제어 | DHI, JointGroupImpedanceController, JSB, IMU·RC broadcaster | 관절·IMU·RC 상태, 정의된 impedance 제어 기능 | 명령 배열 23항목, `~/commands`; 실제 배열·단위·유효값 검증 |
| AS-02 | K1 sim2real·정책/모드 | AS-01 + sim2real node·ONNX Runtime·policy assets | 모드 목록/전환·ModeStatus, 정의된 자세·속도 동작 후보 | 모드 접수와 자세/이동 완료를 구분; 모델·정규화·센서·authority 조건 |

기본 controller 설정과 sim2real launch에 1000 Hz가 명시돼 있다. 이는 요구 자원·지연 시험의 입력이며 실측 성능이 아니다. `k1.launch.py`의 기본 controller 기동과 sim2real 실행은 별도 경로다. 두 기능을 제공하려면 그 실행 관계·버전·정책 파일을 함께 검증해야 한다.[^3]

AS-02의 구성에는 Damping·ReadyPose·Velocity 등 모드와 API 진입 조건이 있다. 서비스 호출 성공이나 active_mode 일치만으로 자세 도달·보행 완료를 주장하지 않는다. RX의 완료가 있는 상위 작업으로 제공하려면 추가 완료 근거를 계약에 정의한다.

## 6. 공통 상위 작업으로 묶을 범위

다음 이름은 RX 설계용 작업 분류다. 구현된 API 이름이나 지원 완료를 뜻하지 않는다.

| 작업·관측 종류 | 연결 후보 | 완료·사용 조건 |
|---|---|---|
| 장비 식별·준비·상태 조회 | 모든 기본 모델 | 모델·버전·namespace·제어권과 관측 유효성 확인 |
| 관절 trajectory | JTC가 있는 일반/follower 구성 | action 결과와 적용 오차·현재 관측·요청 연관성. topic 송신만으로 완료하지 않음 |
| gripper/손 제어 | 전용 action 또는 팔/손 controller | controller 자원 공유·모드 전환을 반영. 소재 보유는 추가 관측 |
| leader 입력·teleop 상태 | OM leader·FFW LG2 | 명령 스트림의 출처·수신 갱신·수동 제어권. 유한 생산 작업과 구별 |
| 베이스 속도·상태 | F2·SG2·SH5·base 구성 | 속도 입력은 유한 위치 이동 작업과 다름. 만료·odometry·정지 관측 필요 |
| navigation 목표 | 별도 navigation 구성 | 지도·localization·실제 Nav2 연결과 목표 결과를 검증한 뒤 선언 |
| Sapiens 모드 선택 | AS-02 | 모드 접수·활성화 확인. 자세·이동의 물리 완료와 구별 |
| 중단·재조정 | 각 모델에서 정의할 경로 | 요청과 실제 정지·보유 상태·잔류 명령을 별도로 확인 |

JTC는 action과 topic 경로의 결과 통지가 다르다. RX 작업 완료를 다루는 경로에서는 설치된 controller의 action·관측 의미를 명세에 연결한다.[^4] 동일 팔 JTC에 gripper가 포함된 모델은 별도 gripper 작업이 기존 팔 목표를 덮어쓰지 않도록 자원·명령 조율이 필요하다.

leader/teleop 명령 스트림은 별도의 제어권 세션으로 정의하고 자동 공정의 명령원과 배타적으로 사용한다. 허가된 세션 안의 고주기 제어는 solutions에서 처리하고, platform은 세션·자원·중단·복구 상태를 관리한다.

## 7. 교정·모드·장치 요구

| 구성군 | 코드에서 확인된 연결 예 | 프로파일에 고정할 내용 |
|---|---|---|
| OpenManipulator-X·OMX | serial, 1 Mbps 설정 | 실제 장치 식별, ID·모델·firmware, 관절 순서·영점·방향·한계·tool |
| OMY-3M/F3M | 팔 `/dev/ttyAMA2` 6.25 Mbps, end-unit `/dev/ttyAMA4` 4 Mbps 예 | 팔/툴 연결 소유권, end-unit 매핑, gripper·TCP·하중·교정 |
| OMY-L100 | USB serial, 4 Mbps 예 | leader/follower 역할, offset·reverse joint·effort/spring 설정 |
| FFW | `/dev/follower`, leader 좌/우, 일부 base/sensor의 추가 USB serial; 4 Mbps 예 | 연결 역할별 실제 장치, 손·베이스·센서 구성, 모드·controller 소유권 |
| FFW 베이스/손 | swerve·odometry·pressure 구성 | 조향 영점·바퀴/차체 geometry·좌표계·지도, 손 transmission·압력 교정 |
| K1 | 팔·다리·IMU·hat의 e2d2udp 경로, 6 Mbps 설정값 | 실제 NIC·장치 endpoint·여섯 역할, 관절/정책 배열·IMU 축·RC·policy 해시 |

장치 경로와 주소는 현재 코드의 예이며 현장 값을 자동 할당하지 않는다. 같은 모델에서도 ‘로컬 하드웨어를 RX가 구동하는 방식’과 ‘이미 구동 중인 장비 컨트롤러의 ROS 인터페이스로 연결하는 방식’을 구분한다. 한 하드웨어 연결의 driver 소유자는 하나로 둔다.

## 8. 기동·중단에서 확인된 중요 차이

DHI의 start 경로에는 상태 읽기·명령 동기화·장치 쓰기와 구성에 따른 torque enable이 있고, stop에는 torque disable 호출이 있다. 일부 FFW launch는 init_position 기본값이 true다. 그러므로 controller_manager/driver의 시작·종료를 단순한 읽기·연결 작업으로 분류하지 않는다.[^5]

기본 등록은 소프트웨어와 모델을 준비하는 단계다. 실제 driver configure/activate·초기 자세·토크·mode 전환은 해당 모델의 시작 효과와 기구 상태를 확인한 뒤 실행하는 별도 경계로 둔다. 종료 시에도 모든 모델에 일괄 torque off를 적용하지 않고 하중·소재·자세에 맞는 정지·유지·해제 조건을 정한다.

DHI 소멸자도 stop을 호출한다. 따라서 토크로 소재·자세를 유지해야 하는 동안에는 정상 절차에서 DHI를 종료하지 않는다. 토크 해제가 가능한 지지·소재 이관 상태를 확인하거나 검증된 외부 유지 수단으로 넘긴 뒤 종료한다. 그 전에는 제어를 유지하거나 계획된 종료를 보류해야 한다. 강제 종료·정전까지 이 소프트웨어 절차가 막아준다는 뜻은 아니다.[^6]

## 9. 필수 전이 의존성 묶음

| 묶음 | 포함·참조할 항목 | 적용 |
|---|---|---|
| DEP-BASE | DYNAMIXEL SDK·DHI·dynamixel_interfaces·ROS 제어·pluginlib·메시지·URDF/xacro | 모든 자사 기본 지원 |
| DEP-OM | open_manipulator와 자체 controllers·robotis_interfaces·관련 MoveIt 구성 | OM 계열 |
| DEP-FFW | ai_worker·ffw controllers/manager·robotis_interfaces·robotis_hand 등 | FFW 모델별 기능 |
| DEP-MOBILE | swerve·navigation2·nav2_bringup·SLAM·laser/camera 구성 | 이동·navigation 기능 |
| DEP-AS | ai_sapiens_interfaces·controllers·sim2real·ONNX Runtime·Eigen·yaml-cpp·정책 자산 | AS-01/02에서 필요한 기능별 연결 |
| DEP-SENSOR/GPU | RealSense·ZED·lidar·해당 GPU/Jetson·추론 의존 | 실제 장착·운영 모드에 맞는 이미지 variant |

기본 제품에는 지정 자사 모듈을 포함한다. 기능별 기동 여부와 하드웨어별 variant를 나누더라도 자사 모델을 선택 설치 플러그인으로 누락하지 않는다. 로컬 main·기존 Docker의 jazzy와 외부 라이브러리를 통합한 lock 조합은 아직 검증되지 않았다.

## 10. 검증 범위와 현재 상태

| 검증 ID | 범위 | 확인할 것 |
|---|---|---|
| V0 | 의존·빌드·registry | 필수 패키지·정책 자산·모델 목록·버전·라이선스·중복 package 검출 |
| V1 | 구성·launch | 인자 선언·전달, real/mock/sim 선택, joint 목록·타입·namespace·device binding |
| V2 | 계약·모의 | 입력·결과·미지원·오래된 관측·중복·불명·중단·경합 |
| V3 | 실장비 단위 | 실제 ID·교정·모드·관측·동작·그리퍼/손·베이스·토크의 의미 |
| V4 | 기동·종료·복구 | init_position·controller 활성·재시작·정지·잔류 명령·소재 유지 |
| V5 | 자원·시간 | 모델별 주기·누락·지연·CPU/GPU·메모리·장치/네트워크 부하 |
| V6 | 현장 공정 | 작업자·지그·문·척·소재와 결합한 완료·개입·인수 |

현재 모든 지원 행의 V0–V6 **실행 검증은 미수행**이다. 별도로 코드·설정 읽기 근거가 존재한다. 지원 의무, 소스 존재, 빌드 통과, 실물 적합성, 현장 인수를 서로 다른 상태로 기록한다. `required=true`와 `hardware_verified=false`가 함께 있을 수 있다.

첫 실물 작업은 선정한 로봇에서 시작하더라도 다른 자사 제품의 기본 지원 의무를 제거하지 않는다. 어느 이미지가 어느 모델·모드·기능을 지원한다고 출시하려면 해당 범위의 검증 결과를 갖춰야 한다.

## 11. 기본 registry 명세에 다음으로 넣을 필드

각 행에 profile ID, 제품군·모델/revision·역할, 저장소/패키지 버전, launch·controller 집합, driver 소유 방식, API/관측 매핑, 장치 역할, 교정·정책 자산, 시작·종료 효과, 필요한 이미지 variant, 필수 검증·현재 증거 수준을 넣는다. 현재 이 구조를 문서로 정의하며 실행 가능한 registry 파일은 만들지 않는다.

## Sources

[^1]: [20개 controller 설정 추출](/Users/ojaehong/RX_automation/rx_ws/references/own_controller_inventory_2026-09-09.json), [40개 하드웨어 xacro 추출](/Users/ojaehong/RX_automation/rx_ws/references/own_hardware_inventory_2026-09-09.json). 2026-09-09 로컬 HEAD·해시 포함. 반복 wildcard YAML 항목을 보존한 읽기이며 ROS 로딩·기동 미수행.
[^2]: [FFW F2 controller 설정](/Users/ojaehong/RX_automation/ai_worker/ffw_bringup/config/ffw_f2_follower/ffw_f2_follower_ai_hardware_controller.yaml), [SH5 설정](/Users/ojaehong/RX_automation/ai_worker/ffw_bringup/config/ffw_sh5_rev1_follower/ffw_sh5_follower_ai_hardware_controller.yaml), [navigation launch](/Users/ojaehong/RX_automation/ai_worker/ffw_navigation/launch/navigation.launch.py). 설정·경로 사실에 한정.
[^3]: [K1 controller](/Users/ojaehong/RX_automation/ai_sapiens/ai_sapiens_bringup/config/k1_rev1/k1_rev1_controllers.yaml), [K1 기동](/Users/ojaehong/RX_automation/ai_sapiens/ai_sapiens_bringup/launch/k1.launch.py), [sim2real 모드 설정](/Users/ojaehong/RX_automation/ai_sapiens/ai_sapiens_sim2real/config/k1_config.yaml), [모드 인터페이스](/Users/ojaehong/RX_automation/ai_sapiens/ai_sapiens_sim2real/src/controllers/mode_ros_interface.cpp).
[^4]: ros-controls, [JTC Jazzy 인터페이스](https://control.ros.org/jazzy/doc/ros2_controllers/joint_trajectory_controller/doc/userdoc.html), action/topic·오차·결과 구분, 2026-09-09 확인. 설치된 패키지 버전과 실제 결과는 별도 확인.
[^5]: [DHI start/stop](/Users/ojaehong/RX_automation/dynamixel_hardware_interface/src/dynamixel_hardware_interface.cpp:550), [BG2 launch](/Users/ojaehong/RX_automation/ai_worker/ffw_bringup/launch/ffw_bg2_follower_ai.launch.py:51). 초기화·종료 효과의 소스 근거이며 실제 동작·정지 보장이 아님.
[^6]: [DHI 소멸자](/Users/ojaehong/RX_automation/dynamixel_hardware_interface/src/dynamixel_hardware_interface.cpp:49), [stop의 torque disable 호출](/Users/ojaehong/RX_automation/dynamixel_hardware_interface/src/dynamixel_hardware_interface.cpp:593). 정상 종료 전 물리 유지 상태 확인이 필요한 근거.
