"""Explicit existing API documents sent only through the installed rx api product command."""
import json
import urllib.parse
import uuid
import time
from commands import ROOT, command, read, write


def get(path, label, who='engineer', **query):
    time.sleep(2)
    if query: path += '?' + urllib.parse.urlencode(query)
    result = command(['python3', str(ROOT/'installed-client/rx'), 'api', '--connection',
                      str(ROOT/'site/connections'/(who+'.json')), '--state-dir', str(ROOT/'site/api-client'),
                      'get', path], label)
    value = json.loads(result.stdout)
    write(ROOT/'site/api-observations'/(label+'-'+uuid.uuid4().hex+'.json'), value)
    return value


def post(path, body, label, who='engineer'):
    time.sleep(2)
    folder = ROOT/'site/api-requests'; folder.mkdir(exist_ok=True)
    file = folder/(label+'.json'); identifier = folder/(label+'.id')
    if file.exists():
        if read(file) != body: raise ValueError('original API body changed: '+label)
    else:
        write(file, body); identifier.write_text(str(uuid.uuid4()))
    result = command(['python3', str(ROOT/'installed-client/rx'), 'api', '--connection',
                      str(ROOT/'site/connections'/(who+'.json')), '--state-dir', str(ROOT/'site/api-client'),
                      'post', path, '--body', str(file), '--request-id', identifier.read_text()], label)
    value = json.loads(result.stdout)
    write(ROOT/'site/api-observations'/(label+'-'+uuid.uuid4().hex+'.json'), value)
    return value


def mutation(path, command_body, label, who='engineer'):
    file = ROOT/'site/api-requests'/(label+'.json')
    body = read(file) if file.exists() else {'request_key': str(uuid.uuid4()), 'command': command_body}
    if body['command'] != command_body: raise ValueError('original mutation command changed')
    return post(path, body, label, who)
