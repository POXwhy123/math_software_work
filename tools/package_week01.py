"""Create a local Week 01 review snapshot with hashes. No commit, push, PR or remote writes."""
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

from validate_week01 import validate

ROOT=Path(__file__).resolve().parents[1]
WEEK=ROOT/'06-课程成果'/'第01周'
REVIEW_VERSION='week01-v2'


def main():
    # Refuse to package mismatched source and browser evidence.
    validate()
    result=subprocess.run(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT,capture_output=True,check=True)
    paths=sorted(set(p.decode('utf-8') for p in result.stdout.split(b'\0') if p))
    manifest_path=WEEK/'evidence'/'file-manifest.json'
    manifest_name=manifest_path.relative_to(ROOT).as_posix()
    paths=[p for p in paths if p!=manifest_name and (ROOT/p).is_file()]
    assert all(not p.startswith(('.git/','.local/','.playwright/','.playwright-cli/','output/playwright/')) for p in paths)
    files=[{'path':p,'bytes':(ROOT/p).stat().st_size,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in paths]
    manifest={'version':REVIEW_VERSION,'created_at':datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds'),
              'scope':'Vault snapshot for Week 01. Weeks 02-11 contain scaffolding only.',
              'manifest_excludes_itself':True,'files':files}
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    review=ROOT/'.local'/'review'
    review.mkdir(parents=True,exist_ok=True)
    target=review/f'{REVIEW_VERSION}.zip'
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED) as archive:
        for name in paths+[manifest_name]:
            archive.write(ROOT/name,arcname='math_software_work/'+name)
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
    sha=hashlib.sha256(target.read_bytes()).hexdigest()
    target.with_suffix('.zip.sha256').write_text(sha+'  '+target.name+'\n',encoding='ascii')
    print(f'Review archive: .local/review/{target.name}; {len(paths)+1} files; {target.stat().st_size} bytes')
    print('SHA256: '+sha)


if __name__=='__main__':
    main()
