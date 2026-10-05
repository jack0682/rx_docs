"""Offline Ed25519 signing of bytes emitted by installed product tools; no test signer."""
import hashlib
import os
from pathlib import Path
from commands import ROOT, command, installed, read, write

os.umask(0o077)
PRIVATE = ROOT/'private'; PRIVATE.mkdir(exist_ok=True)


def key(role):
    private = PRIVATE/(role+'.pem')
    public = PRIVATE/(role+'.der')
    if not private.exists():
        command(['openssl', 'genpkey', '-algorithm', 'ED25519', '-out', private], role+'-key', 'signer')
        command(['openssl', 'pkey', '-in', private, '-pubout', '-outform', 'DER', '-out', public], role+'-public', 'signer')
    data = public.read_bytes()
    if len(data) != 44 or data[:12].hex() != '302a300506032b6570032100':
        raise ValueError('unexpected Ed25519 public key encoding')
    return private, data[12:].hex()


def sign(request, output, role):
    private, public = key(role)
    request, output = Path(request), Path(output)
    document = read(request)
    raw = bytes.fromhex(document['message_hex'])
    if hashlib.sha256(raw).hexdigest() != document['message_digest']:
        raise ValueError('product signing bytes differ from message digest')
    message = PRIVATE/(output.stem+'.message')
    signature = PRIVATE/(output.stem+'.signature')
    message.write_bytes(raw)
    command(['openssl', 'pkeyutl', '-sign', '-rawin', '-inkey', private,
             '-in', message, '-out', signature], output.stem+'-sign', 'signer')
    write(output, {'key': document['key'], 'signature': signature.read_bytes().hex()})
    return public


if __name__ == '__main__':
    base = read(ROOT/'base-package-policy.json')
    for label in ['robot', 's1']:
        if not (ROOT/(label+'-signing.json')).exists():
            installed('/opt/rx/bin/rx-device-package', ['request', '/author/'+label+'-candidate',
                      'f2-package-signer', '/author/'+label+'-signing.json'], label+'-signing-request')
        public = sign(ROOT/(label+'-signing.json'), ROOT/(label+'-signature.json'), 'package')
        manifest = read(ROOT/(label+'-candidate/manifest.json'))
        policy = read(ROOT/'base-package-policy.json')
        policy.update(contracts=manifest['contracts'], target=manifest['targets'][0], dependencies=[])
        policy['keys'] = [{'id': 'f2-package-signer', 'publisher': 'f2-author', 'verifying_key': public,
                           'kinds': ['DEVICE'], 'permissions': manifest['permissions']}]
        files = {hashlib.sha256(file.read_bytes()).hexdigest(): file
                 for file in (ROOT/(label+'-candidate')).rglob('*') if file.is_file()}
        policy['assets'] = [{'reference': item, 'path': '/author/'+str(files[item['sha256']].relative_to(ROOT))}
                            for item in manifest['assets']]
        write(ROOT/(label+'-policy.json'), policy)
        installed('/opt/rx/bin/rx-device-package', ['seal', '/author/'+label+'-candidate',
                  '/author/'+label+'-signature.json', '/author/'+label+'-policy.json', '/author/'+label+'-package'], label+'-seal')
        installed('/opt/rx/bin/rx-device-package', ['inspect', '/author/'+label+'-package',
                  '/author/'+label+'-policy.json'], label+'-inspect')
    installed('/opt/rx/bin/rx-device-package', ['external-register', '/author/s1-package', '/author/s1-policy.json',
              'example/pneumatic-chuck', '/author/registry.json'], 's1-register')
    print('Signed external package registered as availability only. No activation or native execution.')
