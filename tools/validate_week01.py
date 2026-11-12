"""Check Week 01 native source, saved browser evidence and PNG artifacts; no third-party packages."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
WEEK = ROOT / '06-课程成果' / '第01周'


def validate():
    lines=[]
    source=WEEK/'source'/'week01-basic-objects.ggb'
    with zipfile.ZipFile(source) as archive:
        assert archive.testzip() is None, 'Corrupt .ggb ZIP entry'
        xml=ET.fromstring(archive.read('geogebra.xml'))
        construction=xml.find('construction')
        elements={e.get('label'):e for e in construction.findall('element')}
        assert set(elements)=={'A','B','s','M','c'}, 'Unexpected native objects'
        commands={c.find('output').get('a0'):c for c in construction.findall('command')}
        for label,name,args in [('s','Segment',['A','B']),('M','Midpoint',['A','B']),('c','Circle',['M','A'])]:
            command=commands[label]
            assert command.get('name')==name, f'Wrong command: {label}'
            assert [command.find('input').get('a0'),command.find('input').get('a1')]==args, f'Wrong dependencies: {label}'
        for label,expected in [('A',(-2,1)),('B',(4,3)),('M',(1,2))]:
            coords=elements[label].find('coords')
            z=float(coords.get('z'))
            actual=(float(coords.get('x'))/z,float(coords.get('y'))/z)
            assert actual==expected, f'Wrong saved coordinates: {label}'
    lines.append('PASS: native .ggb ZIP CRC, five objects, construction dependencies and initial coordinates')
    sha=hashlib.sha256(source.read_bytes()).hexdigest()
    evidence=json.loads((WEEK/'evidence'/'browser-check.json').read_text(encoding='utf-8'))
    cases={s['case'] for s in evidence['states']}
    assert cases=={'initial','mouse_drag_A','mouse_drag_B','horizontal','vertical','decimal','exported_bytes_reloaded'}
    assert len(evidence['states'])==7 and evidence['all_passed'] is True
    max_error=0
    for state in evidence['states']:
        assert state['passed'] is True
        independent=state['independent']
        assert independent=={'A':True,'B':True,'s':False,'M':False,'c':False}
        A,B,M=state['A'],state['B'],state['M']
        assert math.dist(M,[(A[0]+B[0])/2,(A[1]+B[1])/2])<1e-8
        assert abs(state['segment_length']-math.dist(A,B))<1e-8
        for error in state['errors'].values():
            assert math.isfinite(error) and error<1e-8
            max_error=max(max_error,error)
    assert len(evidence['mouse_drags'])==2
    for drag in evidence['mouse_drags']:
        assert drag['moved'] is True and drag['target_error']<0.15
    lines.append(f'PASS: seven recorded browser states and two real mouse drags; maximum numerical residual {max_error:.17g}')
    disk=json.loads((WEEK/'evidence'/'disk-reopen-check.json').read_text(encoding='utf-8'))
    assert disk['passed'] is True and disk['source_sha256']==sha
    assert disk['initial']['A']==[-2,1] and disk['initial']['M']==[1,2]
    assert disk['drag']['after']['A']==[-3,2] and disk['drag']['after']['M']==[0.5,2.5]
    lines.append('PASS: fresh-session disk reload evidence matches the current source SHA-256 and expected drag result')
    pngs=sorted((WEEK/'output').glob('*.png'))
    assert len(pngs)>=6, 'Missing previews'
    for png in pngs:
        header=png.read_bytes()[:24]
        assert header[:8]==b'\x89PNG\r\n\x1a\n', f'Not PNG: {png.name}'
        width,height=struct.unpack('>II',header[16:24])
        assert width>100 and height>100
    lines.append(f'PASS: {len(pngs)} PNG files have valid signatures and nontrivial dimensions (visual review is separate)')
    lines.append('Source SHA-256: '+sha)
    lines.append('Limits: checks stored evidence, not a new browser execution; desktop GeoGebra and Obsidian GUI remain manual.')
    lines.append('RESULT: PASS.')
    return '\n'.join(lines)+'\n'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-report',action='store_true')
    args=parser.parse_args()
    try:
        report=validate()
    except (AssertionError,OSError,ValueError,KeyError,zipfile.BadZipFile,ET.ParseError) as exc:
        print('RESULT: FAIL:',str(exc))
        return 1
    if args.write_report:
        (WEEK/'evidence'/'selfcheck.txt').write_text(report,encoding='utf-8',newline='\n')
    print(report,end='')
    return 0


if __name__=='__main__':
    sys.exit(main())
