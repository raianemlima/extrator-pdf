import streamlit as st
import fitz  # PyMuPDF
from fpdf import FPDF
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import date
import io
import random

# Cor verde oficial da identidade visual Cursos Duo
COR_VERDE_DUO_RGB = (166, 201, 138) 

def limpar_texto_total(texto):
    """Mapeia símbolos complexos para evitar o erro '?' e falhas de espaço horizontal"""
    mapa_sinais = {
        '\u2013': '-', '\u2014': '-', '\u201c': '"', '\u201d': '"',
        '\u2018': "'", '\u2019': "'", '\u2022': '•', '\uf0b7': '•',
        '\uf02d': '-', '\uf0d8': '>', '\u2026': '...', '\u00a0': ' ',
        '\u2010': '-', '\u2011': '-', '\u00ba': 'º', '\u00aa': 'ª',
        '? ': '- ', ' :': ':'
    }
    for original, substituto in mapa_sinais.items():
        texto = texto.replace(original, substituto)
    return " ".join(texto.split())

st.set_page_config(page_title="Resumo Inteligente - Duo", page_icon="🎓")

# --- CABEÇALHO VISUAL CURSOS DUO ---
st.markdown(f"""
    <div style="background-color: rgb{COR_VERDE_DUO_RGB}; padding: 25px; border-radius: 12px; text-align: center; border: 1px solid #d1e7dd;">
        <h1 style="color: white; margin: 0; font-family: Arial, sans-serif; letter-spacing: 2px; font-size: 2.2em;">RESUMO INTELIGENTE</h1>
        <p style="color: white; margin: 5px 0 0 0; font-family: Arial, sans-serif; font-size: 1.4em; font-weight: bold; opacity: 0.9;">Cursos Duo</p>
    </div>
    <br>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Suba o material em PDF", type="pdf")
nome_modulo = st.text_input("Identificação do Material", placeholder="Ex: Criminologia - Teoria Labelling Approach")

if uploaded_file is not None:
    try:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        highlights = []
        for page_num, page in enumerate(doc):
            for annot in page.annots():
                if annot.type[0] == 8: 
                    text = page.get_textbox(annot.rect)
                    if text.strip():
                        highlights.append({"pag": page_num + 1, "texto": limpar_texto_total(text)})

        if highlights:
            st.success(f"Análise concluída: {len(highlights)} pontos de estudo ativos.")
            tab1, tab2, tab3 = st.tabs(["📄 Downloads do Resumo", "🗂️ Flashcards e P&R", "🧠 Quiz Dinâmico"])

            # --- TAB 1: DOWNLOADS ---
            with tab1:
                # PDF
                pdf = FPDF()
                pdf.add_page()
                pdf.set_fill_color(*COR_VERDE_DUO_RGB)
                pdf.rect(0, 0, 210, 45, 'F')
                pdf.set_font("Helvetica", "B", 18)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 15, "RESUMO INTELIGENTE", ln=True, align='C')
                pdf.set_font("Helvetica", "B", 14)
                pdf.cell(0, 10, "Cursos Duo", ln=True, align='C')
                pdf.ln(25)
                pdf.set_font("Helvetica", size=10)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 5, f"Material: {nome_modulo} | Gerado em: {date.today().strftime('%d/%m/%Y')}", ln=True, align='R')
                pdf.ln(5)

                for i, h in enumerate(highlights, 1):
                    pdf.set_font("Helvetica", "B", 11)
                    pdf.set_text_color(*COR_VERDE_DUO_RGB)
                    pdf.cell(0, 8, f"ITEM {i:02d} | PÁGINA {h['pag']}", ln=True)
                    pdf.set_font("Helvetica", size=12) 
                    pdf.set_text_color(0, 0, 0)
                    txt_pdf = h['texto'].encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 7, txt_pdf, align='J')
                    pdf.ln(4)
                
                # WORD COM TÍTULO VERDE
                word_doc = Document()
                h_word = word_doc.add_heading(level=0)
                r_h = h_word.add_run("RESUMO INTELIGENTE")
                r_h.font.color.rgb = RGBColor(166, 201, 138)
                p_sub = word_doc.add_paragraph()
                r_sub = p_sub.add_run("Cursos Duo")
                r_sub.bold = True
                word_doc.add_paragraph(f"Material: {nome_modulo} | Data: {date.today().strftime('%d/%m/%Y')}")

                for i, h in enumerate(highlights, 1):
                    p = word_doc.add_paragraph()
                    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    rt = p.add_run(f"ITEM {i:02d} | PÁGINA {h['pag']}\n")
                    rt.bold = True
                    rt.font.color.rgb = RGBColor(166, 201, 138)
                    rtx = p.add_run(h['texto'])
                    rtx.font.name = 'Arial'
                    rtx.font.size = Pt(12)

                c1, c2 = st.columns(2)
                with c1: st.download_button("📥 Baixar em PDF", bytes(pdf.output()), "Resumo_Duo.pdf")
                with c2:
                    buf = io.BytesIO()
                    word_doc.save(buf)
                    st.download_button("📥 Baixar em Word", buf.getvalue(), "Resumo_Duo.docx")

            # --- TAB 2: FLASHCARDS E P&R ---
            with tab2:
                st.subheader("Estudo Ativo: Flashcards e P&R Inteligentes")
                
                # Roteiro P&R Avançado (Correção de Espaço)
                pr_pdf = FPDF()
                pr_pdf.set_auto_page_break(auto=True, margin=15)
                pr_pdf.add_page()
                pr_pdf.set_font("Helvetica", "B", 16)
                pr_pdf.cell(0, 10, "ROTEIRO P&R - CURSOS DUO", ln=True, align='C')
                
                for i, h in enumerate(highlights, 1):
                    pr_pdf.ln(5)
                    pr_pdf.set_x(10) # Garante o início na margem esquerda
                    pr_pdf.set_font("Helvetica", "B", 11)
                    pr_pdf.set_text_color(*COR_VERDE_DUO_RGB)
                    pr_pdf.cell(0, 8, f"PERGUNTA {i:02d} (Pág. {h['pag']}):", ln=True)
                    
                    pr_pdf.set_font("Helvetica", "I", 11)
                    pr_pdf.set_text_color(50, 50, 50)
                    pr_pdf.multi_cell(190, 7, "Qual a tese central ou conceito explorado neste trecho do material?", align='L')
                    
                    pr_pdf.set_font("Helvetica", "B", 11)
                    pr_pdf.set_text_color(*COR_VERDE_DUO_RGB)
                    pr_pdf.cell(0, 8, "RESPOSTA:", ln=True)
                    
                    pr_pdf.set_font("Helvetica", size=12)
                    pr_pdf.set_text_color(0, 0, 0)
                    txt_pr = h['texto'].encode('latin-1', 'replace').decode('latin-1')
                    pr_pdf.multi_cell(190, 7, txt_pr, align='J')
                    pr_pdf.ln(4)
                    pr_pdf.line(10, pr_pdf.get_y(), 200, pr_pdf.get_y())

                # Flashcards Estilo Grade (Recortáveis)
                f_pdf = FPDF()
                f_pdf.set_auto_page_break(auto=True, margin=10)
                f_pdf.add_page()
                
                for i, h in enumerate(highlights, 1):
                    # Cabeçalho do Flashcard
                    f_pdf.set_fill_color(*COR_VERDE_DUO_RGB)
                    f_pdf.set_text_color(255, 255, 255)
                    f_pdf.set_font("Helvetica", "B", 10)
                    f_pdf.cell(190, 8, f" FLASHCARD {i:02d} | ORIGEM: PÁGINA {h['pag']}", border=1, ln=True, fill=True)
                    
                    # Conteúdo do Flashcard
                    f_pdf.set_text_color(0, 0, 0)
                    f_pdf.set_font("Helvetica", size=11)
                    txt_f = h['texto'].encode('latin-1', 'replace').decode('latin-1')
                    f_pdf.multi_cell(190, 8, txt_f, border=1, align='J')
                    f_pdf.ln(5) # Espaço entre os cartões

                col_a, col_b = st.columns(2)
                with col_a: st.download_button("📝 Baixar Roteiro P&R", bytes(pr_pdf.output()), "Roteiro_PR_Duo.pdf")
                with col_b: st.download_button("✂️ Baixar Flashcards", bytes(f_pdf.output()), "Flashcards_Duo.pdf")

            with tab3:
                st.subheader("🧠 Quiz de Recuperação")
                amostra = random.sample(highlights, min(len(highlights), 3))
                for idx, item in enumerate(amostra):
                    palavras = item['texto'].split()
                    if len(palavras) > 5:
                        secreta = max(palavras, key=len).strip(".,;:()")
                        st.write(f"**Questão {idx+1}:** {item['texto'].replace(secreta, '__________')}")
                        resp = st.text_input(f"Complete (Pág {item['pag']}):", key=f"qz_{idx}")
                        if st.button(f"Checar {idx+1}"):
                            if resp.lower().strip() == secreta.lower().strip(): st.success(f"Correto! Palavra: {secreta}")
                            else: st.warning(f"A resposta era: {secreta}")

        st.markdown(f"<hr><p style='text-align: center; color: gray;'>Dúvidas: sugestoes@cursosduo.com.br</p>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Ocorreu um erro inesperado: {e}")
