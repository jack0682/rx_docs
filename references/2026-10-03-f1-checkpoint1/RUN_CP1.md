# F1′ CP1 — S2 9단계 SIM 직접 실행

병합된 develop의 전용 SIM 설치를 사용하는 제품 CLI 명령이다.
Docker daemon으로 분리 실행한 P/Host/Executor를 사용하며, 터미널 종료로 서버가 종료되지 않는다.
환경은 **SIMULATION / FILE_SIMULATION, Linux arm64**다.

아래 명령은 별도 실제 object instance로 새 **N=1 Run**을 시작한다.

```sh
cp1=/Users/ojaehong/RX_automation/rx_ws/.build/framework-f1-checkpoint1
rxcp1() {
  python3 "$cp1/live10/verification/installed-client/rx" execution \
    --connection "$cp1/live10/operator.json" \
    --state-dir "$cp1/live10/operator-client" "$@"
}
set -o pipefail

rxcp1 run "$cp1/author10/publication.json" \
  --object "$cp1/author10/object-acceptance.json" \
  --request-id 700ccbe2-af66-4d88-a9ef-0bd032696453 \
  --wait-seconds 90 --output "$cp1/live10/user-receipt.json" |
  jq '{environment, run:.binding.run, state:.result.run.value.state,
       operations:[.result.work[] | {node:.execution.selection.node,
         outcome:.operation.outcome, disposition:.operation.disposition}],
       reports:(.approved_reports | keys)}'
```

기대 결과: environment=SIMULATION, state=COMPLETED, 9개 operation 모두
SUCCEEDED / RELEASED. 실제 순서는 pick → load → rotate-align → clamp →
close-door → process(5초) → open-door → unload → place다.
rotation 선택값은 95° / 허용오차 0.5°다.

같은 Run의 저장 보고서를 다시 연다. 조회는 native 명령을 전송하지 않는다.

```sh
cp1_run=$(jq -r '.binding.run' "$cp1/live10/user-receipt.json")
rxcp1 inspect "$cp1_run" --reports |
  jq '{environment, run:.binding.run, state:.result.run.value.state,
       operations:[.result.work[] | {node:.execution.selection.node,
         outcome:.operation.outcome, disposition:.operation.disposition}],
       reports:.approved_reports}'
```

응답을 잃었을 때에는 첫 run 명령의 **동일 request ID**를 보존하고
--output을 빼거나 새로운 파일 경로를 지정해 조회를 이어간다.
기존 출력 파일은 서버 요청 전에 거절한다. 새 request ID는 복구 명령이 아니다.

CP1 사용자 수락 대기에서 멈춘다. CP2/CP3, F2′/F3′는 시작하지 않았다.
