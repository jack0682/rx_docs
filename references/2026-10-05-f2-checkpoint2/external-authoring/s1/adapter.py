"""External S1 FILE_SIMULATION chuck; no Host/P source imports or workflow loop."""
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


sdk = module('external_sdk', Path(__file__).parent / 'sdk/rx_external_adapter.py')
# Reuse the installed S2 example's SIM clamp model, not a platform/Host implementation.
model = module('tending_model', Path('/artifact/s2-source/skill.py'))
DEVICE = Path('/data/workflow-simulation')


class Chuck:
    def state(self):
        if DEVICE.is_symlink() or not DEVICE.is_dir() or DEVICE.stat().st_uid != os.getuid():
            raise ValueError('owned simulated device directory required')
        path = DEVICE / 'state.json'
        if not path.exists():
            return {'schema': 'rx.tending-simulation-state.v1', 'environment': 'FILE_SIMULATION', 'clamped': False}
        state = model.read(path)
        if state['schema'] != 'rx.tending-simulation-state.v1' or state['environment'] != 'FILE_SIMULATION':
            raise ValueError('simulated device identity differs')
        return state

    def execute(self, envelope, correlation):
        operation, invocation = correlation['operation'], correlation['invocation']
        if envelope['primitive'] == 'clamp':
            os.environ['RX_HOST_OPERATION_ID'] = operation
            os.environ['RX_HOST_INVOCATION_ID'] = invocation
            # The existing clamp task also requests the model's gripper release/retreat.
            # This is example model behavior, not a physical gripper support measurement.
            model.main(envelope)
        elif envelope['primitive'] == 'unclamp':
            descriptor = os.open(DEVICE / 'state.lock', os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
                state = self.state()
                selection = {k: envelope[k] for k in ('inputs', 'templates_digest', 'candidate', 'slot')}
                if (state.get('active_selection') != selection or state.get('active_slot') != envelope['slot']
                        or state.get('phase') != 'SUPPORTED' or not state.get('holding')
                        or not state.get('clamped') or state.get('door_closed') or not state.get('process_done')):
                    raise ValueError('same-Part acquire-support model state required')
                before = hashlib.sha256(model.encoded(state)).hexdigest()
                state['clamped'] = False
                state['effects'] += 1
                model.save(DEVICE, state)
                effect = {'environment': 'FILE_SIMULATION', 'operation': operation, 'invocation': invocation,
                          'run': correlation['selection']['run'], 'part': correlation['selection']['part'],
                          'selection': selection, 'node': envelope['node'], 'slot': envelope['slot'],
                          'primitive': 'unclamp', 'parameters': envelope['values'], 'before_digest': before,
                          'after_digest': hashlib.sha256(model.encoded(state)).hexdigest(),
                          'observations': {'chuck.clamped': False},
                          'support_evidence': {'basis': 'OPERATION_ORDER_ONLY', 'fresh_observation': False},
                          'device': {key: state.get(key) for key in ['phase', 'holding', 'clamped', 'door_closed', 'process_done']}}
                fd = os.open(DEVICE / 'effects.jsonl', os.O_WRONLY | os.O_CREAT | os.O_APPEND | os.O_NOFOLLOW, 0o600)
                with os.fdopen(fd, 'ab') as stream:
                    stream.write(model.encoded(effect) + b'\n'); stream.flush(); os.fsync(stream.fileno())
            finally:
                os.close(descriptor)
        else:
            raise ValueError('undeclared chuck command')
        return {'status_schema': 'rx.simulation.chuck-completed.v1', 'status': 0}

    def observe(self, sources):
        state = self.state()
        values = {'sim/ready': True, 'chuck.clamped': state['clamped']}
        return {source: sdk.sample({'boolean': values[source]}) for source in sources}

    def custody(self):
        self.state()
        # FILE_SIMULATION has no physical load or asynchronous controller queue.
        # These provider-control facts do NOT claim a fresh gripper support observation.
        return {'no_pending_commands': True, 'control_available': True,
                'support_stable': True, 'safe_to_drop': True}


sdk.serve(Chuck())
