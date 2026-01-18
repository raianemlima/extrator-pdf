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

# Cor oficial Cursos Duo
COR_VERDE_DUO_RGB = (166, 201, 138) 

def tratamento_caracteres_fiel(texto):
    """Garante a extração fiel de símbolos como %$()_* e marcadores de lista"""
    # 1. Limpeza de rodapés numéricos (Ex: Federal5 -> Federal)
    texto = re.sub(r'([a-zA-ZáéíóúÁÉÍÓÚçÇ]{3,})(\d+)', r'\1', texto)
    texto = re.sub(r'(\.)(\d+)', r'\1', texto)

    # 2. Mapeamento para símbolos compatíveis com PDF (Standard Fonts)
    mapa_fiel = {
        '\u2013': '-', '\u2014': '-', '\u201c': '"', '\u201d': '"',
        '\u2018': "'", '\u2019': "'", '\u2022': '*', '\uf0b7': '*',
        '\uf02d': '-', '\uf0d8': '>', '\u2026': '...', '\u00a0': ' ',
        '–': '-', '—': '-', '“': '"', '”': '"', '‘': "'", '’': "'",
        '•': '*', '·': '*', '§': 'Paragrafo ', '©': '(c)', '®': '(r)'
    }
    for original, substituto in mapa_fiel.items():
        texto = texto.replace(original, substituto)
    
    # Mantém fielmente % $ ( ) _ * conforme solicitado
    return " ".join(texto.split())

st.set_page_config(page_title="Resumo Inteligente - Duo", page_icon="🎓")

# Cabeçalho Identidade Cursos Duo
st.markdown(f"""
    <div style="background-color: rgb{COR_VERDE_DUO_RGB}; padding: 30px; border-radius: 12px; text-align: center;">
        <h1 style="color: white; margin: 0; font-family: Arial, sans-serif; letter-spacing: 2px;">RESUMO INTELIGENTE</h1>
        <p style="color: white; margin: 5px 0 0 0; font-weight: bold;">Cursos Duo</p>
    </div>
    <br>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Suba o material do curso (PDF)", type="pdf")
nome_modulo = st.text_input("Identificação do Módulo", value="Revisão Estratégica")

if uploaded_file is not None:
    try:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        highlights = []
        for page_num, page in enumerate(doc):
            for annot in page.annots():
                if annot.type[0] == 8: 
                    content = page.get_textbox(annot.rect)
                    if content.strip():
                        highlights.append({
                            "pag": page_num + 1, 
                            "texto": tratamento_caracteres_fiel(content)
                        })

        if highlights:
            st.success(f"{len(highlights)} destaques processados com sucesso.")
            tab1, tab2 = st.tabs(["📄 Downloads do Resumo", "🧠 Estudo Ativo"])

            with tab1:
                # Geração PDF com codificação robusta
                pdf = FPDF()
                pdf.add_page()
                pdf.set_fill_color(*COR_VERDE_DUO_RGB)
                pdf.rect(0, 0, 210, 45, 'F')
                pdf.set_font("Helvetica", "B", 18); pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 15, "RESUMO INTELIGENTE", ln=True, align='C')
                pdf.ln(25); pdf.set_font("Helvetica", size=10); pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 5, f"{nome_modulo} | {date.today().strftime('%d/%m/%Y')}", ln=True, align='R')
                
                for i, h in enumerate(highlights, 1):
                    pdf.set_font("Helvetica", "B", 11); pdf.set_text_color(*COR_VERDE_DUO_RGB)
                    pdf.cell(0, 8, f"ITEM {i:02d} | PÁGINA {h['pag']}", ln=True)
                    pdf.set_font("Helvetica", size=12); pdf.set_text_color(0, 0, 0)
                    # Encode seguro: ignora o que não for latim-1 para não quebrar o PDF
                    txt_pdf = h['texto'].encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(190, 7, txt_pdf, align='J')
                    pdf.ln(4)
                
                # Word (Suporta Unicode nativamente)
                word_doc = Document()
                h_w = word_doc.add_heading(level=0)
                r_h = h_w.add_run("RESUMO INTELIGENTE"); r_h.font.color.rgb = RGBColor(166, 201, 138)
                
                for i, h in enumerate(highlights, 1):
                    p = word_doc.add_paragraph()
                    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    rt = p.add_run(f"ITEM {i:02d} | PÁGINA {h['pag']}\n"); rt.bold = True
                    rt.font.color.rgb = RGBColor(166, 201, 138)
                    rtx = p.add_run(h['texto']); rtx.font.name = 'Arial'; rtx.font.size = Pt(12)

                c1, c2 = st.columns(2)
                with c1: st.download_button("📥 Baixar PDF", bytes(pdf.output()), "Resumo_Duo.pdf")
                with c2:
                    buf = io.BytesIO(); word_doc.save(buf)
                    st.download_button("📥 Baixar Word", buf.getvalue(), "Resumo_Duo.docx")

            with tab2:
                # Estudo Ativo P&R (Sem Títulos desnecessários) 
                pr_pdf = FPDF()
                pr_pdf.set_auto_page_break(auto=True, margin=15)
                pr_pdf.add_page()
                pr_pdf.set_fill_color(*COR_VERDE_DUO_RGB)
                pr_pdf.rect(0, 0, 210, 15, 'F')
                
                for i, h in enumerate(highlights, 1):
                    pr_pdf.ln(8)
                    pr_pdf.set_fill_color(248, 252, 248)
                    pr_pdf.set_font("Helvetica", "B", 10); pr_pdf.set_text_color(60, 90, 60)
                    pr_pdf.cell(190, 8, f"  QUESTÃO {i:02d} (Pág. {h['pag']})", ln=True, fill=True, border='B')
                    
                    pr_pdf.set_font("Helvetica", size=10); pr_pdf.set_text_color(0, 0, 0)
                    txt_pr = h['texto'].encode('latin-1', 'replace').decode('latin-1')
                    pr_pdf.set_draw_color(*COR_VERDE_DUO_RGB)
                    pr_pdf.multi_cell(190, 6, txt_pr, align='J', border='L')
                    pr_pdf.ln(2)

                st.download_button("📝 Baixar Roteiro P&R", bytes(pr_pdf.output()), "Roteiro_PR_Duo.pdf")

    except Exception as e:
        st.error(f"Erro no processamento: {e}")
