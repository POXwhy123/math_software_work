"""Read the actual .ggb bytes from disk and verify them in an open isolated GeoGebra browser session."""
import base64
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
WEEK = ROOT / '06-课程成果' / '第01周'
SOURCE = WEEK / 'source' / 'week01-basic-objects.ggb'


def main():
    data = SOURCE.read_bytes()
    encoded = base64.b64encode(data).decode('ascii')
    sha = hashlib.sha256(data).hexdigest()
    # The file is passed to the browser locally over Playwright; no cloud save or HTTP upload.
    script = r'''async (page) => {
      await page.setViewportSize({width:1280,height:820});
      await page.waitForFunction(()=>window.ggbApplet && typeof ggbApplet.setBase64==='function');
      const report = await page.evaluate(async ({base64,sha256})=>{
        const g=ggbApplet;
        await new Promise(resolve=>g.setBase64(base64,resolve));
        const read=()=>({A:[g.getXcoord('A'),g.getYcoord('A')],B:[g.getXcoord('B'),g.getYcoord('B')],M:[g.getXcoord('M'),g.getYcoord('M')],s:g.getValue('s'),circle:g.getValueString('c',false),definitions:{s:g.getCommandString('s',false),M:g.getCommandString('M',false),c:g.getCommandString('c',false)},independent:{A:g.isIndependent('A'),B:g.isIndependent('B'),M:g.isIndependent('M'),s:g.isIndependent('s'),c:g.isIndependent('c')}});
        const initial=read();
        if(JSON.stringify(initial.A)!=='[-2,1]'||JSON.stringify(initial.B)!=='[4,3]'||JSON.stringify(initial.M)!=='[1,2]') throw new Error('Unexpected disk file coordinates');
        const report={checked_at:new Date().toISOString(),source:'source/week01-basic-objects.ggb',source_sha256:sha256,app:'GeoGebra Classic web',api_version:g.getVersion(),method:'Fresh browser session; read .ggb from disk; load via official setBase64 API',initial};
        g.setMode(0);
        const v=JSON.parse(g.getViewProperties(1));
        const screen=(x,y)=>({x:v.left+(x-v.xMin)/v.invXscale,y:v.top+v.height-(y-v.yMin)/v.invYscale});
        window.week01DiskRead=read;
        return {...report,drag:{from:screen(-2,1),to:screen(-3,2)}};
      },{base64:__BASE64__,sha256:__SHA__});
      await page.keyboard.press('Escape');
      // Close only the visible virtual keyboard, if the fresh session opened it.
      const close=page.locator('[data-test="closeKeyboardButton"]');
      if(await close.isVisible()) await close.click();
      await page.screenshot({path:'output/playwright/week01-disk-open.png'});
      // Re-read view properties after the keyboard/layout change.
      const coords=await page.evaluate(()=>{
        const v=JSON.parse(ggbApplet.getViewProperties(1));
        const screen=(x,y)=>({x:v.left+(x-v.xMin)/v.invXscale,y:v.top+v.height-(y-v.yMin)/v.invYscale});
        return {from:screen(-2,1),to:screen(-3,2)};
      });
      await page.mouse.move(coords.from.x,coords.from.y);await page.mouse.down();
      await page.mouse.move(coords.to.x,coords.to.y,{steps:24});await page.mouse.up();
      report.drag={...coords,after:await page.evaluate(()=>window.week01DiskRead())};
      const after=report.drag.after;
      report.passed=JSON.stringify(after.A)==='[-3,2]'&&JSON.stringify(after.M)==='[0.5,2.5]'&&after.independent.A&&after.independent.B&&!after.independent.M&&!after.independent.s&&!after.independent.c;
      if(!report.passed) throw new Error('Disk reload drag check failed');
      await page.screenshot({path:'output/playwright/week01-disk-drag.png'});
      await page.evaluate(async base64=>new Promise(resolve=>ggbApplet.setBase64(base64,resolve)),__BASE64__);
      const pending=page.waitForEvent('download');
      await page.evaluate(report=>{
        const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(report,null,2)],{type:'application/json'}));a.download='disk-reopen-check.json';document.body.append(a);a.click();a.remove();
      },report);
      await (await pending).saveAs('06-课程成果/第01周/evidence/disk-reopen-check.json');
      return {passed:report.passed,source_sha256:report.source_sha256,api_version:report.api_version};
    }'''.replace('__BASE64__', json.dumps(encoded)).replace('__SHA__',json.dumps(sha))
    local = ROOT / '.local' / 'checks'
    local.mkdir(parents=True, exist_ok=True)
    code_file = local / 'week01-reopen.js'
    code_file.write_text(script, encoding='utf-8')
    npx = shutil.which('npx.cmd') or shutil.which('npx')
    if not npx:
        raise SystemExit('npx is required for the optional browser check')
    command=[npx,'--yes','--package','@playwright/cli@0.1.24','playwright-cli','-s=math-week01','run-code','--filename',str(code_file)]
    result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=120)
    (local/'week01-reopen-cli.txt').write_text(result.stdout+result.stderr,encoding='utf-8')
    # CLI errors can be printed while its process still returns 0. Require the resulting evidence.
    evidence=WEEK/'evidence'/'disk-reopen-check.json'
    if result.returncode or not evidence.exists():
        raise SystemExit('Browser reload failed; see .local/checks/week01-reopen-cli.txt')
    report=json.loads(evidence.read_text(encoding='utf-8'))
    if not report['passed'] or report['source_sha256']!=sha:
        raise SystemExit('Browser evidence does not match current .ggb')
    print('Disk .ggb reload and real mouse drag: PASS')
    print('SHA256:',sha)


if __name__=='__main__':
    main()
