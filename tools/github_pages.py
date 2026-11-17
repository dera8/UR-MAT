"""Inspect/configure this repository's Pages using Git's credential manager.

Credentials stay in memory and are never printed or written to files.
"""
import argparse, json, subprocess, urllib.request, urllib.error

parser=argparse.ArgumentParser()
parser.add_argument('--publish',action='store_true')
args=parser.parse_args()
result=subprocess.run(['git','credential','fill'],input='protocol=https\nhost=github.com\n\n',text=True,capture_output=True)
credential=dict(line.split('=',1) for line in result.stdout.splitlines() if '=' in line)
token=credential.get('password')
if not token:
    raise SystemExit('No GitHub credential available in the configured Git credential manager.')
def api(path,method='GET',data=None):
    req=urllib.request.Request('https://api.github.com/'+path,method=method,data=json.dumps(data).encode() if data is not None else None,headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','User-Agent':'UR-MAT-pages-setup','Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req,timeout=40) as response:
            body=response.read();return json.loads(body) if body else {}
    except urllib.error.HTTPError as error:
        if error.code==404:return None
        raise SystemExit(f'GitHub API returned HTTP {error.code}: {error.reason}')
repo='repos/dera8/UR-MAT'
state=api(repo+'/pages')
if args.publish:
    payload={'build_type':'legacy','source':{'branch':'main','path':'/docs'}}
    state=api(repo+'/pages','PUT' if state else 'POST',payload)
    state=api(repo+'/pages')
if state:
    print(json.dumps({key:state.get(key) for key in ['html_url','status','build_type','source']},indent=2))
    build=api(repo+'/pages/builds/latest')
    if build:print(json.dumps({key:build.get(key) for key in ['status','commit','error','updated_at']},indent=2))
else:print('GitHub Pages is not configured for dera8/UR-MAT.')
