# RX 계약·프로토콜 방법 조사와 선택 근거

대상: 두 컨테이너 기반 RX의 첫 계약 기준판. 사실과 RX 설계 판단을 분리한다.

## 1. 결론과 평가 범위

RX에는 **명시적인 상태 전이·조건·증거를 가진 비동기 작업 계약**, **양쪽 프로세스의 영속 수신/전달 기록**, **장비별 관측·중단·재시작 능력 선언**을 결합하는 방법이 가장 적합하다. 내부 전송은 gRPC/Protobuf, 고속 제어는 장비 측, 운영 화면은 HTTP/JSON/SSE로 분리한다. 이 결론은 아래 요구와 반례에 대한 설계 판단이며 성능 측정 결과가 아니다.

평가 순서는 다음과 같다. 앞 조건을 충족하지 못하면 뒤 장점으로 상쇄하지 않는다.

1. 응답 유실·재시작에서 물리 동작을 중복시키거나 완료를 꾸며내지 않는가?
2. 자사 유한 동작·leader/follower·속도 제어·정책 모드·토크 수명주기를 모두 표현하는가?
3. ROS 비의존 Rust 코어와 두 RX 컨테이너 경계를 지키는가?
4. 현장 장애를 추적하고 사람이 복구할 수 있는가?
5. 현재 셀에 필요한 운영 부담과 향후 확장 비용이 합리적인가?

‘모든 메서드’는 유한한 목록으로 증명할 수 없다. 조사 범위를 산업 정보/상태 표준, 명세 기법, 내구 실행, 전송, 스키마/호환성의 다섯 부류로 나누어 대표 표준과 최근 대안을 검토했다. 유료 ISA/IEC 본문 전체, 모든 상용 제품, 모든 버전의 구현을 검증했다고 주장하지 않는다. ISA-88/95 관련 구체 비교에는 공개 OPC companion specification을 사용했다. 검색 요약만 확보한 항목을 규범 결정의 단독 근거로 사용하지 않는다.

## 2. 산업 모델에서 가져올 것

| 방법 | 원문에서 확인한 범위 | RX 적용 판단 |
|---|---|---|
| ISA-95 Job Control / Machinery Job Management | 저장·시작 허용·실행·중단·종료와 job 결과를 구분한다. StoreAndStart 성공 직후 상태는 AllowedToStart일 수 있다.[^1] | 공정 job/run과 장비 operation의 계층 분리, 실행 허용과 실제 시작 구분을 채택. 장비의 개별 축 명령까지 MES job 모델로 강제하지 않는다. |
| ISA-88 계열 / OPC PackML 1.01 | 장비 단위의 실행·holding·held·suspending·suspended·완료 등의 상태와 전이 모델을 제공한다.[^2] | 공정·장비 상태 표시와 원인 분류에 참고. 모든 RX 작업을 같은 PackML 상태로 바꾸면 제어 스트림·드라이버 수명주기 의미가 손실되므로 내부 단일 상태기계로 채택하지 않는다. |
| PLCopen Motion Control Part 1 v2.0 | 모션 명령의 Busy/Done/CommandAborted/Error와 축 상태를 명세한다.[^3] | 요청 수명과 축 상태를 구별하는 방법을 채택. 일반 Stop 완료를 셀의 소재 지지·문·레이저까지 포함하는 안전 보장으로 확대하지 않는다. |
| OPC UA Robotics 1.02 | TaskControlStateMachineType에 감시뿐 아니라 선택적 원격 제어, Load/Start/Stop과 stop mode가 있다.[^4] | ‘OPC Robotics는 감시만’이라는 오래된 일반화를 배제한다. 장비가 해당 conformance unit을 실제 제공하는지 확인한 뒤 binding 가능. 내부 계약 전체를 대체할 근거는 아니다. |
| VDA 5050 3.0.0 | 2026-03 배포판은 자유 주행·zone, 동작 상태·blocking type을 확장하고 재전송과 내용 변경의 구별을 보강했다.[^5] | 이동 로봇 연동 후보로 유지. order/action 식별·revision·동시성 모델은 참고하되 CNC·휴머노이드 토크 제어까지 VDA order로 강제하지 않는다. |
| AAS | 자산 정보와 submodel의 구조·의미 및 별도 API 규격을 제공한다.[^6] | 장비 catalog·능력·교정/버전 metadata의 외부 표현 후보. 자산 기술이 명령 전달/실행의 내구성을 대신하지 않는다. |
| W3C WoT TD 1.1 | properties/actions/events와 protocol binding을 분리한다.[^7] | 능력과 전송의 분리 원리를 채택. 이름만 공통인 action에 물리 완료 의미를 자동 부여하지 않는다. |

산업 표준의 값어치는 RX 고유 용어를 줄이고 외부 시스템과 접점을 만드는 데 있다. 실제 제어기 옵션·OEM PLC 프로그램·관측 신호가 없는데도 표준 명칭만으로 장비 지원을 선언할 수는 없다.

## 3. 명세와 검토 방법

| 방법 | 이점 | 한계·선택 |
|---|---|---|
| Design by contract / assume-guarantee | 선행 조건·결과 조건·불변식·환경 가정을 계약 카드로 명시 | RX의 기본 작성법으로 채택. 가정이 현장에서 충족되는지는 별도 검증한다. |
| 상태 전이표·statecharts / SCXML | 중첩 상태·사건·guard·전이를 명시할 수 있다.[^8] | 전이표를 규범으로 사용. SCXML 실행기 자체는 필수가 아니다. BT 상태와 물리 결과를 같은 상태 변수에 섞지 않는다. |
| TLA+ / PlusCal / TLC | 비동기 주체·유실·재시작의 상태 공간과 invariant 검토에 적합하다.[^9] | 문서에 변수·전이·불변식·반례를 명시하고 후속 TLC 검증 범위를 정한다. 이번 문서 walkthrough는 모델 검사 실행이나 수학적 증명으로 표시하지 않는다. |
| 시나리오 기반 검토 / model-based testing | 정상뿐 아니라 경합을 구체적인 사건 순서로 설명 | SC01–14에 복구·차단·증거를 대입해 설계 검토. 이후 같은 trace를 계약 시험으로 옮긴다. |
| 타입 중심 설계 | 누락·미지 값·다른 작업 종류를 구조적으로 구별 | Rust 내부 domain type과 wire type을 분리. 메모리 안전을 물리 정확성·관측 신뢰도와 혼동하지 않는다. |

RX는 ‘표준 하나를 그대로 구현’하는 방법보다 **계약 카드 → 전이표 → 장애 trace → 데이터/전송 → 같은 trace 재검토**를 채택한다. 이는 기존 메타 계획을 실제 설계로 닫는 절차다.

## 4. 실행·복구 방법과 최근 대안

| 방법 | 확인한 특성 | RX 선택과 비용 |
|---|---|---|
| caller idempotency key + 내용 비교 | AWS는 같은 요청 ID의 다른 의도를 오류로 구분하고 지연 요청·보존 기간을 별도로 다룬다.[^10] | 채택. 내용 hash만으로 서로 다른 두 번의 생산 작업을 합치지 않는다. |
| transactional outbox + inbox | 상태 변경과 발행 대기를 같은 DB transaction으로 저장하며 소비자는 중복을 처리해야 한다.[^11] | platform의 작업/사건/전달대기 atomic commit, Host의 수신/전달 journal에 채택. DB 두 개와 실제 장비 동작을 하나의 transaction으로 간주하지 않는다. |
| event sourcing / CQRS | 이력과 현재 읽기 모델을 분리하는 설계 접근 | 전체 범용 event-sourcing framework 대신 **작업 상태+타입 있는 사건을 한 transaction으로 기록**. revision별 재생 규칙은 고정한다. 실제 장비 상태를 replay로 재현했다고 하지 않는다. |
| lease + fencing | 만료만으로 지연된 이전 소유자의 쓰기를 막지 못하며, 쓰기 수신 지점의 token 검사가 필요하다.[^12] | Host가 세대·권한을 검사하고 자원을 배타 소유. native 장비가 token을 모르면 직접 pendant·다른 SDK client까지 막았다고 하지 않는다. |
| Temporal | activity timeout/retry 정책과 cancellation·비동기 결과 회수가 존재한다. timeout은 실행 유실 판단의 근거가 되어 재시도를 유발할 수 있다.[^13] | 장기 업무 workflow의 향후 후보. 첫 셀에 별도 orchestration service를 넣어도 장비의 불명 결과 문제는 남는다. BT 교체보다 물리 경계 계약이 먼저다. |
| Restate | 실행 log에 결과를 남기고 재생한다. durable step 내부 실패는 설정에 따라 재시도한다.[^14] | 서비스 내구화의 유력 대안. 장비 호출이 성공한 뒤 결과 저장 전 죽는 구간에는 RX의 journal/조회 계약이 여전히 필요하다. 첫 기준판의 필수 런타임으로 채택하지 않는다. |
| DBOS | workflow 복원, 완료 step 재사용, step의 at-least-once와 DB transaction의 exactly-once를 구분한다.[^15] | DB 중심 공정 업무에는 적합할 수 있다. 외부 로봇 동작이 DB transaction에 포함된다는 보장이 없으므로 첫 셀 핵심 경계의 대체재로 채택하지 않는다. |
| Saga / 보상 동작 | 실패 이후 별도의 업무 동작으로 보상하는 접근 | 복구 절차 구성에 사용 가능. 이미 열처리한 부품·이동한 소재를 DB rollback처럼 되돌린다고 표현하지 않는다. 보상도 별도 ID·허가·관측을 가진 새 작업이다. |
| 2PC / 분산 transaction | 참여자 모두 준비/commit을 지원해야 원자적 commit 가능 | 현재 PLC/ROS/native SDK 물리 동작은 RX DB transaction 참여자가 아니다. 첫 셀의 장비 완료 보장 수단으로 배제한다. |

이 비교에서 새 엔진을 배제한 이유는 언어 취향이 아니다. 현 구성에서는 추가 서버·운영 상태를 도입하면서도 가장 중요한 외부 부작용의 불확실성을 제거하지 못한다. 이후 다수 셀·장기 주문·사람 승인 workflow 요구가 실제로 커지면 C02 위쪽의 실행 엔진을 다시 평가할 수 있다. C03의 식별·증거·중단 규칙은 유지해야 한다.

## 5. 전송 선택

| 후보 | 강점 | 첫 RX에서의 판단 |
|---|---|---|
| gRPC / HTTP2 | Rust–C++ 간 타입 있는 RPC, unary·stream, deadline/cancel | 두 컨테이너 내부 계약에 채택. RPC cancellation은 이전 변경을 rollback하지 않는다.[^16] 유실·재시도·보존은 RX 규약이 담당한다. |
| ROS 2 actions / services / topics | action은 goal ID·접수·feedback·result·cancel을 제공 | solutions native binding에 채택. 결과 cache는 서버 shutdown을 넘어선 내구 이력으로 보장되지 않는다.[^17] |
| DDS / ROS QoS | 기존 ROS 생태계의 발견·pub/sub·전달 정책 활용 | solutions 내부 선택으로 제한. ROS QoS만으로 platform DB commit과 물리 실행을 일치시킬 수 없다. |
| Zenoh | pub/sub·queryable·storage 추상화 제공.[^18] | ROS RMW나 관측 통합의 후보. C03의 의미를 Zenoh key 이름에 숨기지 않는다. 첫 플랫폼 전송을 추가로 이중화하지 않는다. |
| MQTT 5 / Sparkplug 3.0 | MQTT 전달 QoS, Sparkplug의 topic/payload/session-state 규약.[^19] | PLC gateway·SCADA/MES 연동 후보. QoS2 전달을 로봇 작업의 exactly-once로 확대하지 않는다. retained motion command 사용을 허용하지 않는다. |
| NATS JetStream | 저장 stream·consumer 기반 구성.[^20] | 이후 다수 소비자·분산 이벤트 운용 요구 때 재평가. 첫 셀에는 platform 사건 원장과 재구독으로 필요한 범위를 충족한다. |
| Kafka | partition log·transaction·재생, 외부 출력의 exactly-once에는 목적지 협력이 필요.[^21] | 공장 전체 집계/분석 후보. 두 컨테이너 첫 셀 내부 명령 버스로는 운영 비용이 과하다. |
| HTTP/JSON/SSE | UI·운영 도구 접근과 서버→화면 사건 흐름 | 운영 API에 채택. SSE 재접속도 cursor 만료·갭 복구가 필요하며 브라우저 연결을 제어권의 근거로 삼지 않는다. |
| shared memory / 직접 FFI / 자체 TCP framing | 같은 호스트 고빈도 자료 전달에 유리할 수 있음 | 고속 제어는 solutions 내부에 유지. 공통 제어 계약은 먼저 관찰·복구 가능한 RPC로 구성하며 성능 병목 측정 없이 자체 전송을 만들지 않는다. |

전송의 역할은 **이미 정한 의미를 운반하는 것**이다. gRPC가 산업 표준보다 우수해서 모든 장비에 gRPC를 설치한다는 결론이 아니다. C08에서 ROS·MC protocol·필드버스·SDK로 번역한다.

## 6. 표현·버전 선택

Protobuf proto3의 `optional`을 사용해 누락과 0/false를 구별한다. 조회한 prost 0.14.4 문서는 proto2/3와 optional의 Option 매핑을 명시한다. Editions 지원 이슈는 조회 시 open 상태다.[^22] 따라서 RX v1은 proto3를 선택하고 Editions는 양 언어 도구 검증 후 차기 후보로 둔다. 특정 crate의 최신 patch 번호를 영구적인 제품 toolchain 선택으로 고정하지 않는다.

Protobuf deterministic serialization은 canonical serialization이 아니다.[^23] 요청 동일성은 **정규화한 의미 객체의 JCS(RFC8785) 바이트에 SHA-256**으로 정의한다. JCS는 Informational RFC이며 Unicode 정규화나 단위 변환을 대신하지 않는다.[^24] CBOR의 deterministic encoding은 유효한 대안이지만 첫 UI/지원 도구까지의 가독성과 추가 표현체계 비용을 고려해 채택하지 않는다.[^25]

UUID는 RFC9562의 v7을 플랫폼 ID에 사용하되 시간순 정렬을 사건의 인과 순서로 쓰지 않는다.[^26] 사건의 실제 순서는 원장의 순번이다. CloudEvents 1.0.2는 외부 사건 envelope로 사용할 수 있지만 완료 payload·원장 cursor의 의미는 RX가 정의한다.[^27] AsyncAPI 3.0은 stream 문서 표현에 참고하며 프로토콜 구현·보장을 제공하는 도구로 취급하지 않는다.[^28]

HTTP Idempotency-Key 문서는 조회 시 **expired Internet-Draft -07**이다. 이를 확정 RFC라고 인용하지 않는다.[^29] RX는 자체 명세의 `request_key`와 scope를 사용하며 HTTP header 이름에 설계 정확성을 의존시키지 않는다.

## 7. 근거의 수준과 남은 검증

공식 specification·공식 구현 문서·유지관리자 issue를 읽고, 현재 자사 5개 저장소 HEAD와 작업 상태를 다시 확인했다. [현재 상태 기록](current_state.json), [자사 지원표](../../docs/13_robotis_support_matrix.md), [이미지 명세](../../docs/14_image_support_spec.md)가 현장 입력이다. DHI 기동/소멸의 토크 효과, 공유 JTC, FFW 속도 및 Sapiens 모드가 단일 `execute→success` 추상화의 구체적인 반례다.

문서 검토의 완료는 compiler 상호운용, 지연/전력 상실 시험, 장비 안전 기능 검증을 뜻하지 않는다. SQLite의 내구성도 파일시스템·동기화·저장장치 전제에 의존한다.[^30] 이를 명시적인 납품 검증 의무로 남기는 것이 설계의 일부다.

## 출처

모두 2026-09-10 조회. 버전이 없는 웹 문서는 조회 시점 문서이며, 제조사 납품 binding의 버전 고정은 별도다.

[^1]: [OPC ISA-95 Job Control 2.00 StoreAndStart](https://reference.opcfoundation.org/specs/OPC-10031-4/6.2.1.4), [상태 정의](https://reference.opcfoundation.org/ISA95JOBCONTROL/v200/docs/6.2.2.2), [Machinery Job Mgmt 실행 순서](https://reference.opcfoundation.org/Machinery/Jobs/v100/docs/6.4).
[^2]: [OPC PackML 1.01](https://reference.opcfoundation.org/specs/OPC-30050/6).
[^3]: [PLCopen Motion Control](https://www.plcopen.org/standards/motion-control/), [Part 1 v2.0](https://www.plcopen.org/download_file/force/9f19d854-2dbf-4e07-a2ff-e5ff1a3e293a/342/).
[^4]: [OPC Robotics Part 1 1.02, §7.16](https://reference.opcfoundation.org/specs/OPC-40010-1/full).
[^5]: [VDA 5050 3.0.0 release](https://github.com/VDA5050/VDA5050/releases/tag/3.0.0), [고정 tag의 order schema](https://github.com/VDA5050/VDA5050/blob/3.0.0/json_schemas/order.schema). Release 설명은 2026-03-19 발행 문서라고 명시한다. PDF 파일명의 2025-03을 규격 발행일로 사용하지 않는다.
[^6]: [IDTA 현행 목록 Release 26-01](https://industrialdigitaltwin.org/en/content-hub/aasspecifications), [Part 1 범위](https://industrialdigitaltwin.org/en/content-hub/aasspecifications/specification-of-the-asset-administration-shell-part-1-metamodel-idta-number-01001).
[^7]: [W3C WoT Thing Description 1.1](https://www.w3.org/TR/wot-thing-description11/).
[^8]: [W3C SCXML](https://www.w3.org/TR/scxml/).
[^9]: [Lamport, Specifying Systems](https://lamport.azurewebsites.net/tla/book.html), [TLA+ Tools](https://lamport.azurewebsites.net/tla/tools.html).
[^10]: [AWS Builders’ Library, Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/).
[^11]: [AWS transactional outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html).
[^12]: [Martin Kleppmann, How to do distributed locking](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html). 저자의 분산 시스템 분석이며 표준 문서는 아니다.
[^13]: [Temporal Activity Execution](https://docs.temporal.io/activity-execution).
[^14]: [Restate Durable Steps](https://docs.restate.dev/develop/ts/durable-steps).
[^15]: [DBOS Workflow Guarantees](https://docs.dbos.dev/typescript/tutorials/workflow-tutorial).
[^16]: [gRPC Core Concepts](https://grpc.io/docs/what-is-grpc/core-concepts/).
[^17]: [ROS 2 Actions design](https://design.ros2.org/articles/actions.html), [Jazzy JTC 사용자 문서](https://control.ros.org/jazzy/doc/ros2_controllers/joint_trajectory_controller/doc/userdoc.html).
[^18]: [Zenoh abstractions](https://zenoh.io/docs/manual/abstractions/).
[^19]: [MQTT 5.0 OASIS Standard](https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html), [Eclipse Sparkplug 3.0](https://sparkplug.eclipse.org/specification/).
[^20]: [NATS JetStream](https://docs.nats.io/learn/jetstream/).
[^21]: [Kafka 4.1 Design, delivery semantics](https://kafka.apache.org/41/design/design/).
[^22]: [prost 0.14.4](https://docs.rs/prost/0.14.4/prost/), [Editions issue #1031](https://github.com/tokio-rs/prost/issues/1031).
[^23]: [Protobuf serialization is not canonical](https://protobuf.dev/programming-guides/serialization-not-canonical/).
[^24]: [RFC8785 JCS](https://www.rfc-editor.org/rfc/rfc8785).
[^25]: [RFC8949 CBOR §4.2](https://www.rfc-editor.org/rfc/rfc8949).
[^26]: [RFC9562 UUID](https://www.rfc-editor.org/rfc/rfc9562).
[^27]: [CloudEvents 1.0.2](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md).
[^28]: [AsyncAPI 3.0.0](https://www.asyncapi.com/docs/reference/specification/v3.0.0).
[^29]: [Idempotency-Key draft status](https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/).
[^30]: [SQLite atomic commit](https://sqlite.org/atomiccommit.html), [WAL](https://sqlite.org/wal.html).
