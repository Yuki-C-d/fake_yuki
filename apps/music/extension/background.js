// Background service worker — badge management
const API = 'https://music.fake-star.xyz';
let wasPlaying = false;

async function checkNowPlaying() {
  try {
    var r = await fetch(API+'/api/now-playing');
    var info = await r.json();
    var isPlaying = !!(info && info.title && (Date.now() - (info.time||0) < 300000));
    if (isPlaying !== wasPlaying) {
      wasPlaying = isPlaying;
      if (isPlaying) {
        chrome.action.setBadgeText({text: '♪'});
        chrome.action.setBadgeBackgroundColor({color: '#4A7A9A'});
      } else {
        chrome.action.setBadgeText({text: ''});
      }
    }
  } catch(e) {}
}

// Check every 5 seconds
setInterval(checkNowPlaying, 5000);
checkNowPlaying();
