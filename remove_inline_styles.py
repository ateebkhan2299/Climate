import glob
import os

for filepath in glob.glob('d:/climate/templates/*.html'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replacing 2fr 1fr
    content = content.replace('class="split-row" style="display:grid; grid-template-columns:2fr 1fr; gap:24px;"', 'class="split-row-2-1"')
    
    # Replacing 1fr 1fr with class="split-row"
    content = content.replace('class="split-row" style="display:grid; grid-template-columns:1fr 1fr; gap:24px;"', 'class="split-row"')
    
    # For analytics.html which doesn't have class="split-row" on those elements originally:
    content = content.replace('style="display:grid; grid-template-columns:1fr 1fr; gap:24px;"', 'class="split-row"')
    
    # Let's also check for any padding left from main-viewport that might cause overflow. 
    # In theme.css I already changed it to padding: 16px; on mobile which is fine.
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Inline grid styles removed from HTML templates.")
