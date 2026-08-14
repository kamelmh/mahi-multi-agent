"""
Generate improved motivation letter - 1 page, concise, professional
"""
from fpdf import FPDF


class MotivationLetter(FPDF):
    def header(self):
        pass
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')


def create_motivation_letter(output_path):
    pdf = MotivationLetter()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.set_left_margin(25)
    pdf.set_right_margin(25)
    
    # Sender info (right aligned)
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(0)
    sender_info = [
        "Mahi Kamel Abdelghani",
        "El Bayadh, Algérie",
        "Tél: 0676773892",
        "Email: kamelmahi71@gmail.com"
    ]
    for line in sender_info:
        pdf.cell(0, 5, line, new_x="LMARGIN", new_y="NEXT", align='R')
    pdf.ln(8)
    
    # Date (right aligned)
    pdf.cell(0, 5, "El Bayadh, le 23 juillet 2026", new_x="LMARGIN", new_y="NEXT", align='R')
    pdf.ln(8)
    
    # Recipient (left aligned, bold)
    pdf.set_font('Helvetica', 'B', 10)
    recipient_info = [
        "Monsieur le Directeur du Département d'Anglais",
        "Centre Universitaire Nour Bachir",
        "El Bayadh, Algérie"
    ]
    for line in recipient_info:
        pdf.cell(0, 5, line, new_x="LMARGIN", new_y="NEXT", align='L')
    pdf.ln(8)
    
    # Subject (bold)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 6, "Objet : Candidature pour le Master 1 en Langue Anglaise", new_x="LMARGIN", new_y="NEXT", align='L')
    pdf.ln(6)
    
    # Body (concise, 3 short paragraphs)
    pdf.set_font('Helvetica', '', 11)
    
    para1 = (
        "Je me permets de vous soumettre ma candidature pour intégrer le Master 1 en Langue Anglaise "
        "au Centre Universitaire Nour Bachir pour l'année universitaire 2026-2027, dans le cadre du "
        "20% des étudiants externes."
    )
    pdf.multi_cell(0, 6, para1, new_x="LMARGIN", new_y="NEXT", align='J')
    pdf.ln(4)
    
    para2 = (
        "Titulaire d'une Licence en Langue Anglaise obtenue à l'Université de Saida (2015-2020), "
        "j'ai développé un vif intérêt pour la linguistique, la littérature et la traduction. "
        "Mon parcours académique m'a permis d'acquérir des bases solides en analyse textuelle "
        "et en compréhension des mécanismes langagiers."
    )
    pdf.multi_cell(0, 6, para2, new_x="LMARGIN", new_y="NEXT", align='J')
    pdf.ln(4)
    
    para3 = (
        "Ce Master constitue pour moi l'opportunité d'approfondir mes connaissances en linguistique "
        "anglaise et de développer une réflexion plus analytique sur les phénomènes langagiers. "
        "Je souhaite particulièrement m'initier à la recherche scientifique et acquérir les méthodologies "
        "nécessaires pour mener des travaux rigoureux dans ce domaine."
    )
    pdf.multi_cell(0, 6, para3, new_x="LMARGIN", new_y="NEXT", align='J')
    pdf.ln(4)
    
    para4 = (
        "Je me tiens à votre disposition pour tout entretien ou complément d'information que vous "
        "jugerez nécessaire."
    )
    pdf.multi_cell(0, 6, para4, new_x="LMARGIN", new_y="NEXT", align='J')
    pdf.ln(6)
    
    # Closing
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 6, "Veuillez agréer, Monsieur le Directeur, l'expression de mes salutations distinguées.", 
             new_x="LMARGIN", new_y="NEXT", align='L')
    pdf.ln(12)
    
    # Signature (right aligned)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 6, "Mahi Kamel Abdelghani", new_x="LMARGIN", new_y="NEXT", align='R')
    
    pdf.output(output_path)
    print(f"Motivation letter saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    output = r"C:\Users\Admin\My Drive\LifeWorkspace\16_Official\Academic\رسالة تحفيزية - ماجستير اللغة الإنجليزية_v2.pdf"
    create_motivation_letter(output)
