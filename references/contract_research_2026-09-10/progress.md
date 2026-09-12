# RX 계약·프로토콜 확정 작업 진행 기록

현재 목표: 산업·최근 방법을 폭넓게 조사하고 RX의 계약·프로토콜 v1.0 설계 기준판을 확정한다. 코드·컨테이너·장비 실행은 수행하지 않는다. 이전 계획을 만드는 목표로 축소하지 않는다.

## 완료할 항목

- [x] 책임 경계 C01–C08와 상태·증거 소유자
- [x] 작업 분류와 종류별 의미 계약
- [x] 접수·완료·실패·중단·불명 상태·전이
- [x] 식별·중복·보존·세대·제어권·재시작·복구
- [x] 메시지 순서·갭·snapshot·재구독·시간·버퍼·오류
- [x] 데이터 타입·정규화·메시지·RPC·호환·권한의 규범적 선택
- [x] 자사 모델·PLC binding과 제공 보장 한계
- [x] SC01–SC14 및 재시작 변형의 실제 문서 walkthrough
- [x] D01–D10 대안 평가와 결정 종료
- [x] 조사 보고서·원문 출처·선택/배제 근거
- [x] 독자 검토·반례 보완·요구별 완료 감사
- [x] README/진행 계획/기존 초안의 현재 기준판 연결

## 조사 분류

산업 계약/상태 모델: ISA-88/95, PackML, OPC UA Machinery/Robotics/Programs, PLCopen, VDA5050, AAS, W3C WoT.
실행·복구: 상태기계/SCXML, design by contract, TLA+·불변식 검토, event sourcing/CQRS, inbox/outbox, lease/fencing, Temporal·Restate·DBOS.
전송·사건: ROS2 actions/QoS, DDS·Zenoh, gRPC/HTTP, MQTT5/Sparkplug, NATS JetStream/Kafka, CloudEvents.
표현·호환: Protobuf proto3/editions, OpenAPI/AsyncAPI, RFC 9562 UUID, RFC 8785 JCS/RFC 8949 CBOR, W3C trace context, idempotency 관행.

원칙: 모든 방법을 빠짐없이 조사했다는 주장을 하지 않는다. 위 분류의 현업 표준·대표 구현·관련 새 대안을 조사하고, 중요한 결정마다 원문 근거 또는 RX 설계 판단을 구분한다. 현장 변수의 미확정은 binding 지원 조건으로 명시하며 공통 계약 결정 자체는 완료한다.

## 완료 범위

v1.0 문서 기준판과 방법 조사·결정 기록·문서 trace·독자 검토를 완료했다. 코드/실물/모델체크의 V01–V11은 후속 검증 의무이며 이번 완료 체크에 포함하지 않는다.
