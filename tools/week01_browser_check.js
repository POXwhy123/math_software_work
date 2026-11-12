// Run on the five-object Week 01 draft in an isolated GeoGebra Classic session.
// Writes only local Week 01 draft artifacts. No sign-in, cloud save or GitHub writes.
async (page) => {
  const root = '06-课程成果/第01周/';
  await page.setViewportSize({width:1280, height:820});
  await page.waitForFunction(() => window.ggbApplet && ggbApplet.getObjectNumber() >= 5);
  await page.evaluate(() => {
    const g = ggbApplet;
    if (g.getAllObjectNames().sort().join(',') !== 'A,B,M,c,s') throw new Error('Unexpected construction; use the Week 01 draft only');
    g.setCoords('A',-2,1); g.setCoords('B',4,3);
    g.setLabelVisible('s',false); g.setLabelVisible('c',false); g.setMode(0);
    const v = JSON.parse(g.getViewProperties(1));
    const yrange = 12 * v.height / v.width;
    g.setCoordSystem(-5,7,2-yrange/2,2+yrange/2);
    window.week01Evidence = {checked_at:new Date().toISOString(),app:'GeoGebra Classic web',url:location.href,api_version:g.getVersion(),viewport:{width:innerWidth,height:innerHeight},states:[],mouse_drags:[],notes:['The native .ggb is exported by GeoGebra, not manually assembled XML.','No desktop app or Obsidian GUI validation is claimed.']};
    window.week01Read = () => {
      const point = n => [g.getXcoord(n),g.getYcoord(n)];
      const A=point('A'), B=point('B'), M=point('M');
      const matrix=new DOMParser().parseFromString(g.getXML('c'),'application/xml').querySelector('matrix');
      const q=Array.from({length:6},(_,i)=>Number(matrix.getAttribute('A'+i)));
      const center=[-q[4]/q[0],-q[5]/q[1]];
      const radius_squared=center[0]**2+center[1]**2-q[2]/q[0];
      const expectedM=[(A[0]+B[0])/2,(A[1]+B[1])/2];
      const expectedR2=(A[0]-B[0])**2/4+(A[1]-B[1])**2/4;
      const length=g.getValue('s'), expectedLength=Math.hypot(A[0]-B[0],A[1]-B[1]);
      const errors={midpoint:Math.hypot(M[0]-expectedM[0],M[1]-expectedM[1]),center:Math.hypot(center[0]-M[0],center[1]-M[1]),radius_squared:Math.abs(radius_squared-expectedR2),segment_length:Math.abs(length-expectedLength),circle_A:Math.abs((A[0]-center[0])**2+(A[1]-center[1])**2-radius_squared),circle_B:Math.abs((B[0]-center[0])**2+(B[1]-center[1])**2-radius_squared)};
      const independent={}; const definitions={};
      for(const n of ['A','B','s','M','c']) {independent[n]=g.isIndependent(n);definitions[n]=g.getCommandString(n,false);}
      const passed=Object.values(errors).every(e=>Number.isFinite(e)&&e<1e-8)&&independent.A&&independent.B&&!independent.s&&!independent.M&&!independent.c&&g.isDefined('c');
      return {A,B,M,segment_length:length,circle_center:center,radius_squared,circle_matrix:q,independent,definitions,errors,passed};
    };
    window.week01Evidence.states.push({case:'initial',...window.week01Read()});
  });
  await page.screenshot({path:'output/playwright/week01-initial.png'});
  const downloadData = async (base64, filename, mime) => {
    const pending = page.waitForEvent('download');
    await page.evaluate(({base64,filename,mime})=>{
      const bytes=Uint8Array.from(atob(base64),c=>c.charCodeAt(0));
      const url=URL.createObjectURL(new Blob([bytes],{type:mime}));
      const a=document.createElement('a');a.href=url;a.download=filename;document.body.append(a);a.click();a.remove();
    },{base64,filename,mime});
    const download=await pending;
    await download.saveAs(root+filename);
  };
  const saved=await page.evaluate(()=>ggbApplet.getBase64());
  await downloadData(saved,'source/week01-basic-objects.ggb','application/vnd.geogebra.file');
  await downloadData(await page.evaluate(()=>ggbApplet.getPNGBase64(1,false,96)),'output/week01-diagram.png','image/png');
  for(const step of [{name:'A',target:[-3,2],screenshot:'week01-drag-A.png'},{name:'B',target:[3,-1],screenshot:'week01-drag-B.png'}]) {
    const coords=await page.evaluate(({name,target})=>{
      const g=ggbApplet,v=JSON.parse(g.getViewProperties(1));
      const screen=(x,y)=>({x:v.left+(x-v.xMin)/v.invXscale,y:v.top+v.height-(y-v.yMin)/v.invYscale});
      return {from:screen(g.getXcoord(name),g.getYcoord(name)),to:screen(...target),before:window.week01Read()};
    },step);
    await page.mouse.move(coords.from.x,coords.from.y); await page.mouse.down();
    await page.mouse.move(coords.to.x,coords.to.y,{steps:24}); await page.mouse.up();
    const after=await page.evaluate(({name,target,before,coords})=>{
      const state=window.week01Read();
      const moved=Math.hypot(...state[name].map((x,i)=>x-before[name][i]))>0.1;
      const target_error=Math.hypot(...state[name].map((x,i)=>x-target[i]));
      const drag={name,target,from:coords.from,to:coords.to,moved,target_error,state};
      window.week01Evidence.mouse_drags.push(drag);
      window.week01Evidence.states.push({case:'mouse_drag_'+name,...state});
      return drag;
    },{name:step.name,target:step.target,before:coords.before,coords});
    if(!after.moved||!after.state.passed||after.target_error>0.15) throw new Error('Mouse drag failed: '+JSON.stringify(after));
    await page.screenshot({path:'output/playwright/'+step.screenshot});
  }
  await page.evaluate(()=>{
    const g=ggbApplet;
    for(const c of [{name:'horizontal',A:[0,0],B:[4,0]},{name:'vertical',A:[1,-2],B:[1,4]},{name:'decimal',A:[-1.25,2.5],B:[3.75,-0.5]}]) {
      g.setCoords('A',...c.A);g.setCoords('B',...c.B);
      const state=window.week01Read();window.week01Evidence.states.push({case:c.name,...state});
      if(!state.passed) throw new Error('Invariant check failed: '+c.name);
    }
  });
  // Loading the exported bytes after clearing the construction checks GeoGebra's native serialization.
  await page.evaluate(async (base64)=>{
    const g=ggbApplet;g.newConstruction();
    if(g.getObjectNumber()!==0) throw new Error('Construction did not clear');
    await new Promise(resolve=>g.setBase64(base64,resolve));
    const state=window.week01Read();
    if(!state.passed||state.A[0]!==-2||state.B[0]!==4) throw new Error('Exported .ggb reload failed');
    window.week01Evidence.states.push({case:'exported_bytes_reloaded',...state});
    window.week01Evidence.all_passed=window.week01Evidence.states.every(s=>s.passed);
  },saved);
  await page.screenshot({path:'output/playwright/week01-reopened.png'});
  const evidence=await page.evaluate(()=>btoa(unescape(encodeURIComponent(JSON.stringify(window.week01Evidence,null,2)))));
  await downloadData(evidence,'evidence/browser-check.json','application/json');
  return await page.evaluate(()=>({states:week01Evidence.states.length,drags:week01Evidence.mouse_drags.length,all_passed:week01Evidence.all_passed,version:week01Evidence.api_version}));
}
