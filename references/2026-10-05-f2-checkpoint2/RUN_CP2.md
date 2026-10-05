# F2′ CP2 — external chuck, mixed N=3, same Host binary

Status: **READY FOR USER ACCEPTANCE**. Codex ran the precheck; the user has not accepted CP2.
All targets are SIMULATION. **There is no fresh gripper support observation.** Unclamp uses
only the existing Run's ordering after the same Part's acquire-support operation has settled
successfully. This is weaker than a real cell requires; the registry-observation follow-up
is parked. CP3 has not started.

The live services are detached Docker containers `rx-f2-s1d-p`, `-ha`, `-hb`, `-e`.
Host A uses the unchanged Python builtin; Host B loads the separately authored external
chuck package through the registry. Both use the same B1 rx-hostd SHA-256:
`1332000944c7d4b4fc1c615c117cedb77d9c8c4d0291e6f54f05282b140538b7`.
P/S source changes during S1 authoring: **0 files / +0 −0 lines**.

Read-only inspection of the registered runtime package:

```sh
docker exec rx-f2-s1d-hb /opt/rx/bin/rx-hostd inspect /config/host/startup.json
```

## Run the unused acceptance objects

The precheck consumed slots 0/1/2. The following unused ECC_51/ECC_99/ECC_51 objects
should use slots 3/4/5. Do not reinitialize inventory or replace the request ID to recover
an uncertain result. If this run stops UNKNOWN, preserve it and inspect the same Run.

```sh
cp2=/Users/ojaehong/RX_automation/rx_ws/.build/framework-f2-author4
rxcp2() {
  python3 "$cp2/installed-client/rx" execution \
    --connection "$cp2/site/connections/operator.json" \
    --state-dir "$cp2/user-client" "$@"
}
set -o pipefail

rxcp2 run "$cp2/authoring/publication.json" --count 3 \
  --object "$cp2/authoring/acceptance-1.json" \
  --object "$cp2/authoring/acceptance-2.json" \
  --object "$cp2/authoring/acceptance-3.json" \
  --request-id 45fc67b5-3112-426d-9b28-fc24bfcab56f \
  --until-unknown --wait-seconds 180 --output "$cp2/user-completed.json" |
  jq '{environment,run:.binding.run,state:.result.run.value.state,
       parts:[.result.parts[].value],operations:(.result.work|length),
       states:([.result.work[].operation|[.phase,.outcome,.disposition]]|unique)}'
```

Expected: rc=0, SIM/COMPLETED, 3 CONFIRMED_COMPLETED Parts, 33
SETTLED/SUCCEEDED/RELEASED operations. rc=2 is an incomplete/UNKNOWN stop, not success.

Reopen the same Run and reports:

```sh
cp2_run=$(jq -r '.binding.run' "$cp2/user-completed.json")
rxcp2 inspect "$cp2_run" --reports --output "$cp2/user-reopened.json" |
  jq '{environment,run:.binding.run,state:.result.run.value.state,
       steps:[.result.work[]|{host,node:.execution.selection.node,
         ordinal:.execution.selection.ordinal,operation,invocation}],
       reports:(.approved_reports|keys)}'
```

Each Part's order is pick → load → rotate-align → clamp → close-door → process →
open-door → acquire-support → unclamp → withdraw → place. Clamp/unclamp belong to
`host/sim-b`; the other nine nodes belong to `host/sim`. The predecessor and successor
must share the same Part reference; final status alone is not a fresh sensor observation.

Compare actual native records with this Run's original IDs (excludes precheck records):

```sh
docker exec rx-f2-s1d-hb cat /data/workflow-simulation/effects.jsonl |
  jq -s --slurpfile receipt "$cp2/user-completed.json" '
    ($receipt[0].result.work |
      map({key:.operation.operation_id,value:{invocation,part,
           ordinal:.execution.selection.ordinal,host}})|from_entries) as $expected |
    map(select($expected[.operation] != null)) as $rows |
    {effects:($rows|length),
     unique_pairs:($rows|map([.operation,.invocation])|unique|length),
     matching_invocations:all($rows[]; $expected[.operation].invocation==.invocation),
     external_effects:([$rows[]|select(.primitive=="clamp" or .primitive=="unclamp")]|length),
     sequence:[$rows[]|{part:$expected[.operation].ordinal,node,operation,invocation,
       host:$expected[.operation].host,support_evidence}],
     values:[$rows[]|select(.node=="pick" or .node=="rotate-align" or .node=="process")|
       {part:$expected[.operation].ordinal,node,slot,parameters,device}]}'
```

Expected: 33 effects, 33 unique pairs, matching_invocations=true, six external chuck
effects, and the 11-node order above for each Part. The selected values are:

| Part | Model | Width | Grip force | Angle / tolerance | Process |
|---|---|---|---|---|---|
| 1 | ECC_51 | 47 mm | 25 N | 95° / 0.5° | 5 s |
| 2 | ECC_99 | 77 mm | 17.5 N | 185° / 0.3° | 7 s |
| 3 | ECC_51 | 47 mm | 25 N | 95° / 0.5° | 5 s |

Read the declared chuck observation through the product API:

```sh
python3 "$cp2/installed-client/rx" api \
  --connection "$cp2/site/connections/operator.json" get /api/v1/overview |
  jq '.cells[]|select(.cell.value.id=="cell/a")|.diagnostics.sources[]|
      select(.source=="chuck.clamped")|
      {source,host,usable,age_ns,observation}'
```

Expected after completion: source host/sim-b, boolean/v1, usable=true, value=false.
This is the chuck source, **not a gripper support observation**.

## Evidence and limitations

Precheck Run `01a10ac1-d3af-728b-a228-a7b6ea06565d` completed with the same package/binary
and is available for read-only inspection. [Summary](summary.json), [product receipt](product-receipt.json),
[reopened record](reopened.json), [native effects](effects.jsonl), [source diagnostics](final-diagnostics.json),
[Host inspection refusals](inspection.json), [B1 freeze](B1.json), [cost](cost.json).
Registered inspect rc=0; unregistered, unsigned and tampered cases rc=1. Inspection starts
no native process. Package execution and Run admission still require configuration/qualification.

[Earlier attempts](preserved-attempts.json) remain separate, paused SIM installations with
their original UNKNOWN operations, journals, volumes and process memory. They were not
force-released or reissued. One failed because an authoring copy dereferenced a venv symlink;
the next lost a Python entry acknowledgement near its deadline under concurrent SIM load.
The successful trial preserved the exact time limits and removed that concurrent background
load. This is a bounded normal-run precheck, not a guarantee under arbitrary load or proof
of either CP3 fault case. Do not unpause those failed installations during this acceptance run.

The scope is one authored external package in simulation, authored by Codex with prior
framework knowledge. The independent external-person exercise is still F3′. After handing
over these commands, implementation stops for the user's CP2 decision.
