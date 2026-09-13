# OMY Authority Provider 재검토

2026-09-13. 현재 제품/고정 ROBOTIS 소스와 공식 Jazzy 문서를 읽은 감사다. 코드 변경·빌드·robot/controller 기동·종료·장비 통신은 수행하지 않았다.

## 결론

**제품 Authority Provider의 근거 수집·제어 경계는 아직 완성되지 않았다.** 현재 Builtin JTC 차단은 유지하는 것이 맞다. 다만 해결책을 “ROS에서 bool 다섯 개를 채우기”로 잡으면 안 된다. controller 식별/관측, command owner의 실제 배제, OMY의 현지 조건·지지, 어떤 구성요소를 종료하는지에 대한 판단을 분리해 검토해야 한다.

현재 [AuthoritySnapshot](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/runtime/rx-host/src/ros_jtc/profile.rs:109)은 controller_session, 단일 observed_at/uncertainty, resource/condition 집합과 exclusive_control/no_external_goals/control_available/support_stable/client_drop_allowed를 한 객체로 받는다. validate는 resource 일치와 시각만 검사한다. 각 bool의 원천·관측 가능 범위·generation 상관·UNKNOWN을 타입으로 검증하지 못한다.

[Jtc::ready](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/runtime/rx-host/src/ros_jtc/adapter.rs:212)는 이 값을 실제 제출 guard로 쓰고, [handover/shutdown](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/runtime/rx-host/src/ros_jtc/adapter.rs:360)는 외부 goal/지지/drop 값으로 잔류 작업·종료 가능성을 판단한다. 현재 `UnavailableAuthority`는 Guard 오류를 내며, [Builtin](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/runtime/rx-host/src/service/factory.rs:115)은 JTC_CONTROL_PROVIDER_NOT_CONFIGURED로 거부한다. 이를 site JSON의 true나 ROS READY로 바꾸는 것은 미결을 해결하는 구현이 아니다.

## 고정 소스와 OMY 범위

원본 pin은 [.cache/robotis/source-lock.json](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/.cache/robotis/source-lock.json)과 [catalog](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/catalogs/robotis-support.v1.json)에 있다.

| 저장소 | 현재 commit |
|---|---|
| DynamixelSDK | `2ded684dff05a40ac78d6a16105c6ddc1b3b9930` |
| dynamixel_hardware_interface | `6bb5f93ecad1fe3c231e3ece580344e8f0a6efc3` |
| open_manipulator | `9187eca0920458be04d2399906388f55242f81f1` |
| dynamixel_interfaces | `5704b4be9149f34f0214ae99c31edf6a5a103b24` |

OMY는 단일 구성명으로 합치지 않는다. catalog의 OM-05=`omy_3m`, OM-06=`omy_f3m`은 arm joint1–6 position JTC 선언이다. OM-06은 별도 gripper_controller/rh_r1_joint도 갖는다. follower의 gripper 포함 7관절·leader effort 구성을 이 6관절 arm과 섞지 않는다. 아래 OMY 3M 파일 관측은 사용자의 실제 OMY 세부형식 확인을 대신하지 않으며, 기존 bridge 예시/모의시험의 OM-06 역시 실장비 식별 근거가 아니다.

[OMY 3M controller YAML](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/.cache/robotis/open_manipulator/open_manipulator_bringup/config/omy_3m/hardware_controller_manager.yaml:1)은 400Hz, arm_controller JTC, position command, position/velocity state, allow_partial_joints_goal=true를 선언한다. 이는 선언값이며 실제 loop 성능·정확도·가용성 검증이 아니다. OMY F3M 파일은 [별도 원문](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/.cache/robotis/open_manipulator/open_manipulator_bringup/config/omy_f3m/hardware_controller_manager.yaml:1)으로 고정해야 한다.

ROS2 control/JTC의 vendored 구현 commit은 이번 로컬 원본 목록에서 확인하지 못했다. 아래 공식 Jazzy 문서는 인터페이스 의미 확인이며 실제 이미지의 정확한 binary/package version에 대한 증거가 아니다. 이후 배포 pin에는 실제 dpkg/패키지 버전·바이너리 digest도 포함해야 한다.

## 얻을 수 있는 사실과 얻지 못하는 증명

| 축 | 현재 실제 읽을 수 있는 원천 | 그 값만으로 증명하지 못하는 것 |
|---|---|---|
| controller 구성/활성 | bridge [inspect](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/native/ros-jtc/bridge.cpp:148): ListControllers의 name/type/state/claimed_interfaces/is_chained와 action service readiness를 검사한다. | 같은 이름으로 재생성된 controller의 incarnation, DHI/모터 reboot 연속성, 외부 입력 부재. bridge가 controller_generation_known=false와 physical_readiness_proven=false를 명시하는 것은 타당하다. |
| controller generation | RX bridge_instance와 native journal의 original invocation은 있다. | bridge process UUID는 controller/hardware generation이 아니다. 현재 ROS ListControllers와 DHI 상태 메시지에는 검증된 OMY 전체 controller/device boot 연속성 token이 없다. 조용한 reboot까지 검출했다고 주장할 수 없다. |
| exclusive owner | controller claimed_interfaces는 controller manager 내부의 interface 할당 관측이다. | 어느 ROS action client가 명령할 수 있는지, trajectory topic·controller switch·직접 DHI service·별도 serial writer를 배제했다는 증명이 아니다. [공식 ControllerInfo 정의](https://control.ros.org/jazzy/doc/api/structhardware__interface_1_1ControllerInfo.html)도 claimed interfaces를 controller의 목록으로 설명한다. |
| 외부 goal/trajectory | bridge는 자신이 보낸 goal UUID/응답/pending 원장만 알고 있다. | 전체 시스템의 명령 부재를 열거하지 않는다. JTC는 action과 topic 두 입력이 있고 새 action이 기존 goal을 preempt할 수 있다. 한 active action이라는 성질은 한 명령 소유자라는 뜻이 아니다. [공식 JTC 문서](https://control.ros.org/jazzy/doc/ros2_controllers/joint_trajectory_controller/doc/userdoc.html#preemption-policy). |
| clock/freshness | RX [strict.hpp](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/native/ros-jtc/strict.hpp:118)은 CLOCK_BOOTTIME을 사용한다. DHI 상태는 [read](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/.cache/robotis/dynamixel_hardware_interface/src/dynamixel_hardware_interface.cpp:648)에서 ROS `this->now()`로 stamp한다. | ROS stamp를 RX BOOTTIME으로 간주할 수 없다. 수신 때 새 timestamp를 붙여 오래된 native 값을 fresh로 만들면 안 된다. 동기 read 취득 구간 또는 검증된 clock/age 변환이 필요하다. |
| OMY 통신·모터 상태 | [DynamixelState.msg](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/.cache/robotis/dynamixel_interfaces/msg/DynamixelState.msg:1)의 comm_state, id, torque_state, dxl_hw_state 및 joint state를 읽을 수 있다. | 토크 enabled/통신 OK/관절 속도 0이 소재 지지, 잔류 command 없음, 위험 구역·interlock 충족, client drop 허가를 뜻하지 않는다. message에 전체 boot/owner/지원 하중 proof가 없다. |
| 우회 쓰기 | DHI는 [set data/reboot/torque service](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/.cache/robotis/dynamixel_hardware_interface/src/dynamixel_hardware_interface.cpp:375)를 별도로 만든다. SDK [Linux port](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/.cache/robotis/DynamixelSDK/c++/src/dynamixel_sdk/port_handler_linux.cpp:205)는 O_RDWR/O_NOCTTY/O_NONBLOCK으로 연다. | 읽은 SDK 구현의 is_using_는 객체 상태이며 파일시스템 전체 command-owner proof가 아니다. 이 경로에서 프로세스 간 flock/TIOCEXCL 배제는 확인되지 않았다. ROS resource claim만으로 직접 device 접근을 차단하지 않는다. |
| lifecycle/drop | DHI [activate/start](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/.cache/robotis/dynamixel_hardware_interface/src/dynamixel_hardware_interface.cpp:538)는 read/sync command/write/torque enable을 수행한다. [stop](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/.cache/robotis/dynamixel_hardware_interface/src/dynamixel_hardware_interface.cpp:593)은 torque disable을 호출하고 destructor도 stop을 부른다. | activate/stop/destructor를 순수한 메타데이터 동작으로 다룰 수 없다. bridge client 종료 허가를 DHI/controller 종료 또는 torque-off 허가로 확대하면 안 된다. |

OMY 3M [ros2_control xacro](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/.cache/robotis/open_manipulator/open_manipulator_description/ros2_control/omy_3m_position.ros2_control.xacro:3)는 실제 DHI plugin, port 기본값, `disable_torque_at_init=true`, HAT 전원 관련 설정을 갖는다. 이 소스는 startup effect 검토가 필요하다는 근거이지 그 설정을 지금 적용하라는 지시가 아니다. [launch](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/.cache/robotis/open_manipulator/open_manipulator_bringup/launch/omy_3m.launch.py:35)의 mock/sim 선택과 실제 설정도 구분해야 한다.

## 최소 제품 Provider 분리 제안

새 거대 framework보다 기존 Jtc에 들어오는 사실을 세 경계로 나누는 것이 우선이다.

1. **ControllerObservation:** 실제 model/support ID·CM/controller/hardware 식별, lifecycle/claimed interfaces, service 상태, 관측 구간과 source generation. unknown은 명시적인 값으로 남긴다. manager process 재시작·controller 재load·DHI/device reset은 다른 변화로 기록하고, locally generated UUID 하나를 모든 세대의 증명으로 쓰지 않는다.
2. **CommandOwnership:** 어떤 resource와 action/topic/lifecycle/direct-device 입력을 누가 실제로 독점하는지에 대한 배포/소유 근거. 등록한 유일 command gateway, endpoint 접근 정책·device 접근 제한과 살아 있는 owner를 대조한다. 발견된 ROS node 수나 단순 ACL 파일 존재만으로 exclusive=true를 만들지 않는다. 배제 범위 밖의 외부 writer가 있으면 Unknown/거부다. P의 grant/permit와 이 현지 배제는 별도다.
3. **LocalConditionsAndLifecycle:** OMY의 검증된 현지 condition 원천과 `support` 근거, 그리고 명시적인 종료 대상(bridge client / controller / hardware)에 대한 허용 관측을 구분한다. 각 항목에 source/취득 시각/불확실성/유효기간·미확인 이유를 붙인다. 최종 Guard·handover·client drop 판단은 adapter가 해당 동작에 필요한 항목만 조합한다.

`protection()`은 계속 저장/Host gate와 독립된 반응 경계로 유지한다. Provider가 오류를 읽었다는 사실과 실제 OMY 현지 hold/정지/지지 반응이 배정·실행·관측됐다는 사실은 분리한다. 검증된 반응 구현이 없으면 noop/임의 torque disable을 보호 완료로 표시하지 않는다.

기존 boolean interface는 추상화 경계로는 쓸 수 있지만 현재는 출처 책임이 지나치게 크다. 최소 변경은 typed observation 결과를 받고 **Unknown을 표현·전파하는 mapping**을 먼저 만드는 것이다. 동일 observed_at으로 서로 다른 수명/출처의 조건을 갱신하지 않는다. support/drop까지 전부 true여야 관측 자체가 가능한 설계도 피한다: 진단 조회, original result lookup, 새 submit, client 종료는 각기 필요한 근거가 다르다.

특히 Jtc가 종료하는 것은 현재 bridge transport다. DHI의 실제 소유자·수명과 분리된 deployment임을 확인하지 않고 `client_drop_allowed`에 하드웨어 정지 의미를 담지 않는다. support_stable은 OMY 자세·tool·소재·부하에 관한 외부 검증 입력이 남아 있으므로 현재 source만으로 구현 완료할 수 없다.

## 최소 검증과 이번 초안의 상태

- 모의 Provider에서 controller 이름/claim이 같아도 generation 변경·expiry·clock 불일치·Unknown이면 새 submit 0을 확인한다.
- 두 번째 action client와 trajectory topic 입력, controller switch 및 DHI/direct-device 우회가 owner 범위에 어떻게 검출·배제되는지 각기 검증한다. bridge 자기 goal 목록만으로 no_external_goals를 통과시키는 반례를 둔다.
- 오래된 motor/joint 상태를 새 ROS/수신 timestamp로 포장해도 condition freshness를 얻지 못하는지 검사한다.
- 결과 lookup과 새 submit을 분리하여 source/control 연속성이 상실되면 original UNKNOWN을 보존하고 새 goal ID/send 0을 확인한다.
- bridge close와 DHI deactivate/destructor를 분리한 모의시험을 둔다. support/drop Unknown에서 하드웨어 종료·토크 변경 0이며, 허용된 bridge 종료도 별도의 실제 child-exit로 확인한다.
- 첫 실물 인수 전에 실제 OMY 세부형식·말단/tool·하중·배선/전원·보호/지지 원천 및 driver lifecycle effect를 고정한다. OM-05/06, follower/leader, 다른 자사 모델의 근거를 대신 사용하지 않는다.

지금 완료된 것은 통신 bridge, Jtc의 원 invocation/원장 경계, 원문 package 검증 및 모의 경계시험이다. **제품용 controller generation/exclusive ownership/전체 외부 goal 배제/물리 support·drop/protection 원천은 미결**이다. 초안 마무리에서는 이를 명시하고 Builtin 차단을 유지한다. 현재 소스만으로 올바른 product Provider를 완성했다고 결론내리지 않는다.
