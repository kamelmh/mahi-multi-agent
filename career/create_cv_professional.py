from fpdf import FPDF
import os

class Professional_CV(FPDF):
    def header(self):
        # Photo
        photo_path = r"C:\Users\Admin\My Drive\LifeWorkspace\01_Identities_&_Assets\_Originals\Personal pic.png"
        if os.path.exists(photo_path):
            self.image(photo_path, 162, 8, 32, 38)
        
        # Name
        self.set_font('Helvetica', 'B', 24)
        self.set_text_color(26, 82, 118)
        self.cell(0, 12, 'KAMEL MAHI', 0, 1, 'L')
        
        # Title
        self.set_font('Helvetica', '', 11)
        self.set_text_color(41, 128, 185)
        self.cell(0, 6, 'VBA Developer & Decision Support Systems Specialist', 0, 1, 'L')
        
        # Contact line
        self.set_font('Helvetica', '', 8.5)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, '+213 676 773 892  |  kamelmahi71@gmail.com  |  El Bayadh, Algeria', 0, 1, 'L')
        self.cell(0, 5, 'linkedin.com/in/kamel-adelghani-mahi  |  github.com/kamelmh  |  kamelmahi.netlify.app', 0, 1, 'L')
        
        # Separator
        self.set_draw_color(26, 82, 118)
        self.set_line_width(0.8)
        self.line(10, self.get_y()+3, 200, self.get_y()+3)
        self.ln(6)
    
    def section_title(self, title):
        self.set_font('Helvetica', 'B', 11)
        self.set_fill_color(26, 82, 118)
        self.set_text_color(255, 255, 255)
        self.cell(0, 7, '  ' + title, 0, 1, 'L', True)
        self.set_text_color(0, 0, 0)
        self.ln(2)
    
    def job_header(self, title, company, date):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(26, 82, 118)
        self.cell(140, 5, title, 0, 0, 'L')
        self.set_font('Helvetica', 'I', 9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 5, date, 0, 1, 'R')
        self.set_font('Helvetica', 'I', 9)
        self.set_text_color(80, 80, 80)
        self.cell(0, 5, company, 0, 1, 'L')
        self.set_text_color(0, 0, 0)
    
    def bullet(self, text, bold_prefix=''):
        self.set_font('Helvetica', '', 9)
        x = self.get_x()
        self.cell(8, 4.5, '  - ', 0, 0)
        if bold_prefix:
            self.set_font('Helvetica', 'B', 9)
            self.cell(self.get_string_width(bold_prefix)+1, 4.5, bold_prefix, 0, 0)
            self.set_font('Helvetica', '', 9)
        self.multi_cell(180, 4.5, text)
    
    def skill_row(self, category, skills):
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(26, 82, 118)
        self.cell(45, 5, category, 0, 0)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(50, 50, 50)
        self.cell(0, 5, skills, 0, 1)
        self.set_text_color(0, 0, 0)
    
    def lang_row(self, lang, level, notes):
        self.set_font('Helvetica', 'B', 9)
        self.cell(30, 5, lang, 0, 0)
        self.set_font('Helvetica', '', 9)
        self.cell(40, 5, level, 0, 0)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, notes, 0, 1)
        self.set_text_color(0, 0, 0)
    
    def highlight_box(self, text):
        self.set_fill_color(240, 248, 255)
        self.set_draw_color(41, 128, 185)
        x = self.get_x()
        y = self.get_y()
        self.rect(x, y, 190, 8, 'DF')
        self.set_xy(x+3, y+1)
        self.set_font('Helvetica', 'B', 8.5)
        self.set_text_color(26, 82, 118)
        self.cell(15, 6, 'Impact:', 0, 0)
        self.set_font('Helvetica', '', 8.5)
        self.set_text_color(50, 50, 50)
        self.cell(0, 6, text, 0, 1)
        self.set_text_color(0, 0, 0)
        self.ln(2)

# Create PDF
pdf = Professional_CV()
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=12)

# PROFESSIONAL SUMMARY
pdf.section_title('PROFESSIONAL SUMMARY')
pdf.set_font('Helvetica', '', 9.5)
pdf.multi_cell(0, 5, 'Results-driven VBA Developer and DSS Specialist with 44 production VBA modules and 113 automated tests deployed at a public institution. Expert in building inventory management ERP systems with SCF-compliant costing (CMUP), Wilson EOQ optimization, ABC classification, and audit trail compliance. BTS in Stock Management & Logistics with a thesis score of 34/36. Proficient in Python, Streamlit, and AI/ML integration.')
pdf.ln(2)

# CORE COMPETENCIES
pdf.section_title('CORE COMPETENCIES')
pdf.set_font('Helvetica', '', 9)
competencies = [
    'VBA (Advanced - 44 modules production)', 'Python (Intermediate)', 'Streamlit',
    'SQL / SQLite', 'Excel (Expert)', 'Git / GitHub',
    'Claude API / AI', 'Prompt Engineering', 'Multi-Agent Systems',
    'JavaScript / TypeScript', 'HTML / CSS', 'Windows / Linux'
]
for i, comp in enumerate(competencies):
    if i % 4 == 0:
        pdf.cell(0, 5, '', 0, 1)
    pdf.cell(5, 5, '', 0, 0)
    pdf.set_font('Helvetica', 'B', 8.5)
    pdf.set_text_color(26, 82, 118)
    pdf.cell(2, 5, '-', 0, 0)
    pdf.set_font('Helvetica', '', 8.5)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(45, 5, comp, 0, 0)
    pdf.set_text_color(0, 0, 0)
pdf.ln(4)

# KEY PROJECTS
pdf.section_title('KEY PROJECTS')

# Academix DSS
pdf.job_header('Academix DSS v14.0 - Inventory Management ERP', 'Direction de l\'Education d\'El Bayadh', '2024 - Present')
pdf.bullet('44 VBA modules: Stock Engine, Wilson EOQ, Barcode/QR, Supplier Scorecard, Budget, Audit Trail, Approval Workflows, Invoicing, Reporting')
pdf.bullet('113 automated tests with full test suite ensuring code quality')
pdf.bullet('SCF-compliant CMUP (chronological moving average) for accurate stock valuation')
pdf.bullet('Wilson EOQ model: Q*=37 units, ROP=206, Safety Stock=200')
pdf.bullet('Thesis score: 34/36 - BTS in Stock Management & Logistics')
pdf.highlight_box('~40% reduction in manual stock processing | ~200 articles managed | 26 worksheets | Full audit trail')
pdf.ln(1)

# Ta'allim
pdf.job_header("Ta'allim - AI-Powered English Teaching Platform", 'Streamlit Cloud', '2026')
pdf.bullet('Python/Streamlit platform aligned to Algerian Ministry of Education curriculum (1AM-4AM)')
pdf.bullet('72 exercise topics across 4 levels (A1-B2) with auto-generated exercises')
pdf.bullet('17 components: Grammar Engine, Exercise Generator, Assessment System, Auto Grader, Student Dashboard')
pdf.bullet('Multi-user authentication, PDF export, usage tracking, Arabic bilingual labels')
pdf.ln(2)

# PROFESSIONAL EXPERIENCE
pdf.section_title('PROFESSIONAL EXPERIENCE')

pdf.job_header('Freelance VBA Developer & DSS Specialist', 'Self-Employed - Remote', '2024 - Present')
pdf.bullet('Built Academix DSS v14.0: 44 VBA modules, 113 tests, 26-sheet workbook')
pdf.bullet('Implemented Wilson EOQ model for reorder optimization')
pdf.bullet('SCF-compliant CMUP, barcode/QR generation, audit trail, auto-backup')
pdf.bullet('Deployed at Direction de l\'Education d\'El Bayadh - thesis score 34/36')
pdf.ln(1)

pdf.job_header('Freelance Academic Editor', 'Fiverr & Upwork - Remote', '2026 - Present')
pdf.bullet('Academic paper editing, proofreading, citation formatting (APA, MLA, Chicago)')
pdf.bullet('Fiverr: 12/12 profile strength, 2 live gigs, 3 portfolio projects')
pdf.bullet('Upwork: $20/hr, 6 portfolio items')
pdf.ln(1)

pdf.job_header('English Teacher & MS Office Instructor', 'Private School - El Bayadh', '2024')
pdf.bullet('Taught English language and MS Office Suite to 25+ students')
pdf.bullet('Created curriculum materials and assessments aligned to ministry standards')
pdf.ln(2)

# EDUCATION
pdf.section_title('EDUCATION')
pdf.set_font('Helvetica', 'B', 9)
pdf.cell(0, 5, 'BTS in Stock Management & Logistics - CNEPD, Algeria', 0, 1)
pdf.set_font('Helvetica', '', 9)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 5, '2023-2026 | Thesis: 34/36 (defended) | Expected completion: 2026', 0, 1)
pdf.set_text_color(0, 0, 0)
pdf.ln(1)

pdf.set_font('Helvetica', 'B', 9)
pdf.cell(0, 5, 'BA in English Language & Literature - Dr. Moulay Tahar University, Saida', 0, 1)
pdf.set_font('Helvetica', '', 9)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 5, '2015-2020', 0, 1)
pdf.set_text_color(0, 0, 0)
pdf.ln(1)

pdf.set_font('Helvetica', 'B', 9)
pdf.cell(0, 5, 'Baccalaureate - Letters & Foreign Languages - Lycée Mohamed Belkhir, El Bayadh', 0, 1)
pdf.set_font('Helvetica', '', 9)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 5, '2015', 0, 1)
pdf.set_text_color(0, 0, 0)
pdf.ln(2)

# TECHNICAL SKILLS
pdf.section_title('TECHNICAL SKILLS')
pdf.skill_row('Programming:', 'VBA (Advanced - 44 modules), Python, JavaScript, TypeScript')
pdf.skill_row('Databases:', 'SQLite, CSV/Excel data pipelines, SQL queries, JSON storage')
pdf.skill_row('AI/ML:', 'Claude API, MCP, Prompt Engineering, Multi-Agent Systems')
pdf.skill_row('Frameworks:', 'Streamlit, Pandas, Matplotlib, fpdf2')
pdf.skill_row('Tools:', 'Git, VS Code, Excel (Expert), Obsidian, Playwright')
pdf.skill_row('Logistics:', 'Wilson EOQ, CMUP, ABC Analysis, Procurement, Audit Trail')
pdf.ln(2)

# LANGUAGES
pdf.section_title('LANGUAGES')
pdf.lang_row('Arabic', 'Native', 'Mother tongue, Algerian dialect')
pdf.lang_row('English', 'C1 (Proficient)', 'BA degree, teaching, academic editing')
pdf.lang_row('French', 'B1-B2 (Intermediate+)', 'Working proficiency, CVs in French')
pdf.ln(2)

# CERTIFICATIONS
pdf.section_title('CERTIFICATIONS & TRAINING')
pdf.bullet('CCA-F (Claude Certified Architect) - All 5 domains studied, practice exam complete')
pdf.bullet('Thirduni AI Training Program - Applied (Sep 2026)')
pdf.bullet('Hubert H. Humphrey Fellowship - Preparing (Target: 2028-2029)')
pdf.ln(2)

# INTERESTS
pdf.section_title('INTERESTS')
pdf.bullet('AI-powered automation and multi-agent systems')
pdf.bullet('Open source software development')
pdf.bullet('Academic research and publishing')
pdf.bullet('Educational technology innovation')
pdf.ln(3)

# Footer
pdf.set_font('Helvetica', 'I', 8)
pdf.set_text_color(150, 150, 150)
pdf.cell(0, 5, 'References available upon request  |  Last Updated: August 2026', 0, 1, 'C')

# Save
output_path = r"C:\Users\Admin\My Drive\LifeWorkspace\01_Identities_&_Assets\CV_Kamel_Mahi_Professional.pdf"
pdf.output(output_path)
print(f"PDF created: {output_path}")
print(f"Size: {os.path.getsize(output_path)} bytes")
