# 스택 선택을 위한 자사 코드·컨테이너 조사

조사일 2026-09-09. 범위는 로컬 저장소의 선언·구성·선택된 제어 경로와 공식 문헌이다. 코드를 수정하거나 빌드·컨테이너·로봇을 실행하지 않았다.

## 로컬 기준점

| 저장소 | HEAD | 확인한 핵심 |
|---|---|---|
| DynamixelSDK | `2ded684dff05a40ac78d6a16105c6ddc1b3b9930` | ROS package 4.0.5, c++ CMake 17, 네이티브 라이브러리 |
| dynamixel_hardware_interface | `6bb5f93ecad1fe3c231e3ece580344e8f0a6efc3` | 1.5.2, hardware_interface/pluginlib/rclcpp/SDK/interfaces, CMake 기본값 14 |
| open_manipulator | `9187eca0920458be04d2399906388f55242f81f1` | 5.1.1, OMY/OMX launch·제어·MoveIt, Jazzy Docker |
| ai_worker | `2e29aae2dee9926691922fc0fa58d97ad88e068f` | FFW 2.2.5, 여러 모델 launch, 제어·navigation, amd64/arm64 Docker 차이 |
| ai_sapiens | `7d62dff281f02b6265ebe07db6c0ae32ba8de381` | 0.1.2, k1 launch, DynamixelHardware 참조, C++/ONNX Runtime |

모두 main checkout이며 읽기 시 작업트리는 깨끗했다. CMake 언어 값은 선언이며 최종 컴파일 옵션·전체 호환성 검증 결과가 아니다. [패키지별 상세 목록과 선택 파일 해시](stack_local_inventory_2026-09-09.json)

## 재현 가능한 직접 근거

| 파일 | 관측한 내용 |
|---|---|
| [DHI package.xml](/Users/ojaehong/RX_automation/dynamixel_hardware_interface/package.xml) | ROS hardware_interface·pluginlib·SDK·dynamixel_interfaces 의존 |
| [DHI CMake](/Users/ojaehong/RX_automation/dynamixel_hardware_interface/CMakeLists.txt) | 공유 라이브러리와 hardware plugin export |
| [DHI 의존 목록](/Users/ojaehong/RX_automation/dynamixel_hardware_interface/dynamixel_hardware_interface_ci.repos) | DynamixelSDK와 dynamixel_interfaces, main 참조 |
| [OpenManipulator 의존 목록](/Users/ojaehong/RX_automation/open_manipulator/open_manipulator_ci.repos) | DHI·robotis_interfaces |
| [AI Worker 의존 목록](/Users/ojaehong/RX_automation/ai_worker/ai_worker_ci.repos) | DHI·robotis_hand·robotis_interfaces |
| [AI Sapiens 의존 목록](/Users/ojaehong/RX_automation/ai_sapiens/ai_sapiens_ci.repos) | DHI 참조 |
| [OpenManipulator Docker](/Users/ojaehong/RX_automation/open_manipulator/docker/Dockerfile) | Jazzy 기반, jazzy branch clone, RealSense·s6·rmw_zenoh_cpp |
| [AI Worker amd64 Docker](/Users/ojaehong/RX_automation/ai_worker/docker/Dockerfile.amd64) | Jazzy·RealSense, 추가 자사 저장소와 Python 도구 |
| [AI Worker arm64 Docker](/Users/ojaehong/RX_automation/ai_worker/docker/Dockerfile.arm64) | Torch/CUDA 기반 이미지, Jetson/L4T·ZED·RealSense 처리 |
| [AI Sapiens Docker](/Users/ojaehong/RX_automation/ai_sapiens/docker/Dockerfile) | Jazzy·ONNX Runtime 1.23.2·rmw_zenoh_cpp. 이 파일 자체에 colcon build 단계는 보이지 않음 |
| [AI Sapiens sim2real CMake](/Users/ojaehong/RX_automation/ai_sapiens/ai_sapiens_sim2real/CMakeLists.txt) | ONNX header/library 탐색과 없을 때 FATAL_ERROR |
| [K1 팔 제어 설정](/Users/ojaehong/RX_automation/ai_sapiens/ai_sapiens_description/ros2_control/k1_rev1/k1_left_arm.ros2_control.xacro) | dynamixel_hardware_interface/DynamixelHardware 참조 |

## 통합 시 별도로 설계할 문제

1. `.repos`는 main을 참조하지만 Dockerfile은 jazzy를 clone한다. 현재 HEAD의 package 버전과 실제 이미지의 소스 조합을 동일시하지 않는다.
2. 같은 공통 의존 저장소를 세 로봇 레포 경로에 중복 배치하면 ROS package 중복 문제가 생길 수 있으므로 하나의 해석된 의존 집합을 만든다.
3. ROS package.xml, CMake의 수동 라이브러리 탐색, Docker의 apt/pip/외부 SDK 설치를 함께 읽어 전이 의존성을 닫는다.
4. ROS C++ 플러그인과 DYNAMIXEL SDK는 제어 프로세스 내부의 라이브러리 경계를 유지한다. 원본 레포 수대로 독립 통신 서비스를 만들지 않는다.
5. 기존 Compose는 host network·ipc·privileged·/dev 공유와 실시간 관련 설정을 포함한다. 실제 납품에 필요한 권한·장치·커널 조건을 별도로 정한다.
6. `.bashrc`의 ROS/RMW 설정이 모든 비대화형 서비스에 적용되는지 확인해야 한다. 컨테이너 서비스 명세에서 환경을 명시한다.
7. AI Worker의 모든 기능이 모든 amd64/arm64 보드에서 동일하게 실행된다는 근거는 없다. 모델·운영 모드·추론·카메라·드라이버별 지원 조합이 필요하다.
8. 기본 지원 요구는 확정됐지만 이번 읽기 조사로 어느 자사 모델의 RX 작업 계약 적합성이나 실물 동작을 검증한 것은 아니다.

## 문헌의 주요 확인 사항

- [Rust ownership](https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html)과 [unsafe](https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html): 신규 도메인 코드의 메모리 관리 이점과 외부 코드 경계 구분.
- [rclrs 원본](https://github.com/ros2-rust/ros2_rust): ROS service/action 지원, 빠른 변화와 안정성 보장 부재 설명, Jazzy 설치 경로. Rust에서 ROS를 사용할 수 없다는 결론을 내리지 않음.
- [ROS 공식 배포 목록](https://github.com/ros2/ros2_documentation/blob/rolling/source/Releases.rst): Jazzy 2029-05, Lyrical 2031-05 지원 종료 표기. 이번 자사 Docker의 기반은 Jazzy.
- [tonic 0.14.6](https://docs.rs/tonic/0.14.6/tonic/)와 [gRPC Rust 저장소](https://github.com/grpc/grpc-rust): Rust gRPC 경로, master의 breaking-change 안내. 안정 릴리스 고정 필요.
- [Docker 프로세스 관리](https://docs.docker.com/engine/containers/multi-service_container/), [자원 조건](https://docs.docker.com/engine/containers/resource_constraints/), [USB/IP](https://docs.docker.com/desktop/features/usbip/): 컨테이너별 생명주기와 장치·호스트 제약 구분.

이 사실에서 도출한 추천은 [스택·컨테이너 제안](../docs/12_stack_and_container_proposal.md)에 있다. 기술 선택의 우선순위는 설계 판단이며 벤치마크 점수나 납품 검증 결과가 아니다.
