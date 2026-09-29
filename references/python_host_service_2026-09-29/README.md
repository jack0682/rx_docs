# Installed Python Host backend lifecycle

2026-09-29. The actual rx-hostd Builtin factory loaded a pinned Python registration in the focused RuntimeSkillValidation image. The image source inventory was compared with current source before startup.

The test prepared a separate SDK wheel and skill inside the image, pinned the registration to its Host/cell/installation/ProgramGoal, rejected a PHYSICAL binding and a changed input, initialized the backend, and reached SOFTWARE_READY_UNARMED. Markers placed in skill and SDK module import code remained absent. Clean shutdown returned STOPPED with simulation safe-to-drop. No Python operation was dispatched in this lifecycle scene; execution through the actual Host gate is documented separately.

[result.json](result.json) contains image identity, passive inspection, ready/stop records and negative controls. [source.json](source.json) identifies the implementation. The full Solutions Docker recipe was updated for embedded helper compilation and runtime inventory, but that full image was not rebuilt in this scene.

P-side skill registration, end-to-end P/Executor/Host Python-skill dispatch, typed output propagation, multiple programs per Host and operator reconciliation remain incomplete. The registration file was prepared by test tooling, not a new public registration command. No physical device was attached or operated.
