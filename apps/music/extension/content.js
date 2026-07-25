// Content script — bridges extension messages to music station page
(function(){
  'use strict';

  // Forward extension commands to page via postMessage
  chrome.runtime.onMessage.addListener(function(msg, sender, sendResponse) {
    if (msg.type !== 'YUKI_COMMAND') return;

    if (msg.action === 'getState') {
      // Query the page for player state
      window.postMessage({type: 'YUKI_COMMAND', action: 'getState'}, '*');
      // Listen for state response
      function onState(e) {
        if (e.data?.type === 'YUKI_STATE') {
          window.removeEventListener('message', onState);
          sendResponse(e.data);
        }
      }
      window.addEventListener('message', onState);
      // Timeout fallback
      setTimeout(function(){
        window.removeEventListener('message', onState);
        sendResponse({playing: false, currentTime: 0, duration: 0});
      }, 500);
      return true; // keep channel open for async response
    }

    // Forward action commands to page
    window.postMessage({type: 'YUKI_COMMAND', action: msg.action, data: msg.data || {}}, '*');
    sendResponse({ok: true});
  });
})();
