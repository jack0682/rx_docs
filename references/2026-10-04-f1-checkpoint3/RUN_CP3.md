# F1′ CP3 — 혼합 N=3 결과 손실과 원 invocation 정산

P/Host/Executor와 외부 SIM 전송 중계기가 Docker daemon에 분리 실행되어 있다.
새 사용자 객체는 ECC_51 / ECC_99 / ECC_51 순서다. Host와 worker를 중지하지 않는다.

```sh
cp3=/Users/ojaehong/RX_automation/rx_ws/.build/framework-f1-checkpoint3
rxcp3() {
  python3 "$cp3/live3/verification/installed-client/rx" execution \
    --connection "$cp3/live3/operator.json" \
    --state-dir "$cp3/live3/operator-client" "$@"
}
faultcp3() {
  docker exec rx-f1-cp3r3-fault python3 /opt/rx/result-link/link.py \
    --state /data/control "$@"
}
set -o pipefail

faultcp3 arm --publication "$(jq -r '.reference.id' "$cp3/author3/publication.json")" \
  --ordinal 2 --node rotate-align

rxcp3 run "$cp3/author3/publication.json" --count 3 \
  --object "$cp3/author3/object-acceptance-1.json" \
  --object "$cp3/author3/object-acceptance-2.json" \
  --object "$cp3/author3/object-acceptance-3.json" \
  --request-id f071c378-3f18-4bfc-a1f0-4a4d42d6a026 \
  --until-unknown --wait-seconds 180 --output "$cp3/live3/user-unknown.json" |
  jq '{run:.binding.run,state:.result.run.value.state,parts:[.result.parts[].value],
       unknown:[.result.work[]|select(.operation.execution_knowledge=="UNKNOWN")|
         {node:.execution.selection.node,ordinal:.execution.selection.ordinal,
          operation,invocation,resources,reconciliation}],slot_pools}'
```

첫 run의 **종료 코드 2는 예상된 미완료 정지점**이다.
rotate-align의 knowledge=UNKNOWN, disposition=QUARANTINED, 원 operation과
resources[].value.holder 일치를 확인한다. resource.quarantined 플래그와 operation의
disposition은 서로 다른 필드다. Part 2 slot은 consumed=false로 보유되며,
Part 3 slot은 예약돼 있으나 part=null이고 실제 Part 기록은 2개뿐이어야 한다.

저장 기록을 제품 CLI로 다시 읽고 중계기의 실제 native 진입 확인을 대조한다.

```sh
cp3_run=$(jq -r '.binding.run' "$cp3/live3/user-unknown.json")
rxcp3 inspect "$cp3_run" --reports --output "$cp3/live3/user-held.json" |
  jq '{run:.binding.run,parts:[.result.parts[].value],
       unknown:[.result.work[]|select(.operation.execution_knowledge=="UNKNOWN")|
         {operation,invocation,resources,reconciliation}],slot_pools}'
faultcp3 status
```

중계기는 BLOCKED와 실제 NATIVE_ACCEPTED/RESULT_CAPTURED의 원 operation/invocation을
표시한다. 이 상태 파일은 fault의 관측 자료이며 P의 결과나 권한이 아니다.
해당 Run의 native 효과는 이 시점에 12개(Part 1의 9개 + Part 2의 3개)다.

통신만 복구한 뒤 **같은 객체 순서와 request ID**로 원 Run의 진행을 이어간다.

```sh
faultcp3 release

rxcp3 run "$cp3/author3/publication.json" --count 3 \
  --object "$cp3/author3/object-acceptance-1.json" \
  --object "$cp3/author3/object-acceptance-2.json" \
  --object "$cp3/author3/object-acceptance-3.json" \
  --request-id f071c378-3f18-4bfc-a1f0-4a4d42d6a026 \
  --wait-seconds 180 --output "$cp3/live3/user-completed.json" |
  jq '{environment,run:.binding.run,state:.result.run.value.state,
       parts:[.result.parts[].value],
       target:[.result.work[]|select(.execution.selection.ordinal=="2" and
         .execution.selection.node=="rotate-align")|{operation,invocation,reconciliation}],
       operations:(.result.work|length)}'

rxcp3 inspect "$cp3_run" --reports --output "$cp3/live3/user-reopened.json" |
  jq '{environment,run:.binding.run,state:.result.run.value.state,
       selections:[.result.work[].execution.selection],reports:(.approved_reports|keys)}'
```

예상 결과는 같은 Run COMPLETED, 3개 CONFIRMED_COMPLETED Part, 27개
SUCCEEDED/RELEASED operation이다. target의 원 operation/invocation이 유지되고
reconciliation.state=COMPLETE여야 한다. 기존 sender의 receipt 조회와 Executor의
정산 경로가 증거를 회수하며, 새 native 호출로 원 호출을 대체하지 않는다.

이 Run의 장치 ID 쌍과 모델별 실제 소비 값을 대조한다. 사전 확인 Run은 ID로 제외한다.

```sh
docker exec rx-f1-cp3r3-h cat /data/workflow-simulation/effects.jsonl |
  jq -s --slurpfile receipt "$cp3/live3/user-completed.json" '
    ($receipt[0].result.work |
      map({key:.operation.operation_id,value:{invocation,ordinal:.execution.selection.ordinal}}) |
      from_entries) as $expected |
    map(select($expected[.operation] != null)) as $effects |
    {effects:($effects|length),
     unique_pairs:($effects|map([.operation,.invocation])|unique|length),
     matching_invocations:all($effects[]; $expected[.operation].invocation == .invocation),
     values:[$effects[]|select(.node=="pick" or .node=="rotate-align" or .node=="process")|
       {part:$expected[.operation].ordinal,node,slot,operation,invocation,parameters,device}]}'
```

예상 값:

| Part | 모델 | grasp width | grip force | angle/tolerance | process |
|---|---|---:|---:|---:|---:|
| 1 | ECC_51 | 47mm | 25N | 95° / 0.5° | 5s |
| 2 | ECC_99 | 77mm | 17.5N | 185° / 0.3° | 7s |
| 3 | ECC_51 | 47mm | 25N | 95° / 0.5° | 5s |

effects=27, unique_pairs=27, matching_invocations=true이며 각 Part의 순서는
pick → load → rotate-align → clamp → close-door → process → open-door → unload → place다.
기존 출력 파일은 서버 요청 전에 거절하므로 재조회 시 새 경로를 쓰거나 --output을 뺀다.
새 request ID는 복구 명령이 아니다. CP3 사용자 수락 대기에서 멈춘다. F2′/F3′는 미착수다.
