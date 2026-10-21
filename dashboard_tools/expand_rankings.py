"""Expose cached public points lists separately; derive YK scores only from complete inputs."""
import re,json,hashlib
from pathlib import Path
import openpyxl
from build_rankings import row as old_row,source,P,clean
from player_identity import Identity
IDENTITY=Identity()
def row(rank,name,pos):
    r=old_row(rank,name,pos);pid=IDENTITY.resolve(name)
    if pid.startswith("nba:"):r.update(player_id=pid,identity_status="audited_source_alias")
    return r
from ranking_import import promote,bundle,ROOT
from build_nba_stats import fantasy,WEIGHTS

def build(workbook=None):
    w=openpyxl.load_workbook(P/'dizzle.xlsx',read_only=True,data_only=True)
    rows=[row(r[0],r[1],r[2]) for r in w['October 2026 Dynasty Ranks, Poi'].values if isinstance(r[0],(int,float)) and r[1]]
    source('dizzle_points','Dizzle · dynasty points','dizzle','2026-10-13','dynasty',rows,format='general_points',url='https://docs.google.com/spreadsheets/d/1EmReTa5KUcFFMCy8Fq-NpQG3WU0pMY7XNW54G3EPbEM/edit',rawfile=P/'dizzle.xlsx',notes='October 2026 points tab. Full published player list; exact points coefficients unverified. Browse this source on its own, never aggregate with YK or another unspecified formula.')
    text=(P/'rotowire_points.html').read_text();raw=json.loads(re.search(r'const RWCS_PLAYERS\s*=\s*(\[.*?\]);',text,re.S)[1]);rows=[row(r['rank'],r['name'],r['pos']) for r in raw]
    source('rotowire_general_points','RotoWire · points top 200','rotowire','2026-10-16','full_season',rows,format='general_points',url='https://www.rotowire.com/basketball/article/2026-27-fantasy-basketball-cheat-sheet-for-points-leagues-printable-excel-141449',rawfile=P/'rotowire_points.html',notes='Public printable/exportable top-200 widget in the cached page. YK coefficients unverified; source-specific browsing only.',coverage='published_top_200')
    # Source projections contain rounded shooting makes/attempts for this public 30-player preview.
    text=(P/'hashtag_ros.html').read_text();table=re.findall(r'<table\b.*?</table>',text,re.S)[0];projected=[];custom=[]
    for tr in re.findall(r'<tr\b.*?</tr>',table,re.S):
        cells=re.findall(r'<t[dh]\b[^>]*>(.*?)</t[dh]>',tr,re.S);v=[clean(c) for c in cells]
        if len(v)<17 or not re.match(r'^\d+',v[0]):continue
        # First linked full name; alternate abbreviated label is not part of the name.
        name=clean(re.search(r'<a[^>]*>(.*?)</a>',cells[1],re.S)[1]);r=row(re.match(r'^\d+',v[0])[0],name,v[3]);custom.append(r)
        fg=re.search(r'\(([\d.]+)/([\d.]+)\)',v[7]);ft=re.search(r'\(([\d.]+)/([\d.]+)\)',v[8])
        if not fg or not ft:continue
        stats={k:float(v[i]) for k,i in [('pts',10),('reb',11),('ast',12),('stl',13),('blk',14),('tov',15),('fg3m',9)]};stats.update(fgm=float(fg[1]),fga=float(fg[2]),ftm=float(ft[1]),fta=float(ft[2]))
        projected.append({**r,'source_original_rank':r['original_rank'],'projected_fp_pg':fantasy(stats),'projection_inputs':stats})
    source('hashtag_custom_ros','Hashtag · custom category ROS','hashtag','2026-10-21','rest_of_season',custom,format='custom_categories',url='https://hashtagbasketball.com/fantasy-basketball-projections',rawfile=P/'hashtag_ros.html',notes='Dated cached public preview, 30 players. Source settings use TO 0.25, H2H mode and missed-game penalty; kept apart from standard nine-category lists.',coverage='partial_public_preview_30')
    projected.sort(key=lambda r:-r['projected_fp_pg'])
    for r in projected:r['original_rank']=1+sum(x['projected_fp_pg']>r['projected_fp_pg'] for x in projected)
    if projected:
        promote({'id':'hashtag_yk_model','label':'YK scoring · Hashtag ROS projection preview','publisher':'hashtag','url':'https://hashtagbasketball.com/fantasy-basketball-projections','published_at':'2026-10-21','season':'2026-27','scoring_format':'yk_projection','horizon':'rest_of_season','rank_scope':'overall','coverage':'derived_within_public_preview_30','notes':'Derived FP/G from the 30 accessible projected statistical lines and verified YK coefficients. Rank is within the preview only, not an overall full-pool expert opinion. Rounded inputs; no independent publisher vote. Source category rank retained separately.','points_weights':{'PTS':1,'REB':1,'AST':2,'STL':4,'BLK':4,'FGM':2,'FGA':-1,'FTM':1,'FTA':-1,'3PM':1,'TO':-2},'raw_sha256':hashlib.sha256((P/'hashtag_ros.html').read_bytes()).hexdigest(),'rows':projected})
    if workbook:
        w=openpyxl.load_workbook(workbook,read_only=True,data_only=True)
        rows=[row(r[1],r[0],'') for r in w['Player rankings (Lawson Ranks)'].values if len(r)>1 and isinstance(r[1],(int,float)) and r[0]]
        # Preserve month precision; Feb 1 is solely the conservative age/cache boundary, not a claimed exact publication day.
        promote({'id':'lawson_feb2026','label':'Lawson · February 2026 (day unknown)','publisher':'lawson','url':'file:YK Dynasty Basketball.xlsx#Player rankings (Lawson Ranks)','published_at':'2026-02-01','publication_precision':'month','season':'2025-26','scoring_format':'general_dynasty','horizon':'dynasty','rank_scope':'overall','coverage':'supplied_february_column','notes':'Source heading says Feb 2026; exact day and scoring formula unavailable. Date uses first of month for conservative freshness only. Other tabs/revisions are the same publisher, not independent votes.','rows':rows})
    inventory=json.loads((ROOT/'source/context/ranking_inventory.json').read_text())
    inventory=[x for x in inventory if not any(k in x['name'] for k in ['Lawson','Hashtag ROS','Dizzle points','YK points coverage'])]
    inventory += [{'name':'Full points lists','status':'Dizzle dynasty points and RotoWire current top 200 are browsable separately. Unverified scoring prevents aggregation, not access.'},{'name':'Hashtag projections','status':'Public 30-player ROS preview supports a separately labeled YK FP/G calculation. Full projected FGM/FGA/FTM/FTA export needed for broad YK projection rankings.'},{'name':'FantasyPros / 9cat projections','status':'Public tables provide percentages, not shooting makes and attempts. Exact YK fantasy points cannot be calculated from these fields.'},{'name':'League Winner projections','status':'Visitor response explicitly full=false, 50 visible ranks from total=520; no underlying shooting lines. A dated complete statistical export/access is needed. No attempt to unlock restricted rows.'},{'name':'Lawson / supplied workbooks','status':'February column browsable under General dynasty for 2025–26; day/scoring unknown. Tracker and derived Current Snapshot are duplicate revisions.'}]
    (ROOT/'source/context/ranking_inventory.json').write_text(json.dumps(inventory,indent=2));bundle()
    print('Cached sources expanded;',len(projected),'derived YK preview rows')
if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--workbook',type=Path,help='Optional original YK workbook to reimport the dated Lawson column');args=parser.parse_args();build(args.workbook)
