# Recoverable local Host binding commit

2026-09-29. Host maintenance now commits a prepared, normally stopped simulation binding replacement using a fresh native generation and an atomic installation-descriptor publication. It retains the original delivery/evidence journal IDs and prior native state. Pending commits block startup/cancellation; lookup separates historical receipt from current installation.

The recovery test launches an actual child process and kills it with SIGKILL at each of three publication boundaries: intent recorded, native generation ready, descriptor published. The original request then completes and repeats without changing the result. Tests also reject changed request identity, staged marker corruption and Arm before the exact P configuration target is acknowledged. No qualification or Arm is restored by restart.

[checks.json](checks.json), [Host suite](binding-commit-host-suite-final.log) and [clippy](binding-commit-clippy-final.log) identify the exercised scope and source. The tests use local FILE_SIMULATION and unchanged scope topology. They do not prove an installed signed-Python-package swap or P's acceptance of a fresh Host transition observation.

P's HOST_BINDING_CHANGE_REQUIRED guard remains. The next implementation must correlate the original staged change with a fresh authenticated Host observation, record contract/compatibility changes and synchronize SDK inputs. Local commit success must not be treated as global configuration application or qualification.
