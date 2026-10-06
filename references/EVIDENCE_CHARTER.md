# Evidence charter와 접수 규칙

이 저장소의 목적은 **무엇을, 어떤 source/artifact와 환경에서, 누가 실행·관측·검증·수락했는지** 다시 판단할 수 있게 보존하는 것이다. 현재 canonical 제품 문서·계약은 [RobotTransformation](https://github.com/jack0682/RobotTransformation/blob/develop/docs/README.md)이 소유한다. 여기의 raw evidence나 역사 `docs/`를 새 제품 규범의 병렬 원본으로 사용하지 않는다.

## 소유 범위와 보존

- 소유한다: 실행 receipt·원문 output, failed/UNKNOWN attempt, 진단·반례·측정, 수락/거절의 출처, source/artifact/Run과 기록 파일의 digest를 묶는 manifest.
- 소유하지 않는다: 현재 제품 구현, 새 wire 의미, SDK source, 설치 권한, qualification·physical authority. 이런 변경은 canonical source의 별도 검토와 검증으로 이어져야 한다.
- 기존 `docs/`와 `references/`의 경로, Git commit/tag/signature, 공개 URL을 보존한다. 과거 본문의 “현재”는 그 기록의 시점이다. 새 관측은 날짜·source·scope를 가진 새 record로 추가하고 과거 판정을 조용히 덮지 않는다.
- 큰 원문이나 배포 artifact는 접근 가능한 immutable locator·digest·size·보존 책임을 기록할 수 있다. 이 규칙은 이미 보관한 자료의 삭제·이동·history rewrite 승인이 아니다.

## 한 건의 접수 흐름

1. 이미 존재하는 Run/operation/request와 연결되는 기록인지 먼저 확인한다. 기존 failure의 새 관측이면 original identity와 앞선 evidence를 유지한다. 재시작·새 설치·새 candidate·부하 변화는 별도 항목으로 명시한다.
2. 새 evidence directory에 원문 output과 설명을 추가하고 [manifest template](templates/evidence-manifest.v1.json)의 필드를 실제 값으로 채운다. template 자체는 실행 증거가 아니다. 실행하지 않은 항목은 `NOT_RUN`, 모르는 항목은 `UNKNOWN`과 이유를 남긴다.
3. 파일별 digest와 scope를 확인한 후 PR에서 원 source/artifact, 명령·host·시간, counterexample, 실패와 미검증 범위를 검토한다. publication 검토와 제품 수락은 다른 판단이다.
4. 사용자 수락이 필요한 작업이면 그 명시적 결정의 출처를 별도로 기록한다. agent의 PASS·CI·PR merge·보존 작업으로 사용자 수락을 만들어내지 않는다.

## manifest에 필요한 사실

| 항목 | 기록할 내용 |
|---|---|
| 식별과 연속성 | record ID·종류, original Run/request/operation/invocation, 이전 record locator. 관련 ID가 없으면 null과 해당하지 않는 이유 |
| 요청·실행·검증·수락 주체 | requester, executor/agent, 실행 host, independent verifier와 그 범위, acceptor와 명시적 결정의 출처. “사용자 요청으로 Claude가 사용자 Mac에서 실행”을 “사용자가 실행”으로 줄이지 않음 |
| source | repository + full commit SHA + component path/tree 또는 필요한 source input inventory. branch/tag만으로 exact source를 대신하지 않음 |
| artifact | 종류·digest 체계·정확한 digest·size/locator, source와 연결 근거. Docker image ID, OCI manifest digest, archive SHA256, 실행 파일 SHA256을 서로 바꾸어 적지 않음 |
| candidate와 실행 | baseline/candidate 구분, 실제 사용한 binary/configuration, 명령/cwd·exit code·raw output, 적용된 review/Host/P/qualification 상태 |
| clock와 환경 | timezone이 있는 UTC/wall time, monotonic clock ID/boot identity·단위, 관측 시점과 수신 시점 구분. clock mapping이나 file-mtime 추정은 방법·spread·오차·한계를 함께 기록 |
| 검증 scope | docs/static source/build/unit test/SIM/controller/deployment/physical/functional-safety 중 실제 수행한 층, 입력·부하·장애 조건·지원 profile, 실행하지 않은 범위 |
| 결과와 제한 | PASS/FAIL/UNKNOWN/NOT_RUN, 실패와 counterexample, 현재 custody·원 결과 불명의 상태, 무엇을 입증하지 못하는지 |
| 파일·공개 범위 | 파일별 relative path·bytes·SHA256 또는 immutable Git locator, 공개 가능한 범위와 누락/비공개 이유 |

## 판정을 섞지 않는 규칙

- 계산한 source identity와 실제 compiled-binary identity를 구분한다. source·CI·SIM 결과를 physical completion이나 functional safety로 승격하지 않는다.
- package review, Host application, P confirmation, qualification, activation, Run completion, user acceptance를 각각 기록한다. `APPLIED_UNQUALIFIED`, `AWAITING_BASELINE`, UNKNOWN은 완료 표시가 아니다.
- timeout, SEND_ENTERED, 현재 idle/PID 부재, 재시작 또는 파일 부재만으로 이전 native effect를 성공·NO_EFFECT로 확정하지 않는다. 원 operation/invocation과 unresolved obligation·custody를 유지한다.
- 데이터 일부 누락, 실패, 의도한 refusal, 환경 변화도 evidence다. 완료율이나 연속 성공 계산에서 숨기지 않는다. 범위가 다른 실행끼리 비용 감소율·성능 향상을 주장하지 않는다.
- 측정값의 재계산과 실제 재실행을 구분한다. 로컬 기록을 읽은 날짜가 그 runtime 상태를 새로 관측한 날짜가 되지는 않는다.

## 공개와 projection

credential·private key·개인정보·승인되지 않은 equipment endpoint는 공개하지 않는다. 검토 중 문제가 발견되면 원 evidence를 임의 redact·삭제·수정하지 않고 보존 책임자와 공개 범위를 정한다. 필요한 경우 **별도 public projection**을 만든다. 원 file digest와 보존 위치, 제외한 field/range의 종류, 변환 방법·projection digest·남는 검증 한계를 기록하며 원문을 공개한 것처럼 표시하지 않는다.

이미 공개된 source history와 license/notice를 그대로 보존한다. 이 charter는 과거 record의 서명·수락·근거를 소급 인증하지 않는다. 기존 record에 새 manifest를 붙이는 경우도 새 관측 없이 확인할 수 있는 provenance만 추가한다.

## 검사와 인간 검토의 경계

가벼운 자동 검사는 JSON/schema, immutable source/파일 hash, local link와 명시한 origin locator, 필요한 field·clock 단위·status 일관성, historical file 보존을 검사할 수 있다. 기록의 사실성·원인 규명·현재 권한·실행 성공·수락은 그 검사만으로 증명되지 않는다. 기존 repository/contract/table/signature/DCO gate는 그대로 유지한다.

기존 record를 새 format으로 일괄 변환하지 않는다. 새 record와 새 publication manifest부터 명시한 format을 사용하고, legacy 원문은 source commit·path·hash로 가리킨다. [CP2 진단 publication manifest](2026-10-05-f2-cp2-not-accepted/publication-manifest.json)는 원 record를 고치지 않고 provenance를 추가하는 예다.
