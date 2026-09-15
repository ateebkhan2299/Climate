import glob
import os
import re

for filepath in glob.glob('d:/climate/templates/*.html'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Viewport Meta tag
    if '<meta name="viewport"' not in content:
        content = content.replace('<head>', '<head>\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">')

    # 2. Add Mobile Menu Toggle Button
    if 'mobile-menu-toggle' not in content:
        # We find hud-header and insert the button inside it, before hud-title
        pattern_header = r'(<header class="hud-header">)'
        btn_html = '\n        <button class="mobile-menu-toggle" onclick="window.EarthScape.toggleMenu()" aria-label="Toggle Menu">☰</button>'
        content = re.sub(pattern_header, r'\1' + btn_html, content)
    
    # 3. Add Nav Overlay
    if 'id="nav-overlay"' not in content:
        pattern_layout = r'(<div class="app-layout">)'
        overlay_html = '<div class="nav-overlay" id="nav-overlay" onclick="window.EarthScape.closeMenu()"></div>\n    '
        content = re.sub(pattern_layout, overlay_html + r'\1', content)

    # 4. Wrap tables for horizontal scrolling
    # We will find <table ...> and wrap it if it is not already wrapped by table-responsive-wrapper
    if 'table-responsive-wrapper' not in content:
        # A simple replacement for <table class="clean-table" id="...">
        # We replace <table with <div class="table-responsive-wrapper"><table
        # And replace </table> with </table></div>
        # But only for tables with class="clean-table" to be safe.
        # Actually it's easier to just do simple string replaces
        content = content.replace('<table class="clean-table"', '<div class="table-responsive-wrapper">\n                <table class="clean-table"')
        content = content.replace('</table>', '</table>\n            </div>')
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("HTML templates successfully updated with responsive elements.")
