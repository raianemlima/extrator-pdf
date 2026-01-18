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

# Identidade Visual Cursos Duo
COR_VERDE_DUO_RGB = (166, 201, 138) 

def limpar_texto_total(texto):
    """Garante extração fiel de símbolos e remove números de rodapé colados"""
    # Remove números de rodapé (ex: Federal5 -> Federal) sem quebrar Art. 5
    texto = re.sub(r'([a-zA-ZáéíóúÁÉÍÓÚçÇ]{3,})(\d+)', r'\1', texto)
    texto = re.sub(r'(\.)(\d+)', r'\1', texto)
    
    # Mapeamento para símbolos compatíveis e extração de %$()_*
    mapa_sinais = {
        '\u2013': '-', '\u2014': '-', '\u201c': '"', '\u201d': '"',
        '\u2018': "'", '\u2019': "'", '\u2022': '•', '\uf0b7': '•',
        '\uf02d': '-', '\uf0d8': '>', '\u2026': '...', '\u00a0': ' ',
        '? ': '- ' # Correção para marcadores de lista
    }
    for original, substituto in mapa_sinais.items():
        texto = texto.replace(original, substituto)
    return " ".join(texto.split())

def gerar_pergunta_contextualizada(texto):
    """Gera perguntas diretas baseadas no conteúdo real do destaque"""
    t = texto.lower()
    if "cpi" in t: return "Como o texto define a natureza da CPI e seus requisitos de criação?"
    if "parlamentar" in t: return "O que o material explica sobre imunidades e o marco da diplomação?"
    if "stf" in t or "stj" in t: return "Qual o entendimento atualizado dos Tribunais sobre este ponto?"
    if "labelling" in t: return "Discorra sobre a Teoria do Etiquetamento e as propostas citadas."
    
    # Fallback contextual
    tema = " ".join(texto.split()[:5]).strip(".,;:- ")
    return f"Explique o ponto central sobre '{tema}' conforme abordado no material."

# Configuração Responsiva para Celular/Tablet
st.set_page_config(page_title="Resumo Inteligente - Duo", page_icon="🎓", layout="centered")

# CSS para interface Profissional
st.markdown(f"""
    <style>
    .stApp {{ background-color: #fcfcfc; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: #f1f1f1; border-radius: 5px; padding: 10px;
    }}
    .stTabs [aria-selected="true"] {{ background-color: rgb{COR_VERDE_DUO_RGB} !important; color: white !important; }}
    </style>
""", unsafe_allow_html=True)

# Banner de Identidade Visual
st.markdown(f"""
    <div style="background-color: rgb{COR_VERDE_DUO_RGB}; padding: 30px; border-radius: 15px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
        <h1 style="color: white; margin: 0; font-family: sans-serif; letter-spacing: 2px; font-size: 2em;">RESUMO INTELIGENTE</h1>
        <p style="color: white; margin: 5px 0 0 0; font-weight: bold; font-size: 1.2em;">Cursos Duo</p>
    </div>
    <br>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📂 Suba o PDF do curso", type="pdf")
nome_modulo = st.text_input("📍 Nome do Módulo", value="Material de Revisão")

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
            st.success(f"**{len(highlights)}** pontos estratégicos processados.")
            tab1, tab2, tab3 = st.tabs(["📄 Downloads", "🗂️ Flashcards & P&R", "🧠 Simulado C/E"])

            with tab1:
                # Gerador PDF (Arial 12)
                pdf = FPDF()
                pdf.add_page()
                pdf.set_fill_color(*COR_VERDE_DUO_RGB)
                pdf.rect(0, 0, 210, 45, 'F')
                pdf.set_font("Helvetica", "B", 18); pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 15, "RESUMO INTELIGENTE", ln=True, align='C')
                pdf.set_font("Helvetica", "B", 14); pdf.cell(0, 10, "Cursos Duo", ln=True, align='C')
                pdf.ln(30); pdf.set_text_color(0,0,0)
                
                for i, h in enumerate(highlights, 1):
                    pdf.set_font("Helvetica", "B", 11); pdf.set_text_color(*COR_VERDE_DUO_RGB)
                    pdf.cell(0, 8, f"ITEM {i:02d} | PÁGINA {h['pag']}", ln=True)
                    pdf.set_font("Helvetica", size=12); pdf.set_text_color(0, 0, 0)
                    txt = h['texto'].encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(190, 7, txt, align='J')
                    pdf.ln(4)

                # Gerador Word (Título Verde + Arial 12)
                word_doc = Document()
                h_w = word_doc.add_heading(level=0)
                r_h = h_w.add_run("RESUMO INTELIGENTE"); r_h.font.color.rgb = RGBColor(166, 201, 138)
                word_doc.add_paragraph("Cursos Duo").bold = True
                for i, h in enumerate(highlights, 1):
                    p = word_doc.add_paragraph()
                    rt = p.add_run(f"ITEM {i:02d} | PÁGINA {h['pag']}\n"); rt.bold = True; rt.font.color.rgb = RGBColor(166, 201, 138)
                    rtx = p.add_run(h['texto']); rtx.font.name = 'Arial'; rtx.font.size = Pt(12); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

                c1, c2 = st.columns(2)
                with c1: st.download_button("📥 Baixar PDF", bytes(pdf.output()), "Resumo_Duo.pdf")
                with c2:
                    buf = io.BytesIO(); word_doc.save(buf)
                    st.download_button("📥 Baixar Word", buf.getvalue(), "Resumo_Duo.docx")

            with tab2:
                # Roteiro P&R Adaptado
                pr_pdf = FPDF()
                pr_pdf.set_auto_page_break(auto=True, margin=15)
                pr_pdf.add_page()
                for i, h in enumerate(highlights, 1):
                    pr_pdf.set_fill_color(248, 252, 248)
                    pr_pdf.set_font("Helvetica", "B", 10); pr_pdf.set_text_color(60, 90, 60)
                    pr_pdf.cell(190, 8, f"  QUESTÃO {i:02d} (Pág. {h['pag']})", ln=True, fill=True, border='B')
                    pr_pdf.set_font("Helvetica", "B", 10); pr_pdf.set_text_color(0, 0, 0)
                    pr_pdf.multi_cell(190, 6, f"PERGUNTA: {gerar_pergunta_contextualizada(h['texto'])}", align='L')
                    pr_pdf.set_font("Helvetica", size=10); txt_pr = h['texto'].encode('latin-1', 'replace').decode('latin-1')
                    pr_pdf.set_draw_color(*COR_VERDE_DUO_RGB)
                    pr_pdf.multi_cell(190, 5, f"RESPOSTA: {txt_pr}", align='J', border='L')
                    pr_pdf.ln(5)

                # Flashcards para Recorte (Grade)
                f_pdf = FPDF()
                f_pdf.add_page()
                for i, h in enumerate(highlights, 1):
                    f_pdf.set_fill_color(*COR_VERDE_DUO_RGB); f_pdf.set_text_color(255, 255, 255)
                    f_pdf.set_font("Helvetica", "B", 10)
                    f_pdf.cell(190, 8, f" FLASHCARD {i:02d} | PÁGINA {h['pag']}", border=1, ln=True, fill=True)
                    f_pdf.set_text_color(0, 0, 0); f_pdf.set_font("Helvetica", size=11)
                    txt_f = h['texto'].encode('latin-1', 'replace').decode('latin-1')
                    f_pdf.multi_cell(190, 8, txt_f, border=1, align='J')
                    f_pdf.ln(6)

                st.download_button("📝 Baixar Roteiro P&R", bytes(pr_pdf.output()), "Roteiro_PR_Duo.pdf")
                st.download_button("✂️ Baixar Flashcards (Recorte)", bytes(f_pdf.output()), "Flashcards_Duo.pdf")

            with tab3:
                st.subheader("🧠 Simulado Certo ou Errado")
                ponto = random.choice(highlights)
                st.info(f"**Item de Prova:** {ponto['texto']}")
                escolha = st.radio("Sua avaliação:", ["Selecione", "Certo", "Errado"], key="simu")
                if escolha != "Selecione":
                    if escolha == "Certo": st.success("✅ Correto! O item reflete o material original.")
                    else: st.error("❌ Incorreto. A afirmação está de acordo com o texto estudado.")

        st.markdown(f"<hr><p style='text-align: center; color: gray;'>Dúvidas: sugestoes@cursosduo.com.br</p>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Erro: {e}")
