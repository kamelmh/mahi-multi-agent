import markdown
import os
import sys

def md_to_html(md_path, html_path):
    """Convert markdown file to styled HTML for browser print-to-PDF."""
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert markdown to HTML
    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
    
    # Wrap in full HTML with styling
    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>CV - MAHI Kamel Abdelghani</title>
    <style>
        @page {{
            size: A4;
            margin: 1.5cm;
        }}
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 11pt;
            line-height: 1.4;
            color: #333;
            max-width: 210mm;
            margin: 0 auto;
            padding: 15mm;
        }}
        h1 {{
            color: #1a5276;
            font-size: 22pt;
            border-bottom: 2px solid #1a5276;
            padding-bottom: 5px;
            margin-bottom: 8px;
        }}
        h2 {{
            color: #2c3e50;
            font-size: 13pt;
            border-bottom: 1px solid #bdc3c7;
            padding-bottom: 3px;
            margin-top: 12px;
            margin-bottom: 6px;
        }}
        h3 {{
            color: #34495e;
            font-size: 11pt;
            margin-top: 8px;
            margin-bottom: 4px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 6px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 4px 8px;
            text-align: left;
            font-size: 10pt;
        }}
        th {{
            background-color: #1a5276;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        strong {{
            color: #1a5276;
        }}
        a {{
            color: #2980b9;
            text-decoration: none;
        }}
        ul, ol {{
            margin: 4px 0;
            padding-left: 18px;
        }}
        li {{
            margin: 2px 0;
        }}
        hr {{
            border: none;
            border-top: 1px solid #ccc;
            margin: 10px 0;
        }}
        p {{
            margin: 4px 0;
        }}
        @media print {{
            body {{
                padding: 0;
            }}
        }}
    </style>
</head>
<body>
    {html_content}
    <script>
        // Auto-trigger print dialog for easy PDF export
        window.onload = function() {{
            // Don't auto-print, let user decide
            document.title = 'CV_MAHI_Technical.pdf';
        }};
    </script>
</body>
</html>"""
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print(f"HTML created: {html_path}")
    print(f"Open in browser and press Ctrl+P to save as PDF")

if __name__ == "__main__":
    base_dir = r"C:\Users\Admin\My Drive\LifeWorkspace\01_Identities_&_Assets"
    
    # Technical CV
    tech_md = os.path.join(base_dir, "CV_MAHI_Technical.md")
    tech_html = os.path.join(base_dir, "CV_MAHI_Technical.html")
    if os.path.exists(tech_md):
        md_to_html(tech_md, tech_html)
    
    # Academic CV
    acad_md = os.path.join(base_dir, "CV_MAHI_Academic.md")
    acad_html = os.path.join(base_dir, "CV_MAHI_Academic.html")
    if os.path.exists(acad_md):
        md_to_html(acad_md, acad_html)
    
    print("\nDone! Open the HTML files in Chrome and press Ctrl+P > Save as PDF")
