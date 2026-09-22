# 기존 검사기의 CI 연결과 실패 대조 — 2026-09-18

문서 21·22·23의 기존 표 검사와 platform의 기존 binding 검사를 필수 CI에 연결한다. SDK 신선도와 서버 설정 감사는 기존 `ci.yml`의 수동 실행에서 독립 job으로 실행한다. 새로운 계약 검사나 장치 검증을 추가한 작업이 아니다.

## 사전 측정

변경 전 기준은 rx_docs `3da1b5b54a3307ba0ea234aa6233a6240006f7d0`, rx-platform `ee4052fbb60e961a2adebc76b99118d208680f48`, rx-solutions `6c1e27ff141cbd2ba30bbd51738031145f9627f4`다.

| 대상 | 현재 실행 결과 | 세 저장소 CI의 해당 호출 참조 |
|---|---|---|
| 문서 21·22·23의 유일한 Python 블록 | 3/3 통과; 77자리, 요구 19개, 반례 4개·단계 24개·축 20개 | 각 저장소 0줄 |
| `update_*_binding.py --check` | 7/7 통과 | 각 저장소 0줄 |
| `check_host_sdk.py ../rx-solutions/sdk` | `SDK synchronized with platform: 107 files; authority excluded` | 각 저장소 0줄 |
| `configure_github.py` 기본 읽기 전용 실행 | 세 저장소 모두 설정 일치, rc=0 | 각 저장소 0줄 |

참조 수는 `.github/workflows/*` 전체에서 `update_\S*binding`, `check_host_sdk`, `configure_github`, `21_declaration|22_open_items|23_handover|```python|check_doc`의 일치 줄을 각각 세었다. 일반적인 간접 호출 그래프의 도구 수를 주장하는 수치가 아니다. 당시 CI 파일도 직접 읽어 호출 부재를 확인했다.

## 실패할 수 있는 검사인지 확인

Git 추적 파일을 별도 사본 트리로 복사하고, 새 문서 추출기만 추가 복사해 실행했다. 문서의 Python 로직을 별도 검사 파일로 복제하지 않았다. 각 문서 변형은 해당 실험 직후 복구하고 다음 실험을 진행했다. 원본 저장소와 서버 설정은 변형하지 않았다.

| 주입 위치·변경 | 실행 | 관측 |
|---|---|---|
| 문서 21 첫 `S01` 표 행을 `S00`으로 | `python3 tools/check_document_tables.py` | 문서 간 자리 순서 비교 `AssertionError`, rc=1 |
| 문서 22 첫 `M-01` 표 행을 `M-02`로 | 같은 추출기 | 요구 ID 유일성 `AssertionError`, rc=1 |
| 문서 23 첫 `책임` 표 행을 알 수 없는 축으로 | 같은 추출기 | 다섯 축 비교 `AssertionError`, rc=1 |
| 문서 21 Python fence 제거 / 두 개로 증가 / 닫힘 제거 | 같은 추출기, 각각 실행 | 세 경우 모두 `expected exactly one complete Python fence`, rc=1 |
| `spec/host-read/v1/binding.json`의 `max_payload_bytes`를 1000000→1000001, source hash 불변 | `python3 tools/update_host_read_binding.py --check` | `Host read binding source mismatch`, rc=1 |
| 바로 위와 **동일한 사본** | `cargo check -p rx-protocol --locked` | rc=0; 기존 build의 비해시 필드 검출 공백 확인 |
| SDK `contract.proto`에 주석 추가 후 **자체 source-lock 해시도 갱신** | 원본 platform의 `python3 tools/check_host_sdk.py <사본 SDK>` | 자체 정합성은 맞지만 `SDK is stale relative to platform sources`, 해당 proto 표시, rc=1 |
| 사본 `repository-settings.json`의 기대 topics에 `na-negative-control` 추가 | 사본의 `python3 tools/configure_github.py` | 서버를 바꾸지 않고 `DRIFT: jack0682/rx-platform: topics`, rc=1 |

[전체 대조 실행 출력](negative-controls.txt). 최초 cargo 호출은 PATH에 없어 시작하지 못했고, 설치된 Rust 1.98.1을 명시한 재실행 결과만 컴파일 근거로 사용한다. 빌드 성공은 위 메타데이터 공백에 대한 근거이며 실제 장치의 자격 근거가 아니다.

## 두 기본 proto의 판정

선택적 source binding에 기본 proto를 추가하지 않는다. **설계상 계약 식별자 분리로 판단**했으며, 작성자의 과거 의도를 직접 확인했다는 주장은 아니다.

- 규범 manifest 두 개는 각 규범 문서 4개와 base/cell 연쇄를 해시한다. proto 원본 바이트는 이 해시의 대상이 아니다.
- 선택적 executor 및 checkpoint binding의 README는 frozen base/cell을 대체하지 않는 별도 식별자라고 명시한다. 기본 proto를 그중 하나에 넣는 것은 소유 경계를 새로 정하는 변경이다.
- 전체 로컬 refs의 두 proto 이력은 최초 구현 `493a6bb1a5d2e1ac7a49675ff64c6602b1082591`로 이어지고, binding JSON 및 updater 이력에서 두 경로의 추가·제거 기록은 없다. [실제 검색 출력](schema-history.txt).
- 두 proto 모두 SDK inventory에는 고정돼 있으며 platform 바이트와 일치했다. 이는 사본 무결성이지 platform 자체의 source freeze가 아니다.
- 기존 wire 시험 11개가 통과했고 규범 문서와 descriptor의 필드 403개를 비교했다. [실제 시험 출력](wire-tests.txt). 이 시험은 문서에서 찾지 못하는 메시지를 건너뛰므로 완전한 wire conformance 증명으로 읽으면 안 된다.

규범 문서 식별자, 선택적 binding의 source hash, SDK inventory는 별개로 유지된다. **두 기본 proto에 platform 원본 바이트 동결은 없다.** 더 강한 고정이나 의미 적합성 검사는 별도 요구와 검증이 필요한 후속 작업이다.

판정의 파일별 근거와 소유 경계는 [platform의 고정 revision 기록](https://github.com/jack0682/rx-platform/blob/49912bc86e2c6ed2b3790115092026b8fa9e329f/docs/ci-guards.md)에 연결했다.

## 실행 경계

문서·binding 검사는 기존 push/PR 필수 repository job에 포함된다. 수동 감사 두 job은 `workflow_dispatch` 때만 실행되고 집계 `ci.needs`는 `[repository, rust]` 그대로다. 따라서 필수 CI 성공과 수동 감사 성공은 별개 결과다.

**cron 미활성. 향후 정상 main 승격 시 예약 설정을 명시적으로 추가해야 활성화된다.** 현재 schedule 키가 없으므로 승격만으로 예약이 자동 생성되는 것은 아니다. `main` 변경이나 기본 브랜치 변경은 이번 작업에 포함하지 않았다.

원격 서버 감사에는 읽기 전용 `github.token`만 사용한다. 로컬 관리자 권한으로 통과한 결과를 원격 토큰의 권한 증거로 대체하지 않는다. 권한이 부족하면 해당 실패를 보존하고, 승인된 로컬 계정의 읽기 전용 감사를 대안으로 쓴다. CI에서 서버 설정을 적용하거나 관리 토큰을 저장하지 않는다.

## 원격 실행 관측

[platform PR #13](https://github.com/jack0682/rx-platform/pull/13)은 [필수 PR CI](https://github.com/jack0682/rx-platform/actions/runs/35293459158)와 DCO가 성공한 뒤 `develop`에 병합됐다. 서명 및 작성자 signoff가 검증된 병합 커밋은 `0e274e2b95e9bac3660b2b0355f9a0fc68a21f63`이다. PR의 repository job에서 binding 7개가 실행·통과했고 전체 Rust fmt/clippy/workspace test도 통과했다.

`gh workflow run ci.yml --ref develop`로 [실제 수동 실행 35293778714](https://github.com/jack0682/rx-platform/actions/runs/35293778714)를 만들었다.

- [SDK 감사 job](https://github.com/jack0682/rx-platform/actions/runs/35293778714/job/105441987703): **SUCCESS**. 비교한 platform은 위 병합 커밋, solutions는 `6c1e27ff141cbd2ba30bbd51738031145f9627f4`다. 두 체크아웃의 SHA와 `SDK synchronized with platform: 107 files; authority excluded`를 실제로 출력했다.
- [서버 설정 감사 job](https://github.com/jack0682/rx-platform/actions/runs/35293778714/job/105441987517): **FAILURE**, `github configuration: gh: Resource not accessible by integration (HTTP 403)`, exit 1. 워크플로의 `contents: read` 토큰은 이 스크립트가 요구하는 API 접근을 모두 제공하지 못했다. 원본 오류가 API 경로를 포함하지 않아 정확히 어느 호출이 거부됐는지는 이 로그만으로 특정하지 않는다.

따라서 **서버 설정 표류의 원격 감사 성공은 미달성**이다. 실행 경로와 실제 권한 실패를 확인한 것이 결과다. 같은 스크립트는 사전 측정의 인증된 로컬 읽기 전용 실행에서 통과했고 기대 topics 변형도 검출했다. 현재 대안은 그 로컬 감사다. 원격 job의 실패를 성공으로 바꾸거나 권한을 늘리지 않았다. 필수 CI 성공으로 이 감사 실패를 가리지 않는다.

두 감사 step의 [실제 출력 발췌](remote-audits.txt)는 원격 job 로그에서 가져왔다.
