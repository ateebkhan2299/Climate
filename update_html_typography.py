import os
import glob

print('Updating HTML templates typography...')
for filepath in glob.glob('d:/climate/templates/*.html'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update Plotly Chart Layouts
    content = content.replace("size: 11", "size: 13")
    
    # Update inline styles
    content = content.replace("font-size: 14px;", "font-size: 15px;")
    content = content.replace("font-size:14px;", "font-size:15px;")
    
    # Forms and Inputs in HTML 
    # If there are inline sizes like 12px, bump them to 13px
    content = content.replace("font-size: 12px;", "font-size: 13px;")
    content = content.replace("font-size:12px;", "font-size:13px;")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
print('Updated HTML files.')
