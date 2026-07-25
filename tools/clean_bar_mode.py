"""Remove bar-mode (old mini popup) code from music frontend"""
import re

path = r'D:\fake_yuki\apps\music\frontend\index.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove bar-mode CSS block (from "Bar mode" comment to "player-bar" definition)
content = re.sub(
    r'\n/\* [═]+ Bar mode.*?\n\.player-bar \{ display: flex;',
    '\n.player-bar { display: flex;',
    content, flags=re.DOTALL
)

# 2. Remove popup button from hero
content = content.replace(
    ' <button id="popupBtn" title="弹出独立播放器" style="display:none;font-size:1.2rem;background:none;border:1px solid var(--c-blue);color:var(--c-blue);border-radius:8px;padding:2px 10px;cursor:pointer;margin-left:8px;vertical-align:middle">🔔 弹出</button>',
    ''
)

# 3. Remove popup button JS
content = re.sub(
    r'\n// Popup button:.*?window\.close\(\);\s*\}\);\s*\}',
    '',
    content,
    flags=re.DOTALL
)

# 4. Remove mini bar HTML + script block
content = re.sub(
    r'\n<!-- [═]+ Mini bar popup.*?</script>',
    '',
    content,
    flags=re.DOTALL
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Cleaned bar-mode code")
