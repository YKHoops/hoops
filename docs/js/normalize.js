/* Small browser adapter: season strings and selected snapshots, never calendar-year arithmetic. */
(function(root) {
  'use strict';
  function season(value) {
    const s = String(value || '').replace(/[–—]/g, '-');
    return /^20\d\d-\d\d$/.test(s) && (Number(s.slice(0,4))+1)%100 === Number(s.slice(5)) ? s : null;
  }
  function select(data, requested) {
    const id = season(requested);
    const selected = data.teams.meta.seasons.includes(id) ? id : data.default_season;
    return {season: selected, roster: data.rosters_by_season[selected] || {
      meta: {season: selected, total_rostered: null, basis: 'No saved roster for this season'},
      players: [], by_owner: {},
    }};
  }
  function previous(value) {
    const s = season(value);
    return s ? `${Number(s.slice(0,4))-1}-${s.slice(2,4)}` : null;
  }
  const api = {season, select, previous};
  if(typeof module !== 'undefined') module.exports = api;
  else root.YKNormalize = api;
})(typeof window === 'undefined' ? this : window);
