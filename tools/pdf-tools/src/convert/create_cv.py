"""
Generate professional CV
"""
from fpdf import FPDF


class CVDocument(FPDF):
    def header(self):
        pass
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')
    
    def section_title(self, title):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(0, 80, 160)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(0, 80, 160)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(4)
        self.set_text_color(0)
    
    def entry(self, title, subtitle, date_range, description=""):
        self.set_font('Helvetica', 'B', 10)
        self.cell(0, 6, title, new_x="LMARGIN", new_y="NEXT")
        if subtitle:
            self.set_font('Helvetica', 'I', 10)
            self.cell(0, 5, subtitle, new_x="LMARGIN", new_y="NEXT")
        if date_range:
            self.set_font('Helvetica', '', 9)
            self.set_text_color(100)
            self.cell(0, 5, date_range, new_x="LMARGIN", new_y="NEXT")
            self.set_text_color(0)
        if description:
            self.set_font('Helvetica', '', 10)
            self.multi_cell(0, 5, description, new_x="LMARGIN", new_y="NEXT")
        self.ln(3)


def create_cv(output_path):
    pdf = CVDocument()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.set_left_margin(20)
    pdf.set_right_margin(20)
    
    # Header - Name
    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(0, 80, 160)
    pdf.cell(0, 10, "Mahi Kamel Abdelghani", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.set_text_color(0)
    
    # Contact info
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 5, "El Bayadh, Algérie | Tél: 0555081718 | Email: kamelmahi71@gmail.com", 
             new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(6)
    
    # Section: Personal Info
    pdf.section_title("INFORMATIONS PERSONNELLES")
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 5, "Né le 06/03/1996 à El Bayadh", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, "Registre: 20091691373 | Matricule: 151538064886", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    
    # Section: Education
    pdf.section_title("FORMATION")
    
    pdf.entry(
        "Licence en Langue Anglaise",
        "Université de Saida - Tahar Moulay",
        "2015 - 2020",
        "Diplôme obtenu avec mention. Spécialisation en linguistique, littérature et traduction."
    )
    
    pdf.entry(
        "Baccalauréat en Lettres et Langues Étrangères",
        "Lycée El Idrissi, El Bayadh",
        "2015",
        "Option: Langues Étrangères"
    )
    
    # Section: Professional Experience
    pdf.section_title("EXPÉRIENCE PROFESSIONNELLE")
    
    pdf.entry(
        "Enseignant d'Anglais",
        "Centre de Langues, El Bayadh",
        "2020 - Présent",
        "Enseignement de l'anglais général et professionnel. Préparation des examens."
    )
    
    pdf.entry(
        "Formateur en Informatique de Gestion",
        "Institut de Formation, El Bayadh",
        "2018 - 2020",
        "Formation en bureautique, VBA, et systèmes d'information de gestion."
    )
    
    # Section: Skills
    pdf.section_title("COMPÉTENCES")
    
    pdf.set_font('Helvetica', '', 10)
    skills = [
        "- Langues: Anglais (C1), Français (B2), Arabe (Natif)",
        "- Informatique: Python, VBA, Office (Word, Excel, PowerPoint)",
        "- Pédagogie: Didactique des langues, pédagogie active",
        "- Communication: Rédaction, présentation, médiation culturelle"
    ]
    for skill in skills:
        pdf.cell(0, 5, skill, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    
    # Section: Projects
    pdf.section_title("PROJETS RÉALISÉS")
    
    pdf.entry(
        "Système d'Aide à la Décision pour la Gestion des Stocks",
        "Academix DSS v14.0",
        "2023 - Présent",
        "Application VBA/Excel pour l'optimisation des commandes et la gestion des inventaires."
    )
    
    pdf.entry(
        "Plateforme d'Enseignement de l'Anglais",
        "English Teaching Project",
        "2024 - Présent",
        "Système d'exercices interactifs et de plans de cours pour l'enseignement de l'anglais."
    )
    
    # Section: Certifications
    pdf.section_title("CERTIFICATIONS")
    
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 5, "- Certification CCA-F (Claude Certified Architect) - En cours", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, "- Formation en Développement d'Applications avec l'IA", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    
    # Section: Interests
    pdf.section_title("CENTRES D'INTÉRÊT")
    
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 5, "- Enseignement et didactique des langues", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, "- Technologies éducatives et intelligence artificielle", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, "- Littérature et culture anglophone", new_x="LMARGIN", new_y="NEXT")
    
    pdf.output(output_path)
    print(f"CV saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    output = r"C:\Users\Admin\My Drive\LifeWorkspace\16_Official\Academic\CV_Kamel_MAHI_v2.pdf"
    create_cv(output)
