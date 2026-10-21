"""Read supplied context once into a small, reviewable JSON input. No workbook edits.

Run with the bundled Python runtime and the supplied Downloads directory.
The dashboard build consumes the resulting JSON, not the spreadsheets.
"""
import hashlib
import json
from pathlib import Path
import re
import sys
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]


def extract(folder):
    name = 'YK Dynasty Basketball.xlsx'
    book = load_workbook(folder / name, read_only=True, data_only=True)
    sources = []
    for filename in [name, 'yk_trade_analysis.xlsx', 'YK Dynasty Preseason Power Rankings - Year 6.docx',
                     'YK Dynasty Preseason Power Rankings - Year 7.docx',
                     '[ARCHIVED] YK Dynasty BBall Constitution (Feb 21 2026 export).docx']:
        sources.append({'name': filename, 'sha256': hashlib.sha256((folder / filename).read_bytes()).hexdigest()})
    drafts = []
    # Exact recap blocks only. Do not parse repeated historical slot comparisons below them.
    for year, sheet, start, stop in [(2021,'2021',40,49),(2022,'2022',55,64),(2023,'2023',77,87),
                                    (2024,'2024',76,85),(2025,'2025',77,86),(2026,'2026 (Last Season)',77,87)]:
        picks = []
        for row in book[sheet].iter_rows(min_row=start, max_row=stop, max_col=4):
            for col, rnd in [(0,1),(3,2)]:
                cell = row[col]; raw = str(cell.value or '').strip()
                m = re.fullmatch(r'#(\d+):\s*(.+?):\s*(.+)', raw)
                special = {'D43': ('4', 'Herro Ball → HaleTrager', 'Jaden McDaniels'),
                           'D46': ('7', 'Washed Kings → Jowkar', 'Victor Oladipo')}
                if year == 2021 and cell.coordinate in special:
                    slot, picker, selected = special[cell.coordinate]
                elif m:
                    slot, picker, selected = m.groups()
                else:
                    continue
                # Explicit post-selection trade notes do not change who made the selection.
                selected = re.split(r'\s*-\s*>\s*Traded', selected, flags=re.I)[0].strip()
                picks.append({'round': rnd, 'slot': int(slot), 'picker_label': picker,
                              'selected_player': selected, 'raw': raw, 'source_cell': cell.coordinate,
                              'status': 'workbook_record'})
        drafts.append({'draft_year': year, 'season': f'{year}-{str(year+1)[-2:]}',
                       'sheet': sheet, 'source': name, 'picks': picks})
    holdings, conditions = [], {}
    for year in range(2027,2034):
        sheet = '2027 (Year VII Current Season)' if year == 2027 else str(year)
        rows = {i: r for i,r in enumerate(book[sheet].iter_rows(values_only=True),1)}
        for header, begin, end in [(1,2,7),(9,10,16)]:
            for col in [0,2,4,6,8]:
                holder = str(rows[header][col] or '').strip(' *')
                for i in range(begin,end+1):
                    row = rows.get(i,())
                    label = str(row[col] or '').strip() if len(row)>col else ''
                    if not re.match(r'(?i)(1st|2nd|comp|#\d+)', label): continue
                    holdings.append({'draft_year': year,'holder_label': holder,'label':label,
                                     'source': name,'sheet':sheet,'source_cell':f'{get_column_letter(col+1)}{i}',
                                     'status':'workbook_record_unverified'})
        conditions[str(year)] = [str(r[0]).strip() for i,r in rows.items()
                                if 17 <= i <= 20 and r and isinstance(r[0],str) and r[0].startswith(('*','^'))]
    recent_trades = []
    # Bounded, dated FOR blocks. Stop before adjacent roster lists with no trade marker.
    for sheet, first, middle, last, end in [('2026 (Last Season)',18,19,20,32),
                                           ('2027 (Year VII Current Season)',14,15,16,10)]:
        rows = list(book[sheet].iter_rows(min_row=2, max_row=end, max_col=last, values_only=True))
        active = None
        for number, row in enumerate(rows,2):
            if row[middle-1] == 'FOR':
                active = {'sheet':sheet,'source_range':f'{get_column_letter(first)}{number}',
                          'give':[],'get':[],'date':None}
                recent_trades.append(active)
            if active:
                for column, side in [(first,'give'),(last,'get')]:
                    if row[column-1]:active[side].append(str(row[column-1]).strip())
                stamp = row[middle-1]
                if hasattr(stamp, 'isoformat'):
                    active['date'] = stamp.date().isoformat()
                    active['source_range'] += f':{get_column_letter(last)}{number}'
        if active and not active['date']:raise ValueError('Undated new trade block')
    return {'imported_at':'2026-10-21','source_as_of':None,'sources':sources,'drafts':drafts,
            'recent_trades':sorted(recent_trades,key=lambda t:t['date'],reverse=True),
            'holdings':holdings,'pick_conditions':conditions,
            'notes':[
                {'title':'Year VII owner','text':'The Unction is listed under Jared Sands in the Year VII report. The 2026 workbook draft order labels the former Logan slot “Logan (Sands).” Exact handover date is not recorded.', 'source':'YK Dynasty Preseason Power Rankings - Year 7.docx; YK Dynasty Basketball.xlsx, 2026 (Last Season)!A25'},
                {'title':'2026–27 games limit','text':'Year VII reports 35–55 games per regular-season week, with the maximum prorated for double weeks. This supersedes the archived February constitution’s 50-game maximum. Current Fantrax enforcement is not independently verified.', 'source':'YK Dynasty Preseason Power Rankings - Year 7.docx, opening league updates'},
                {'title':'Archived roster rules','text':'The February constitution records 20 main roster spots, 2 G-League spots and 4 IR slots. G-League eligibility is 164 or fewer career games at season start and under 25 FPPG. A five-primary-center cap excludes IR and G-League. These are archived rules, not a fresh eligibility audit.', 'source':'[ARCHIVED] YK Dynasty BBall Constitution (Feb 21 2026 export).docx, Rosters / G-League / Center Restriction'},
                {'title':'2025–26 champion','text':'Year VII reports Nick Jowkar as champion and a 15–0 regular season. The dashboard’s saved standings remain a partial capture and are not overwritten by this report.', 'source':'YK Dynasty Preseason Power Rankings - Year 7.docx, opening paragraph'},
                {'title':'Redistribution remains unresolved','text':'The 2026 redistribution sheet contains proposals, available-player lists and empty team selection columns. It does not establish completed selections. Adjacent picks in the future-picks sheets are retained as recorded.', 'source':'YK Dynasty Basketball.xlsx, 2026 Redistribution Draft'},
                {'title':'Draft chronology','text':'A summer draft belongs to the season beginning that fall. The analysis workbook labels the 2021–2025 drafts by the preceding season; this view uses the primary workbook’s dated recap headings. Multi-owner annotations remain unresolved, and compensatory rounds are not fully reconciled.', 'source':'YK Dynasty Basketball.xlsx, 2021–2026 recap headings; yk_trade_analysis.xlsx, Draft Results'},
            ]}


if __name__ == '__main__':
    data = extract(Path(sys.argv[1]))
    out = ROOT / 'source/context/supplied_context.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')
    print(f"Imported {sum(len(d['picks']) for d in data['drafts'])} draft records and {len(data['holdings'])} future holdings")
