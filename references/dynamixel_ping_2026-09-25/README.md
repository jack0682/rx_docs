# G5.2 DYNAMIXEL Ping 모의 어댑터 실행 근거

[결정과 지원 경계](../../docs/41_dynamixel_ping_adapter.md)의 공개 근거다. 구현자 관측이며 독립
수락 receipt를 대신하지 않는다. 실물 장비, 장비 자격, 물리 안전, 전체 G5 SDK 또는 다섯 제품
번들 완료를 주장하지 않는다. `verification-summary.json`의 기계 판독 플래그를 함께 읽는다.

## 원본과 재현

- Platform source `b145366992c36b1227efbab7e7a776fae6d9c62f`의
  [실제 client passage](https://github.com/jack0682/rx-platform/blob/b145366992c36b1227efbab7e7a776fae6d9c62f/tools/test_clients.py).
- Solutions final source `71aec7e7f1e2d6723884e30e97b9dd4ba97fb502` (initial feature source `039aa0d0459b8087e708ec77fdccfbd48fadc1d0`)의
  [adapter](https://github.com/jack0682/rx-solutions/tree/71aec7e7f1e2d6723884e30e97b9dd4ba97fb502/runtime/rx-host/src/dynamixel),
  [helper와 공식 pin](https://github.com/jack0682/rx-solutions/tree/71aec7e7f1e2d6723884e30e97b9dd4ba97fb502/native/dynamixel),
  [설치·예제](https://github.com/jack0682/rx-solutions/blob/71aec7e7f1e2d6723884e30e97b9dd4ba97fb502/runtime/rx-host/DYNAMIXEL_ADAPTER.md).
- `release-clarified/runtime-batch.json`에 최종 네 실제 명령이 있다. 이전 `runtime-batch-final.json`은 최초 구현 cut이다. 실제 이미지 ID는 각 `result.json`과
  각 cut의 `release-evidence.json`에 고정했다. 이미지·private source archive·바이너리는 공개하지 않았다.
  로컬 이미지 이름은 registry 배포 주소가 아니다. 다른 환경에서 같은 명령만 입력하면 같은
  이미지가 생긴다는 재현성을 주장하지 않는다. 공개 Dockerfile과 고정 원본으로 빌드하고,
  기존 외부 개발 release 서명·실제 recovery evidence를 준비하는 절차가 별도로 필요하다.
- 최종 `release-clarified/code-inputs.json` (초기 `compatibility-and-code-inputs.json`)은 선택된 runtime build snapshot의 platform219개,
  solutions240개 코드 입력과 현재 입력이 같음을 확인한다. 테스트·문서 변경은 구별했다.
  각 cut의 `current-source-descriptor.json`은 해당 Linux 이미지 descriptor와 같다.
  최종 source-delta.patch는 주석 교정만 보여 주며 binary-comparison.json은 helper·다른 다섯 binary 불변과 Host pin 변경을 구별한다.

## 주요 관측

| 근거 | 확인할 내용 |
|---|---|
| `release-clarified/python-loss`, `release-clarified/cpp-loss` | 실제 공개 commissioning 후 Ping, 암호화된 receipt 반환 유실, 동일 key 재전송, 반대 언어의 같은 Host/operation 재전송 |
| `release-clarified/python-unknown`, `release-clarified/cpp-unknown` | 외부 OS observer가 실제 helper를 종료; helper audit와 native row 각각1, capture 없음, UNKNOWN/OUTCOME_NONE 유지 |
| 각 장면 `host-adapter-refusals.json` | 실제 Host에서 endpoint/profile/source/산출물/실행 파일/inventory 위조의 여섯 거절 |
| `product-helper-full-request-refusals.json` | 완전한 요청을 갖춘 Python/C++ 직접·가짜 소켓·argv0 위조 여섯 거절, endpoint 네 거절 |
| `helper-mutant-result.json`, `helper-mutant-test.log`, `helper-mutant/helper.cpp` | 분리된 변형에서 부모 실행 파일 검사만 해제하면 unauthorized Ping 성공으로 거절 검사가 실패함 |
| `ownership-probe` | 제품 구현 전 surrogate owner를 쓴 Linux 메커니즘 probe. 제품 Host/SDK 실행 증거와 혼동 금지 |
| `legacy-installation-current-host` | G5.1 이미지로 초기화한 FILE_SIMULATION 설치를 현재 Host로 열어 실제 SDK 요청 성공 |
| `persistence-roundtrip.log`, `namespace-comparison.json` | 기존 JTC/MELSEC 저장 표현 불변과 이전 runtime에 없던 별도 native 이름공간 |
| `client-packages` | 새로 빌드·설치한 두 언어의82개 wire 벡터 결과 동일, 외부 소비자 빌드 |
| `regressions.json`, 각 `regression-*` | 아홉 기존 경계 실행. resource에 resident가 포함됨 |
| `g3-regression`, `g4-regression`, `host-refusals-current.log` | G3 12·G4 22장면과 Host 자기 발급 거절 셋 |
| `regression-lock/result.json` | 11개 lock 장면, 50회 Host stress, 실패0. F9 과거 단발 실패 원인을 소급 확정하지 않음 |
| `incidents.md`와 최초 로그 | entrypoint, fixture 타입/범위, retired boot, noexec mount, 잘못 둔 negative binding의 실패와 구체적 수정 |

macOS 전체 스위트는 platform408/0/16, solutions393/0/17이다. 처음393 이전392회 결과와 새로
추가한 영속 표현 검사1개도 함께 남겼다. Linux CI의 새 source commit 결과는 별도 CI 기록에 둔다.
검사 개수를 장비·현장·전체 SDK 성숙도로 해석하지 않는다.

UNKNOWN 행의 helper audit는 호출 진입 관측이다. Ping 완료를 증명하지 않는다. 성공 행은
별도 native capture의 SDK 결과와 TX/RX를 확인한다. 두 경우 모두 같은 요청을 다시 보낸다고
helper를 다시 실행하지 않았다. client 종료·재접속은 cancel이나 물리 자원 해제의 근거가 아니다.

## 보존 규칙

`inventory.json`은 이 문서 자체를 제외한 선택된 원시 파일의 SHA-256과 크기를 기록한다.
원시 로그의 공백·개행은 바꾸지 않는다. `.gitattributes`의 해당 경로 `-text`도 그 목적이다.
임시 signing seed, login password/cookie, TLS, 개인 키, DB, 실행 바이너리, cargo/cache와 이미지
archive는 제외했다. 선택된 자료에 대해 세 개발 private key의 실제 내용·seed 패턴을 로컬에서
대조했고 발견0이었다. 이 검사는 private key를 runtime이나 공개 파일에 전달하지 않았다.

기존 F12 runner의 `LOCK_LIFETIME_UNRESOLVED` 같은 과거 출력은 원문을 유지했다. G1의 실제
lock 근거를 덮어쓰는 현재 상태 선언이 아니다. 성공한 뒤 최초 실패를 삭제하거나, 미실행을0회
실패로 바꾸지 않았다. 독립 검증은 이 자료를 읽는 것에 더해 실제 장면을 별도로 실행해야 한다.
