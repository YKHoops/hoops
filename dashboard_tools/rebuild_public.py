"""Stage offline outputs, validate the complete release, then promote dashboard last."""
import json,os,hashlib,shutil,subprocess,sys,tempfile
from pathlib import Path
from build_nba_stats import build as nba
from recover_league import build as league
from build_dashboard import build as dashboard
from ranking_import import bundle
from collection_state import publish_snapshot,atomic_json,validate_snapshot
from workspace import ROOT

def stage_build():
    if (ROOT/'private/fantrax_browser/2025-26-results-blocks.json').exists():
        from import_browser_evidence import build as browser_import
        browser_import()
    nba();league()
    data=dashboard();publish_snapshot(ROOT/'docs/data/dashboard.json',data,ROOT/'private')
    bundle()
    finalize(ROOT)
    if (ROOT/'private/lineup_snapshots/approved.json').exists():
        import importlib.util
        runtime=sys.executable if importlib.util.find_spec('scipy') else str(Path(__file__).resolve().parents[1]/'.lineup-venv/bin/python')
        subprocess.run([runtime,str(Path(__file__).with_name('build_lineups.py'))],check=True)

def finalize(root):
    from build_trade_evaluations import build,validate
    data=json.loads((root/'docs/data/dashboard.json').read_text())
    evaluation=build(data,root);validate(evaluation,data)
    encoded=(json.dumps(evaluation,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
    checksum=hashlib.sha256(encoded).hexdigest();relative='data/trade-evaluations/'+checksum+'.json'
    path=root/'docs'/relative;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(encoded)
    data['trade_evaluations']={'path':relative,'sha256':checksum,'dashboard_sha256':evaluation['dashboard_sha256']}
    atomic_json(root/'docs/data/trade_evaluations.json',evaluation)
    validate_snapshot(data);atomic_json(root/'docs/data/dashboard.json',data)
    return evaluation['audit']

def main():
    if '--stage' in sys.argv:return stage_build()
    # Existing public files remain untouched if any collector/build/validation fails.
    with tempfile.TemporaryDirectory(prefix='yk-release-',dir=ROOT/'private') as temporary:
        stage=Path(temporary);(stage/'docs').mkdir()
        shutil.copytree(ROOT/'docs/data',stage/'docs/data')
        for name in ['source','private']:(stage/name).symlink_to(ROOT/name,target_is_directory=True)
        env={**os.environ,'YK_DASHBOARD_WORKSPACE':str(stage)}
        subprocess.run([sys.executable,__file__,'--stage'],env=env,check=True)
        # Ignore offline invocation timestamps, preserving meaningful capture metadata.
        for name in ['nba_stats.json','rankings.json','dashboard.json']:
            old=ROOT/'docs/data'/name;new=stage/'docs/data'/name
            before=json.loads(old.read_text()) if old.exists() else {};after=json.loads(new.read_text())
            def stable(v):
                if isinstance(v,dict):return {k:stable(x) for k,x in v.items() if k!='built_at'}
                if isinstance(v,list):return [stable(x) for x in v]
                return v
            if stable(before)==stable(after):new.write_bytes(old.read_bytes())
        # Content-addressed evaluations arrive first. dashboard.json is the commit point;
        # old readers keep their old immutable evaluation URL throughout promotion.
        paths=sorted((stage/'docs/data').rglob('*.json'),key=lambda p:(p.name=='dashboard.json',p.name=='lineups.json',str(p)))
        backup=ROOT/'private/trade_releases'/hashlib.sha256((ROOT/'docs/data/dashboard.json').read_bytes()).hexdigest()
        backup.mkdir(parents=True,exist_ok=True)
        changed=[]
        try:
            for path in paths:
                target=ROOT/'docs/data'/path.relative_to(stage/'docs/data');raw=path.read_bytes()
                if target.exists() and target.read_bytes()==raw:continue
                prev=target.read_bytes() if target.exists() else None;changed.append((target,prev))
                if prev is not None:
                    saved=backup/path.relative_to(stage/'docs/data');saved.parent.mkdir(parents=True,exist_ok=True);saved.write_bytes(prev)
                target.parent.mkdir(parents=True,exist_ok=True)
                tmp=target.with_suffix('.pending');tmp.write_bytes(raw);os.replace(tmp,target)
        except Exception:
            for target,prev in reversed(changed):
                if prev is None:target.unlink(missing_ok=True)
                else:
                    tmp=target.with_suffix('.rollback');tmp.write_bytes(prev);os.replace(tmp,target)
            raise
        print('Validated offline release promoted:',len(changed),'changed public files. No network or site publication.')
if __name__=='__main__':main()
