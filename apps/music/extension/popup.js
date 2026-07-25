// Yuki popup — mini player control panel
const API = 'https://music.fake-star.xyz';
let musicTabId = null;
let pollTimer = null;
let lastState = { playing: false, currentTime: 0, duration: 0 };

// DOM
const playingView = document.getElementById('playingView');
const idleView = document.getElementById('idleView');
const elCover = document.getElementById('cover');
const elTitle = document.getElementById('title');
const elArtist = document.getElementById('artist');
const elFill = document.getElementById('progressFill');
const elTimeCur = document.getElementById('timeCur');
const elTimeDur = document.getElementById('timeDur');
const elBtnPlay = document.getElementById('btnPlay');

function fmt(sec) { var m=Math.floor(sec/60),s=Math.floor(sec%60); return m+':'+(s<10?'0':'')+s; }
function setProgress(pct, cur, dur) {
  elFill.style.width = pct+'%';
  elTimeCur.textContent = fmt(cur);
  elTimeDur.textContent = fmt(dur || 0);
}
function setPlaying(v) {
  elBtnPlay.textContent = v ? '⏸' : '▶';
  lastState.playing = v;
}

// Find music station tab
async function findMusicTab() {
  var tabs = await chrome.tabs.query({url: 'https://music.fake-star.xyz/*'});
  return tabs.length ? tabs[0] : null;
}

// Send command to music tab via content script
async function sendCommand(action, data) {
  if (!musicTabId) {
    var t = await findMusicTab();
    if (!t) return false;
    musicTabId = t.id;
  }
  try {
    await chrome.tabs.sendMessage(musicTabId, {type:'YUKI_COMMAND', action:action, data:data||{}});
    return true;
  } catch(e) { musicTabId = null; return false; }
}

// Fetch now-playing from API
async function fetchNowPlaying() {
  try {
    var r = await fetch(API+'/api/now-playing');
    var info = await r.json();
    if (!info.title) return null;
    // Get real-time progress from music tab
    var tabState = await getTabState();
    return { ...info, ...tabState };
  } catch(e) { return null; }
}

async function getTabState() {
  if (!musicTabId) { var t = await findMusicTab(); if (!t) return {}; musicTabId = t.id; }
  try {
    var resp = await chrome.tabs.sendMessage(musicTabId, {type:'YUKI_COMMAND', action:'getState'});
    return resp || {};
  } catch(e) { musicTabId = null; return {}; }
}

// Update UI from state
async function refreshUI() {
  var np = await fetchNowPlaying();
  if (!np || !np.title) {
    playingView.style.display = 'none'; idleView.style.display = '';
    return;
  }
  playingView.style.display = ''; idleView.style.display = 'none';
  elTitle.textContent = np.title;
  elArtist.textContent = np.artist || '';
  elCover.src = np.cover || API + '/default-vinyl.svg';
  if (np.duration) {
    var pct = np.duration > 0 ? (np.currentTime/np.duration*100) : 0;
    setProgress(pct, np.currentTime||0, np.duration);
  }
  setPlaying(np.playing);
}

// Polling
function startPolling() {
  refreshUI();
  pollTimer = setInterval(refreshUI, 1500);
}
function stopPolling() { clearInterval(pollTimer); }
startPolling();

// Controls
document.getElementById('btnPrev').addEventListener('click', function(){ sendCommand('prev'); });
document.getElementById('btnNext').addEventListener('click', function(){ sendCommand('next'); });
document.getElementById('btnPlay').addEventListener('click', async function(){
  if (lastState.playing) { await sendCommand('pause'); setPlaying(false); }
  else { await sendCommand('play'); setPlaying(true); }
});

// Progress rail click → seek
document.getElementById('progressRail').addEventListener('click', function(e){
  var rect = this.getBoundingClientRect();
  var pct = (e.clientX - rect.left) / rect.width;
  sendCommand('seek', {percent: pct});
});

// Open full music station
document.getElementById('openFull').addEventListener('click', function(){
  chrome.tabs.create({url: API});
});
document.getElementById('openMusic').addEventListener('click', function(){
  chrome.tabs.create({url: API});
});

// Cleanup on popup close
window.addEventListener('unload', function(){ stopPolling(); });
