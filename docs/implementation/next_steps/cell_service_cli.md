# phase76 CLI 진입점·DTO 결정

부모 승인에 따라 설계 후 구현을 진행했다. 기존 `rx-executor-service CONFIG`를 유지하고 같은 executable에 명시적인 `cell init CONFIG` / `cell run CONFIG`를 추가한다. 새 구현 위치는 `runtime/rx-executor/src/bin/service/cell_cli.rs`다. 별도 자동 감지, 새 UI path 전달 API 또는 새 임의 executable 경로는 만들지 않는다.

CellConfig schema는 `rx.executor-cell-service.v1`이며 service_root, expected_service: assignment_journal::Identity, platform(TLS endpoint 및 세 pinned files), engine pin, 선택적 세 timing options로 구성한다. run/visit/peer_boot/clock_id는 받지 않는다. service scope가 기존 PeerPin의 고정 신원을 공급하고, 실제 run 프로세스가 peer boot·Linux clock을 생성한다. 옵션은 기존 service::Options로 변환하며 SerialProduction만 사용한다.

init은 root owner를 유지한 채 root를 정규화하고 파일 pins를 확인한다. create_new/fsync한 `cell-installation.json`에 전체 normalized configuration digest·expected Identity·root를 먼저 고정하고, `assignment.sqlite3`를 초기화한다. 부분 설치를 덮어쓰거나 유실 원장을 새로 만들지 않는다. config digest에 기본 옵션을 명시하여 omitted-default와 explicit-default는 같게 취급한다. 변화한 TLS/engine/root/Scope/옵션을 조용히 채택하지 않는다.

run은 owner → installation pin 검증 → AssignmentJournal required-open/current run-file 검증 → 배포 파일 pins → 실제 clock/새 peerboot → Client.connect 순서다. 이후 `CellService<F>::new(Client, AssignmentJournal<SqliteRepository>, root, PinnedPlanner, Arc<dyn Clock>, Options)`에 연결한다. initial_status 및 run(shutdown, updates)를 사용하고 `Report.status.phase == Stopped`만 정상 종료로 처리한다.

idle signal은 가짜 pause 없이 CellService의 Stopped, active signal은 기존 RunService의 영속 stop/정리 경계를 따른다. 접속 도중 signal은 startup-interrupted 오류이고, Attention은 비정상 종료다. 상태는 optional run/attachment와 현재 서비스 상태를 watch로 출력한다. poll 10–1000ms, grace/stop 100–60000ms의 기존 범위를 유지하고 CellService transient backoff 최대1000ms, Client connect/RPC 각각2초를 사용한다. 배포 supervisor 등록은 별도이며 RequiresPlatformAuthority/restart_limit=0 및 고정 config argument를 유지해야 한다.

상세한 최종 DTO/경계/제품 제한은 [CELL_CLI.md](/Users/ojaehong/RX_automation/rx_ws/rx-solutions/runtime/rx-executor/CELL_CLI.md)에 정리했다. 새 전용 CLI 시험은 실제 Linux 제품 프로세스에 test-harness before-connect probe를 넣어 init의 통신0회와 중복/부분설치/원장손상/config·파일pin 변경의 접속 전 거부를 확인하도록 작성했다. 실제 P–S 연결·Idle/active signal 인수는 부모 작업의 범위다. 이 작업에서는 빌드·시험·서버 실행·커밋을 하지 않는다.
