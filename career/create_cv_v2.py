from fpdf import FPDF
import os

class CV_PDF(FPDF):
    def header(self):
        # Photo (compressed for LinkedIn <5MB)
        photo_path = r"C:\Users\Admin\Projects\active\photo_compressed.jpg"
        if os.path.exists(photo_path):
            self.image(photo_path, 165, 12, 28, 33)
        
        # Name
        self.set_font('Helvetica', 'B', 20)
        self.set_text_color(26, 82, 118)
        self.cell(150, 8, 'KAMEL MAHI', new_x="LMARGIN", new_y="NEXT")
        
        # Title
        self.set_font('Helvetica', '', 9.5)
        self.set_text_color(41, 128, 185)
        self.cell(150, 4, 'VBA Developer & Decision Support Systems Specialist', new_x="LMARGIN", new_y="NEXT")
        
        # Contact
        self.set_font('Helvetica', '', 7.5)
        self.set_text_color(100, 100, 100)
        self.cell(150, 3.5, '+213 676 773 892  |  kamelmahi71@gmail.com  |  El Bayadh, Algeria', new_x="LMARGIN", new_y="NEXT")
        self.cell(150, 3.5, 'linkedin.com/in/kamelmahi  |  github.com/kamelmh  |  kamelmahi.netlify.app', new_x="LMARGIN", new_y="NEXT")
        
        # Separator
        self.set_draw_color(26, 82, 118)
        self.set_line_width(0.5)
        self.line(10, 50, 200, 50)
        self.set_y(53)
    
    def section(self, title):
        self.set_font('Helvetica', 'B', 9)
        self.set_fill_color(26, 82, 118)
        self.set_text_color(255, 255, 255)
        self.cell(0, 5, '  ' + title, new_x="LMARGIN", new_y="NEXT", fill=True)
        self.set_text_color(0, 0, 0)
        self.ln(1)
    
    def job(self, title, org, date):
        self.set_font('Helvetica', 'B', 8.5)
        self.set_text_color(26, 82, 118)
        self.cell(130, 4, title)
        self.set_font('Helvetica', 'I', 7.5)
        self.set_text_color(120, 120, 120)
        self.cell(0, 4, date, new_x="LMARGIN", new_y="NEXT", align='R')
        self.set_font('Helvetica', 'I', 7.5)
        self.set_text_color(80, 80, 80)
        self.cell(0, 3, org, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(0.5)
    
    def bullet(self, text):
        self.set_font('Helvetica', '', 7.5)
        self.set_x(15)  # indent
        self.multi_cell(180, 3, '- ' + text)
    
    def skill_row(self, cat, val):
        self.set_font('Helvetica', 'B', 7.5)
        self.set_text_color(26, 82, 118)
        self.set_x(15)
        self.cell(30, 3.5, cat)
        self.set_font('Helvetica', '', 7.5)
        self.set_text_color(50, 50, 50)
        self.multi_cell(150, 3.5, val)
        self.set_text_color(0, 0, 0)
    
    def lang_row(self, lang, level, note):
        self.set_font('Helvetica', 'B', 7.5)
        self.set_x(15)
        self.cell(20, 3.5, lang)
        self.set_font('Helvetica', '', 7.5)
        self.cell(35, 3.5, level)
        self.set_text_color(100, 100, 100)
        self.multi_cell(130, 3.5, note)
        self.set_text_color(0, 0, 0)
    
    def highlight_box(self, text):
        self.set_fill_color(240, 248, 255)
        self.set_draw_color(41, 128, 185)
        y = self.get_y()
        self.rect(10, y, 190, 5, 'DF')
        self.set_xy(12, y+0.3)
        self.set_font('Helvetica', 'B', 7)
        self.set_text_color(26, 82, 118)
        self.cell(11, 4.5, 'Impact:')
        self.set_font('Helvetica', '', 7)
        self.set_text_color(50, 50, 50)
        self.multi_cell(165, 4.5, text)
        self.set_text_color(0, 0, 0)
        self.ln(0.5)

pdf = CV_PDF()
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=8)

# PROFESSIONAL SUMMARY
pdf.section('PROFESSIONAL SUMMARY')
pdf.set_font('Helvetica', '', 7.5)
pdf.set_x(15)
pdf.multi_cell(180, 3, 'Results-driven VBA Developer and DSS Specialist with 44 production VBA modules and 113 automated tests deployed at a public institution. Expert in building inventory management ERP systems with SCF-compliant costing (CMUP), Wilson EOQ optimization, ABC classification, and audit trail compliance. BTS in Stock Management & Logistics with a thesis score of 34/36.')
pdf.ln(0.5)

# CORE COMPETENCIES
pdf.section('CORE COMPETENCIES')
pdf.set_font('Helvetica', '', 7)
# Row 1
pdf.cell(5, 3, '')
pdf.cell(47, 3, '- VBA (Advanced - 44 modules)')
pdf.cell(47, 3, '- Python (Intermediate)')
pdf.cell(47, 3, '- Streamlit')
pdf.cell(0, 3, '- SQL / SQLite', new_x="LMARGIN", new_y="NEXT")
# Row 2
pdf.cell(5, 3, '')
pdf.cell(47, 3, '- Excel (Expert)')
pdf.cell(47, 3, '- Git / GitHub')
pdf.cell(47, 3, '- Claude API / AI')
pdf.cell(0, 3, '- Prompt Engineering', new_x="LMARGIN", new_y="NEXT")
# Row 3
pdf.cell(5, 3, '')
pdf.cell(47, 3, '- Multi-Agent Systems')
pdf.cell(47, 3, '- JavaScript / TypeScript')
pdf.cell(47, 3, '- HTML / CSS')
pdf.cell(0, 3, '- Windows / Linux', new_x="LMARGIN", new_y="NEXT")
pdf.ln(0.5)

# KEY PROJECTS
pdf.section('KEY PROJECTS')

# Academix DSS
pdf.job('Academix DSS v14.0 - Inventory Management ERP', "Direction de l'Education d'El Bayadh", '2024 - Present')
pdf.bullet('44 VBA modules: Stock Engine, Wilson EOQ, Barcode/QR, Supplier Scorecard, Budget, Audit Trail, Approval Workflows, Invoicing, Reporting')
pdf.bullet('113 automated tests ensuring code quality and regression prevention')
pdf.bullet('SCF-compliant CMUP (chronological moving average) for accurate stock valuation')
pdf.bullet('Wilson EOQ model: Q*=37, ROP=206, Safety Stock=200 - optimized reorder points')
pdf.bullet('Thesis score: 34/36 - BTS in Stock Management & Logistics')
pdf.highlight_box('~40% reduction in manual stock processing | ~200 articles managed | 26 worksheets')
pdf.ln(0.3)

# Ta'allim
pdf.job("Ta'allim - AI-Powered English Teaching Platform", 'Streamlit Cloud', '2026')
pdf.bullet("Python/Streamlit platform aligned to Algerian Ministry of Education curriculum (1AM-4AM)")
pdf.bullet('72 exercise topics across 4 levels (A1-B2) with auto-generated exercises')
pdf.bullet('17 components: Grammar Engine, Exercise Generator, Assessment System, Auto Grader, Student Dashboard')
pdf.ln(0.5)

# PROFESSIONAL EXPERIENCE
pdf.section('PROFESSIONAL EXPERIENCE')

pdf.job('Freelance VBA Developer & DSS Specialist', 'Self-Employed - Remote', '2024 - Present')
pdf.bullet('Built Academix DSS v14.0: 44 VBA modules, 113 tests, 26-sheet workbook')
pdf.bullet('Implemented Wilson EOQ model for reorder optimization and SCF-compliant CMUP costing')
pdf.bullet('Barcode/QR generation, audit trail, auto-backup, approval workflows')
pdf.ln(0.3)

pdf.job('Freelance Academic Editor', 'Fiverr & Upwork - Remote', '2026 - Present')
pdf.bullet('Academic paper editing, proofreading, citation formatting (APA, MLA, Chicago)')
pdf.bullet('Fiverr: 12/12 profile strength, 2 live gigs, 3 portfolio projects')
pdf.ln(0.3)

pdf.job('English Teacher & MS Office Instructor', 'Private School - El Bayadh', '2024')
pdf.bullet('Taught English language and MS Office Suite to 25+ students')
pdf.ln(0.5)

# EDUCATION
pdf.section('EDUCATION')
pdf.set_font('Helvetica', 'B', 8)
pdf.cell(0, 3.5, 'BTS in Stock Management & Logistics - CNEPD, Algeria', new_x="LMARGIN", new_y="NEXT")
pdf.set_font('Helvetica', '', 7.5)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 3, '2023-2026 | Thesis: 34/36 (defended) | Expected completion: 2026', new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(0, 0, 0)

pdf.set_font('Helvetica', 'B', 8)
pdf.cell(0, 3.5, 'BA in English Language & Literature - Dr. Moulay Tahar University, Saida', new_x="LMARGIN", new_y="NEXT")
pdf.set_font('Helvetica', '', 7.5)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 3, '2015-2020', new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(0, 0, 0)

pdf.set_font('Helvetica', 'B', 8)
pdf.cell(0, 3.5, 'Baccalaureate - Letters & Foreign Languages - El Bayadh', new_x="LMARGIN", new_y="NEXT")
pdf.set_font('Helvetica', '', 7.5)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 3, '2015', new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(0, 0, 0)
pdf.ln(0.5)

# TECHNICAL SKILLS
pdf.section('TECHNICAL SKILLS')
pdf.skill_row('Programming:', 'VBA (Advanced - 44 modules), Python, JavaScript, TypeScript')
pdf.skill_row('Databases:', 'SQLite, CSV/Excel data pipelines, SQL queries, JSON storage')
pdf.skill_row('AI/ML:', 'Claude API, MCP, Prompt Engineering, Multi-Agent Systems')
pdf.skill_row('Frameworks:', 'Streamlit, Pandas, Matplotlib, fpdf2')
pdf.skill_row('Tools:', 'Git, VS Code, Excel (Expert), Obsidian, Playwright')
pdf.skill_row('Logistics:', 'Wilson EOQ, CMUP, ABC Analysis, Procurement, Audit Trail')
pdf.ln(0.5)

# LANGUAGES
pdf.section('LANGUAGES')
pdf.lang_row('Arabic', 'Native', 'Mother tongue, Algerian dialect')
pdf.lang_row('English', 'C1 (Proficient)', 'BA degree, teaching, academic editing')
pdf.lang_row('French', 'B1-B2 (Intermediate+)', 'Working proficiency, CVs in French')
pdf.ln(0.5)

# CERTIFICATIONS
pdf.section('CERTIFICATIONS & TRAINING')
pdf.bullet('CCA-F (Claude Certified Architect) - All 5 domains studied, practice exam complete')
pdf.bullet('Thirduni AI Training Program - Applied (Sep 2026)')
pdf.bullet('Hubert H. Humphrey Fellowship - Preparing (Target: 2028-2029)')
pdf.ln(0.5)

# Footer
pdf.set_font('Helvetica', 'I', 6.5)
pdf.set_text_color(150, 150, 150)
pdf.cell(0, 3, 'References available upon request  |  Last Updated: August 2026', new_x="LMARGIN", new_y="NEXT", align='C')

# Save
output_path = r"C:\Users\Admin\Projects\active\CV_Kamel_Mahi_Professional.pdf"
pdf.output(output_path)
print(f"PDF created: {output_path}")
print(f"Size: {os.path.getsize(output_path)} bytes")
print(f"Pages: {pdf.pages_count}")
