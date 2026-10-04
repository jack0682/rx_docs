# F1′ CP2 — 같은 Run에서 N=3 SIM 직접 실행

전용 Linux arm64 P/Host/Executor가 Docker daemon에 분리 실행되어 있다.
아래는 사용하지 않은 세 object instance를 같은 Run의 Part 1/2/3에 연결한다.
각 Part는 S2의 9단계, rotation 95°/0.5°, process 5초를 수행한다.

```sh
cp2=/Users/ojaehong/RX_automation/rx_ws/.build/framework-f1-checkpoint2
rxcp2() {
  python3 "$cp2/live3/verification/installed-client/rx" execution \
    --connection "$cp2/live3/operator.json" \
    --state-dir "$cp2/live3/operator-client" "$@"
}
set -o pipefail

rxcp2 run "$cp2/author3/publication.json" --count 3 \
  --object "$cp2/author3/object-acceptance-1.json" \
  --object "$cp2/author3/object-acceptance-2.json" \
  --object "$cp2/author3/object-acceptance-3.json" \
  --request-id ef0800f5-90ee-4acb-a6f6-2cd705c1f470 \
  --wait-seconds 180 --output "$cp2/live3/user-receipt.json" |
  jq '{environment,run:.binding.run,state:.result.run.value.state,
       parts:[.result.parts[].value],
       operations:[.result.work[]|{ordinal:.execution.selection.ordinal,
         node:.execution.selection.node,slot:.execution.selection.slot,
         operation:.operation.operation_id,invocation,
         outcome:.operation.outcome,disposition:.operation.disposition}]}'
```

기대 결과는 SIMULATION, 같은 Run의 COMPLETED, 3개 CONFIRMED_COMPLETED Part,
27개 SUCCEEDED/RELEASED operation이다. 각 Part 순서는 pick → load → rotate-align →
clamp → close-door → process → open-door → unload → place다.
CLI는 이전 Part의 CONFIRMED_COMPLETED를 확인한 뒤 다음 객체를 연결한다.
P가 실제 연결·시작 시 현재 권한/참조와 slot/budget을 검사한다.

같은 Run의 고정 보고서·객체·slot·parameter 참조를 다시 연다.

```sh
cp2_run=$(jq -r '.binding.run' "$cp2/live3/user-receipt.json")
rxcp2 inspect "$cp2_run" --reports --output "$cp2/live3/user-reopened.json" |
  jq '{environment,run:.binding.run,state:.result.run.value.state,
       parts:[.result.parts[].value],reports:(.approved_reports|keys),
       selections:[.result.work[].execution.selection]}'
```

장치 기록의 operation/invocation을 이 Run의 제품 기록과 대조한다.
기존 사전 확인 Run의 행은 operation ID로 제외한다.

```sh
docker exec rx-f1-cp2r3-h cat /data/workflow-simulation/effects.jsonl |
  jq -s --slurpfile receipt "$cp2/live3/user-receipt.json" '
    ($receipt[0].result.work |
      map({key:.operation.operation_id,value:.invocation}) | from_entries) as $expected |
    map(select($expected[.operation] != null)) as $effects |
    {expected_operations:($expected|length),
     effect_rows:($effects|length),
     unique_operation_invocation_pairs:($effects|map([.operation,.invocation])|unique|length),
     matching_invocations:all($effects[]; $expected[.operation] == .invocation),
     order:[$effects[]|{node,slot,operation,invocation}]}'
```

기대 값은 27 / 27 / 27 / true다. 이 로그는 상관·중복 대조 자료이며 권한이나
정산 근거를 대신하지 않는다. Run은 P의 operation 기록으로 연결한다.

응답을 잃으면 **같은 세 객체의 순서와 request ID**를 보존하여 run을 재호출한다.
기존 --output 경로는 서버 요청 전에 거절하므로 --output을 빼거나 새 파일을 사용한다.
원 요청 재조회로 새 Run/operation을 만들지 않는다. 새 request ID는 복구 명령이 아니다.
CP3의 무응답 주입·UNKNOWN·정산은 이번 수락 범위에 포함하지 않는다.
