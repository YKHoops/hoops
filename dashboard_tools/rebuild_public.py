"""Rebuild repaired public bundles offline from cached, reviewed evidence."""
from build_nba_stats import build as nba
from recover_league import build as league
from build_dashboard import build as dashboard
from ranking_import import bundle
from collection_state import publish_snapshot
from workspace import ROOT

def main():
    if (ROOT/'private/fantrax_browser/2025-26-results-blocks.json').exists():
        from import_browser_evidence import build as browser_import
        browser_import()
    nba();league()
    data=dashboard();publish_snapshot(ROOT/'docs/data/dashboard.json',data,ROOT/'private')
    bundle()
    print('Public bundles rebuilt from reviewed caches; no network requests or publishing.')
if __name__=='__main__':main()
