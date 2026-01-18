import streamlit as st
import fitz  # PyMuPDF
from fpdf import FPDF
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import date
import io
import random
import re

# Cor verde oficial da identidade visual Cursos Duo
COR_VERDE_DUO_RGB = (166, 201, 138) 

def gerar_pergunta_inteligente(texto):
    """Gera enunciados específicos baseados em temas jurídicos recorrentes"""
    t = texto.lower()
    if "cpi" in t or "parlamentar de inquérito" in t:
        return "Discorra sobre a natureza da CPI como direito das minorias e analise os requisitos constitucionais para sua criação."
    if "parlamentar" in t or "deputado" in t or "senador" in t:
        return "Explique o regime das imunidades parlamentares e o marco temporal para o início das garantias, segundo o STF."
    if "labelling" in t or "etiquetamento" in t:
        return "No âmbito da Criminologia, analise a Teoria do Etiquetamento e as propostas político-criminais decorrentes."
    if "improbidade" in t or "lia" in t:
        return "Acerca da LIA, discorra sobre a exigência de dolo e a vedação do controle de políticas públicas após 2021."
    if "stf" in t or "stj" in t:
        return "Analise a jurisprudência atualizada dos Tribunais Superiores sobre o tema, destacando teses fixadas."
    
    palavras = texto.split()[:5]
    tema = " ".join(palavras).strip(".,;:- ")
    return f"Apresente a natureza jurídica, os principais requisitos e as consequências de: {tema}."

def limpar_texto_total(texto):
    """Remove referências numéricas de rodapé (ex: Federal5) e corrige símbolos"""
    # Remove números de rodapé colados (Federal5 -> Federal)
    texto = re.sub(r'([a-zA-ZáéíóúÁÉÍÓÚçÇ]{3,})(\d+)', r'\1', texto)
    texto = re.sub(r'(\.)(\d+)', r'\1', texto)
    
    mapa_sinais = {
        '\u2013': '-', '\u2014': '-', '\u201c': '"', '\u201d': '"',
        '\u2022': '•', '\uf0b7': '•', '\uf02d': '-', '\u2026': '...',
        '? ': '- ' 
    }
    for original, substituto in mapa_sinais.items():
        texto = texto.replace(original, substituto)
    return " ".join(texto.split())

st.set_page_config(page_title="Resumo Inteligente - Duo", page_icon="🎓")

# --- CABEÇALHO VISUAL ---
st.markdown(f"""
    <div style="background-color: rgb{COR_VERDE_DUO_RGB}; padding: 30px; border-radius: 12px; text-align: center;">
        <h1 style="color: white; margin: 0; font-family: Arial, sans-serif; letter-spacing: 2px;">RESUMO INTELIGENTE</h1>
        <p style="color: white; margin: 5px 0 0 0; font-weight: bold; font-size: 1.2em;">Cursos Duo</p>
    </div>
    <br>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Suba o material do curso (PDF)", type="pdf")
nome_modulo = st.text_input("Identificação do Módulo", value="Revisão Cursos Duo")

if uploaded_file is not None:
    try:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        highlights = []
        for page_num, page in enumerate(doc):
            for annot in page.annots():
                if annot.type[0] == 8: 
                    highlights.append({
                        "pag": page_num + 1, 
                        "texto": limpar_texto_total(page.get_textbox(annot.rect))
                    })

        if highlights:
            st.success(f"{len(highlights)} pontos de estudo identificados.")
            tab1, tab2, tab3 = st.tabs(["📄 Downloads do Resumo", "🗂️ Flashcards & P&R", "🧠 Simulado"])

            # --- TAB 1: DOWNLOADS RESTAURADA ---
            with tab1:
                # Gerador PDF
                pdf = FPDF()
                pdf.add_page()
                pdf.set_fill_color(*COR_VERDE_DUO_RGB)
                pdf.rect(0, 0, 210, 45, 'F')
                pdf.set_font("Helvetica", "B", 18); pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 15, "RESUMO INTELIGENTE", ln=True, align='C')
                pdf.set_font("Helvetica", "B", 14); pdf.cell(0, 10, "Cursos Duo", ln=True, align='C')
                pdf.ln(25); pdf.set_font("Helvetica", size=10); pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 5, f"Material: {nome_modulo} | Gerado em: {date.today().strftime('%d/%m/%Y')}", ln=True, align='R')
                pdf.ln(5)

                for i, h in enumerate(highlights, 1):
                    pdf.set_font("Helvetica", "B", 11); pdf.set_text_color(*COR_VERDE_DUO_RGB)
                    pdf.cell(0, 8, f"ITEM {i:02d} | PÁGINA {h['pag']}", ln=True)
                    pdf.set_font("Helvetica", size=12); pdf.set_text_color(0, 0, 0)
                    txt_pdf = h['texto'].encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 7, txt_pdf, align='J')
                    pdf.ln(4)
                
                # Gerador Word com Título Verde
                word_doc = Document()
                h_word = word_doc.add_heading(level=0)
                r_h = h_word.add_run("RESUMO INTELIGENTE")
                r_h.font.color.rgb = RGBColor(166, 201, 138)
                word_doc.add_paragraph("Cursos Duo").bold = True
                word_doc.add_paragraph(f"Material: {nome_modulo} | Data: {date.today().strftime('%d/%m/%Y')}")

                for i, h in enumerate(highlights, 1):
                    p = word_doc.add_paragraph()
                    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    run_t = p.add_run(f"ITEM {i:02d} | PÁGINA {h['pag']}\n")
                    run_t.bold = True
                    run_t.font.color.rgb = RGBColor(166, 201, 138)
                    run_text = p.add_run(h['texto'])
                    run_text.font.name = 'Arial'; run_text.font.size = Pt(12)

                c1, c2 = st.columns(2)
                nome_f = nome_modulo.replace(" ", "_")
                with c1: st.download_button("📥 Baixar em PDF", bytes(pdf.output()), f"{nome_f}.pdf")
                with c2:
                    buf = io.BytesIO(); word_doc.save(buf)
                    st.download_button("📥 Baixar em Word", buf.getvalue(), f"{nome_f}.docx")

            # --- TAB 2: FLASHCARDS E P&R INTELIGENTES ---
            with tab2:
                st.subheader("Estudo Ativo")
                pr_pdf = FPDF()
                pr_pdf.add_page()
                pr_pdf.set_font("Helvetica", "B", 16); pr_pdf.set_text_color(*COR_VERDE_DUO_RGB)
                pr_pdf.cell(0, 10, "ROTEIRO P&R - BANCA CURSOS DUO", ln=True, align='C')
                
                for i, h in enumerate(highlights, 1):
                    enunciado = gerar_pergunta_inteligente(h['texto'])
                    pr_pdf.ln(5); pr_pdf.set_fill_color(248, 252, 248)
                    pr_pdf.set_font("Helvetica", "B", 11); pr_pdf.set_text_color(60, 90, 60)
                    pr_pdf.cell(0, 10, f"  QUESTÃO {i:02d} (Pág. {h['pag']})", ln=True, fill=True)
                    pr_pdf.set_font("Helvetica", "B", 11); pr_pdf.set_text_color(0, 0, 0)
                    pr_pdf.multi_cell(0, 8, f"ENUNCIADO: {enunciado}", align='L')
                    pr_pdf.set_font("Helvetica", "B", 10); pr_pdf.set_text_color(*COR_VERDE_DUO_RGB)
                    pr_pdf.cell(0, 8, "PADRÃO DE RESPOSTA:", ln=True)
                    pr_pdf.set_font("Helvetica", size=12)
                    txt_pr = h['texto'].encode('latin-1', 'replace').decode('latin-1')
                    pr_pdf.multi_cell(0, 7, txt_pr, align='J', border='L')
                    pr_pdf.ln(5); pr_pdf.line(10, pr_pdf.get_y(), 200, pr_pdf.get_y())

                st.download_button("📝 Baixar Roteiro P&R", bytes(pr_pdf.output()), "Roteiro_PR_Duo.pdf")

            with tab3:
                st.subheader("🧠 Quiz Rápido")
                amostra = random.sample(highlights, min(len(highlights), 3))
                for idx, item in enumerate(amostra):
                    palavras = item['texto'].split()
                    if len(palavras) > 5:
                        secreta = max(palavras, key=len).strip(".,;:()")
                        st.write(f"**Questão {idx+1}:** {item['texto'].replace(secreta, '__________')}")
                        resp = st.text_input(f"Complete (Pág {item['pag']}):", key=f"qz_{idx}")
                        if st.button(f"Validar {idx+1}"):
                            if resp.lower().strip() == secreta.lower().strip(): st.success("Correto!")
                            else: st.warning(f"Resposta: {secreta}")

    except Exception as e:
        st.error(f"Erro: {e}")
