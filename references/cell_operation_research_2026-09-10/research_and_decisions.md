# 셀 운영 계약의 조사 근거와 설계 결정

조사 범위: 운전 조건·시작/중단·개입·복구·변경 및 기존 RX 계약 연결. 2026-09-10 확인.

## 1. 조사 결론

RX는 **검증한 사용 범위, 현재 조건, 자동 운전의 시작 의도, 실제 보호 기능**을 구별해야 한다. 사용 범위의 승인이나 명령 처리 성공을 실시간 보호 기능으로 바꾸지 않고, 각 작업에 유효한 조건과 기록을 적용한다. 개입 후에는 사람·물체·장비·미결 명령의 변화까지 재확인한 뒤 새로운 시작 의도를 받는다.

이것은 특정 표준의 문장을 API 이름으로 옮긴 결과가 아니다. 아래 원문 사실과 자사 플랫폼의 구체적인 부작용을 대조해 내린 RX 설계 선택이다. 현장 모델·PLr·정지시간·안전회로가 없는 상태에서 그런 값을 가정하지 않는다.

## 2. 근거와 적용 한계

| 출처 | 확인한 내용 | RX에 반영한 판단 |
|---|---|---|
| S01 ISO 12100:2010 | 위험성평가와 위험 감소를 기계의 한계·의도된 사용에 연결하는 일반 원칙 | 현장 사용 범위와 위험·검증 연결을 먼저 작성 |
| S02 ISO 13849-1:2023 / IFA 1/2025 | 안전 관련 제어부·소프트웨어 설계, 요구 PLr과 실제 달성 PL의 구분을 설명 | `GOOD`, hash, DB transaction을 안전기능 달성 성능으로 간주하지 않음 |
| S03 ISO 14118:2017 | 예기치 않은 기동을 전기·유공압·중력·저장 에너지 등의 관점에서 다룸 | reset/접속 복원/권한 인계와 시작 의도 구별, 정지와 지지/격리 구별 |
| S04 EU 2006/42/EC Annex I §1.2 | 시작·자동운전·정지·제어 모드의 공개 요구 | 정상 자동 운전과 개입/정지 이후 재시작을 같은 버튼/상태로 합치지 않음 |
| S05 EU 2023/1230, 2026-07-27 통합문 Annex III §1.2 | 자동운전 조건, 정지 우선, 비상정지 해제와 재시작 구별, 연동 장비 영향, 전원/통신 상실을 다룸 | 셀 영향 범위와 명시적인 기동/복구 경계의 참고. 일반 적용일은 2027-01-20이며 일부 조항 예외가 있음 |
| S06 HSE 기계 유지보수 | 위험 에너지 격리, 낙하 가능 부품 지지, 재기동 방지 및 작업 준비의 필요 | 소프트웨어 pause와 사람의 접근/정비 조건을 분리 |
| S07 OSHA group LOTO·shift change | 복수 작업자·책임자·인수인계 때 보호의 연속성을 다룸 | 개입 사례를 담당자 한 명의 체크박스로 닫지 않고 관련 인원/작업/외부 격리 상태와 연결 |
| S08 OPC ISA-95 Job Control 2.00 | 시작 허용 상태와 실제 실행 상태, 중단과 종료가 구별됨 | RunMandate와 현재 operation permit, workflow 상태를 분리 |
| S09 UR Stop recovery / Dashboard SW5.24 | 전원이 켜지고 brake가 풀린 robot mode와 program running은 다름. 정지 종류에 따라 프로그램이 정지 지점 또는 처음부터 재개될 수 있음 | generic resume 금지, native 재개 위치와 중복 효과를 복구 명세에 포함 |
| S10 PLCopen MC Part1 v2.0 | MC_Stop의 완료와 축이 새 동작을 받을 수 있는 상태를 구별하는 모델 | stop 요청/정지 결과/다음 작업 인계를 별도 조건으로 유지 |
| S11 ISO 10218-2:2025 / ISO 11553-1:2020 / IEC 60825-1:2014 | 로봇 통합, 레이저 가공기계 방사 위험, 레이저 제품 분류/정보의 서로 다른 범위 | 첫 레이저 셀을 CNC 예제로 대체하지 않음. 가공 start와 진입 가능 조건을 OEM과 별도 정의 |
| S12 제공된 안전 가이드/점검표/의견서 | 초안·예시·임시 기준 검토자료이며 최종 인증 결과가 아님 | 거리·timeout·위험점수의 단순 복사 금지, 개입/변경 후 점검 연결 |
| S13 현재 자사 source | DHI activate/stop의 토크 부작용, Sapiens 모드/정책과 기동 출력 | process ready, mode 선택, physical ready, 동작 시작을 별도 계약으로 구분 |

법령·기관 자료는 명시된 관할과 적용 범위가 있다. EU·미국·영국 자료를 대한민국 첫 현장의 법적 적용 확정이나 인증 기준으로 채택한 것이 아니다. 공개된 산업 설계 원칙·반례의 교차 근거로 사용했다. 표준은 공개 범위와 이용 가능한 제조사/기관 설명을 대조했으며 유료 전문 전체의 조항 적합 판정은 하지 않았다.

## 3. 현재 코드가 주는 구체적인 반례

자사 5개 repo의 HEAD와 clean 상태는 [current_state.json](current_state.json)에 재확인했다. 다음은 정적 source 확인이며 하드웨어 시험이 아니다.

**DHI:** `on_activate()`는 `start()`, destructor와 `on_deactivate()`는 `stop()`을 호출한다. `start()`에는 command 쓰기와 설정에 따른 torque enable 반복 시도가 있고, 그 반복이 모두 실패한 경우를 별도 failure 반환으로 바꾸지 않고 뒤의 SUCCESS 반환에 도달할 수 있다. `stop()` 역시 disable 요청 후 반환한다. 따라서 lifecycle callback SUCCESS만으로 실제 토크·지지 상태를 판정할 수 없다. 모델별 후조건과 기동 중 부분 결과를 따로 확인해야 한다.

**AI Sapiens:** sim2real README는 기본 command publishing, 초기 Damping, posture 보간, policy 진입 tick의 추론/출력, API_WARMUP/API/수동 권한을 구분한다. 따라서 ‘mode 선택’을 단순 metadata 변경으로 분류하거나, Damping이라는 이름을 전체 몸체의 안전 지지 증거로 사용하는 추상화는 부적합하다.

현재 source에 실제 native 반복이 있는 경우 기존 ‘production invocation 최대 1회’ 규칙과의 적합성을 검증해야 한다. RX가 호출한 native lifecycle 한 번과 그 내부 효과를 구별하고, 내부 반복/부분 실패가 명시·관측되지 않으면 그 binding을 admission하지 않는다. upstream package 필수 포함 요구는 그대로 유지한다.

## 4. 대안 평가와 결정

| 결정 | 대안 | 채택·이유·비용 | 증거/반례 |
|---|---|---|---|
| O-D01 | 전체 ready bool / 작업별 조건 집합 | **검증 범위+작업별 typed 조건과 미확인 구분**. 무엇 때문에 막혔는지와 변화 영향을 추적. 조건 명세 작성 비용 수용 | S01·02, 오래된 GOOD 사본 |
| O-D02 | 매 단계 사람 승인 / 한번 승인하면 영구 자동 / 범위 있는 run 시작 의도 | **RunMandate**로 정상 자동 반복을 허용하고 만료/개입/세대 변경 시 재시작 분리 | S04·05·08, 인건비 목적 |
| O-D03 | 저장된 허가서만 검사 / 짧은 permit+Host 마지막 검사 | **operation에 결합한 1회 permit와 Host gate**. 철회 전달 중의 시간창은 명시하고 물리 보호 기능으로 보완 | 기존 SC02·03·04, 지연 명령 |
| O-D04 | 전역 한 상태 / 독립 축과 영향 범위 | **운용 의도·차단·미결·개입·자원 상태 분리**, 위험 의존 관계가 불명확하면 셀 전체 새 생산 차단 | S05, 공유 JTC·문/레이저 연동 |
| O-D05 | 오류 확인=복구 / 단계·근거 있는 개입 사례 | **접근 조건·작업·재확인·처분·새 시작 분리**. UI 단계는 실제 안전 상태를 대신하지 않음 | S03·06·07 |
| O-D06 | 범용 resume / 명시된 continuation 또는 restart plan | **native 재개 위치·이미 발생한 효과·허용 continuation을 검사**. 불명 작업 재실행 금지 유지 | S09, UR 정지 종류별 차이 |
| O-D07 | 소재 보유자 1개 / 근거 있는 복수 지지 주장 | **복수 지지/불명과 part identity 근거**를 표현. controller lock과 구별 | 지그·그리퍼 공동 지지/인계 |
| O-D08 | 모든 고장 torque-off / 기능별 현지 반응 | **위험·모델·모드별 감지/정지/지지/에너지 경로**. 일률적인 정지값 없음 | S03·05·10·12·13 |
| O-D09 | 변경 시 이름/번호만 변경 / 검증 의존 관계 갱신 | **영향 closure+사용범위 재검토+새 epoch 동기화**. 확인되지 않은 변경을 통과시키지 않음 | S01·12, 지그·정책 변경 |
| O-D10 | base v1 API 그대로 우회 가능 / 의무적인 셀 wrapper | **base 계약 재사용+cell extension 필수 협상**. 보호된 native gateway를 거치지 않는 생산 endpoint 금지 | 구버전 Host/직접 Authorize 우회 |
| O-D11 | 모든 보호정지 자동 재개 / 첫 판에서 명시적 재시작 | **정상 recipe 대기는 자동, 안전/미확인 정지·개입 뒤에는 새로운 의도**. 자동 safeguard 복귀가 필요한 공정은 별도 검증/후속 확장으로 표시 | S04·05의 허용 가능성과 S09의 적용 조건을 구별 |

O-D11은 자동 재시작이 모든 상황에서 표준상 금지된다는 주장이 아니다. RX 첫 셀 운영 계약의 명시적 제품 정책이다. 정상 자동 run의 매 소재·매 node마다 사람 조작을 요구하지 않는다. 현재 입력으로 증명하지 못하는 고장/안전 복귀의 자동 실행을 기본으로 추가하지 않는다.

## 5. 충분성 판단과 검증 한계

사용 범위, 시작/재시작, 정지/지지, 사람 개입/인수인계, 장비 복구, 데이터/권한 경합에 대해 서로 다른 종류의 원문을 비교했다. 중요한 선택마다 직접 근거 또는 RX의 명시적 정책과 반례를 남겼다. 특정 모델의 안전 기능 상세·신호·시간은 자료가 없으므로 **필수 commissioning 입력**으로 닫고, 미충족 때 실행 차단하는 계약을 확정한다.

최종 문서 검토는 조건·전이·메시지·근거가 같은 사례에서 일치하는지 확인한다. 형식 모델 검사·컴파일러 상호운용·실물·기능안전 검증은 별도 의무다. 그 검증을 한 것으로 표현하지 않는다.

## 6. 원문 출처

- S01 [ISO 12100:2010](https://www.iso.org/standard/51528.html), 공개 적용 범위.
- S02 [ISO 13849-1:2023](https://www.iso.org/standard/73481.html), [DGUV IFA Report 1/2025](https://www.dguv.de/ifa/publikationen/reports-download/reports-2025/ifa-report-1-2025/index.jsp). 새 독문판은 2023판 설명. [2/2017e](https://www.dguv.de/ifa/publikationen/reports-download/reports-2017/ifa-report-2-2017/index-2.jsp)는 2015판 기반 영문 설명이므로 판본을 섞지 않는다.
- S03 [ISO 14118:2017](https://www.iso.org/standard/66460.html).
- S04 [Directive 2006/42/EC, 2019-07-26 통합본](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02006L0042-20190726), Annex I §1.2.3–1.2.6. 고정 판본의 설계 원칙 비교용.
- S05 [Regulation 2023/1230, 2026-07-27 통합본](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02023R1230-20260727), Annex III §1.2.2–1.2.6 및 Article 54. 통합본은 문서 편의용이며 법적 효력은 해당 OJ 정본을 따른다. 일반 적용일과 일부 조항의 앞선 적용일을 구별한다.
- S06 [HSE Maintenance of work equipment](https://www.hse.gov.uk/work-equipment-machinery/maintenance.htm), 영국 실무 지침.
- S07 [OSHA 1910.147(f)(3)–(4)](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.147), 미국 group/shift 규칙. 원문 검색 발췌와 [OSHA 공식 tutorial](https://www.osha.gov/etools/lockout-tagout/tutorial/group-lockout-tagout-requirements) 대조. 일부 open 요청은 실패했으며 추가적인 현장 적용/면제 판정 근거로 사용하지 않았다.
- S08 [OPC ISA-95 Job Control 2.00 상태 모델](https://reference.opcfoundation.org/ISA95JOBCONTROL/v200/docs/6.2.2.2).
- S09 [UR Stop recovery](https://docs.universal-robots.com/tutorials/controlling-robot-externally/stop-recovery.html), [Dashboard SW5.24](https://www.universal-robots.com/manuals/EN/HTML/SW5_24/Content/prod-dashboard/Dashboard_table.htm). 대상 controller/설정에서의 의미 확인 자료이며 첫 로봇/설치 버전 선정 증거 아님. 문서 내 보호정지 대기시간 설명의 차이는 RX 공통 timeout으로 채택하지 않는다.
- S10 [PLCopen Motion Control v2.0](https://www.plcopen.org/download_file/force/9f19d854-2dbf-4e07-a2ff-e5ff1a3e293a/342/), §3.3. 이전에 확인한 [로컬 원문](../contract_research_2026-09-10/sources/plcopen_motion_v2.pdf).
- S11 [ISO 10218-2:2025](https://www.iso.org/standard/73934.html), [ISO 11553-1:2020](https://www.iso.org/standard/67658.html), [IEC 60825-1:2014](https://webstore.iec.ch/en/publication/3587).
- S12 [위험성평가 심화 정리](</Users/ojaehong/research_RX/output/documents/machine_tending_risk/머신텐딩_위험성평가_심화_정리.md>), [제공자료 통합 분석](</Users/ojaehong/research_RX/humanoid_safety_documents_integrated_analysis_2026-09-08.md>), 원문 가이드 본문 p.24–30, 점검표 p.1–2. 출처의 초안 상태와 유효 범위는 [16 연결 문서](../../docs/16_safety_requirements_contract_link.md)를 따른다.
- S13 [DHI source](/Users/ojaehong/RX_automation/dynamixel_hardware_interface/src/dynamixel_hardware_interface.cpp:49), [Sapiens sim2real README](/Users/ojaehong/RX_automation/ai_sapiens/ai_sapiens_sim2real/README.md:1). 정확한 commit은 current_state.json에 기록했다.
