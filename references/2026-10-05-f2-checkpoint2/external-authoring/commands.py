"""Record external authoring calls. Only installed images and authored/artifact folders are mounted."""
from pathlib import Path
import json
import subprocess
import time

ROOT = Path(__file__).parent.resolve()
ARTIFACTS = ROOT.parent / 'framework-f2-baseline'
IMAGES = {'solutions': 'rx-f2-solutions:b1', 'platform': 'rx-f2-platform:b1'}


def command(argv, label, category='product', check=True):
    started = time.monotonic()
    result = subprocess.run(list(map(str, argv)), capture_output=True, text=True)
    logs = ROOT / 'logs'; logs.mkdir(exist_ok=True)
    history = ROOT/'commands.jsonl'
    sequence = len(history.read_text().splitlines())+1 if history.exists() else 1
    stem = f'{sequence:04d}-'+label
    (logs/(stem+'.stdout')).write_text(result.stdout)
    (logs/(stem+'.stderr')).write_text(result.stderr)
    (logs / (label + '.stdout')).write_text(result.stdout)
    (logs / (label + '.stderr')).write_text(result.stderr)
    with (ROOT / 'commands.jsonl').open('a') as stream:
        stream.write(json.dumps({'sequence': sequence, 'label': label, 'category': category, 'argv': list(map(str, argv)),
                                 'stdout': str(logs/(stem+'.stdout')), 'stderr': str(logs/(stem+'.stderr')),
                                 'rc': result.returncode, 'wall_seconds': time.monotonic()-started})+'\n')
    if check and result.returncode:
        raise RuntimeError(label + ': ' + result.stderr[-2000:] + result.stdout[-1000:])
    return result


def installed(binary, args, label, role='solutions', check=True):
    argv = ['docker', 'run', '--rm', '--network', 'none', '--user', '0',
            '-v', str(ROOT)+':/author', '-v', str(ARTIFACTS)+':/artifact:ro',
            '--entrypoint', binary, IMAGES[role], *args]
    return command(argv, label, check=check)


def read(path): return json.loads(Path(path).read_bytes())
def write(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')
