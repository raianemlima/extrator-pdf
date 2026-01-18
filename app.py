import streamlit as st
import fitz
from fpdf import FPDF
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import date
import io
import random
import re

COR_VERDE_DUO_RGB = (166, 201, 138)

# --- INJEÇÃO DE CSS PARA IDENTIDADE VISUAL ---
st.markdown(f"""
    <style>
    .stApp {{
        background-color: #f8f9fa;
    }}
    .stButton>button {{
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: rgb{COR_VERDE_DUO_RGB};
        color: white;
        border: none;
        font-weight: bold;
        transition: 0.3s;
    }}
    .stButton>button:hover {{
        background-color: #8EAE74;
        border: none;
        color: white;
    }}
    .main-card {{
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid rgb{COR_VERDE_DUO_RGB};
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }}
    h1, h2, h3 {{
        color: #4A4A4A;
        font-family: 'Arial', sans-serif;
    }}
    </style>
""", unsafe_allow_html=True)

def limpar_texto_total(texto):
    texto = re.sub(r'([a-zA-ZáéíóúÁÉÍÓÚçÇ]{3,})(\d+)', r'\1', texto)
    texto = re.sub(r'(\.)(\d+)', r'\1', texto)
    mapa = {'\u2013': '-', '\u2014': '-', '\u201c': '"', '\u201d': '"', '\u2022': '•', '\uf0b7': '•', '? ': '- '}
    for original, substituto in mapa.items():
        texto = texto.replace(original, substituto)
    return " ".join(texto.split())

def gerar_pergunta_contextualizada(texto):
    t = texto.lower()
    if "cpi" in t: return "Como o material define a natureza da CPI e seus requisitos?"
    if "stf" in t or "stj" in t: return "Qual o entendimento dos Tribunais Superiores neste ponto?"
    return f"Explique o ponto central sobre '{texto[:30]}...' conforme o material."

st.set_page_config(page_title="Duo Study Hub", page_icon="🎓", layout="centered")

# Cabeçalho com Estilo de Banner
st.markdown(f"""
    <div style="background-color: rgb{COR_VERDE_DUO_RGB}; padding: 35px; border-radius: 20px; text-align: center; margin-bottom: 25px;">
        <h1 style="color: white; margin: 0; font-size: 2.2em; letter-spacing: 1px;">RESUMO INTELIGENTE</h1>
        <p style="color: white; margin: 5px 0 0 0; opacity: 0.9; font-weight: 500;">Cursos Duo • Excelência em Preparação</p>
    </div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📂 Arraste seu PDF aqui", type="pdf")
nome_modulo = st.text_input("📍 Identificação do Material", value="Módulo de Revisão")

if uploaded_file is not None:
    try:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        highlights = []
        for page_num, page in enumerate(doc):
            for annot in page.annots():
                if annot.type[0] == 8: 
                    highlights.append({"pag": page_num + 1, "texto": limpar_texto_total(page.get_textbox(annot.rect))})

        if highlights:
            st.info(f"✨ **{len(highlights)}** pontos estratégicos extraídos.")
            tab1, tab2, tab3 = st.tabs(["📄 Central de Downloads", "🗂️ Revisão Ativa", "🧠 Simulado C/E"])

            with tab1:
                st.markdown("### 📥 Seus Materiais estão prontos")
                # Geração de PDF (Arial 12)
                pdf = FPDF()
                pdf.add_page()
                pdf.set_fill_color(*COR_VERDE_DUO_RGB)
                pdf.rect(0, 0, 210, 45, 'F')
                pdf.set_font("Helvetica", "B", 18); pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 15, "RESUMO INTELIGENTE", ln=True, align='C')
                pdf.ln(30)
                for i, h in enumerate(highlights, 1):
                    pdf.set_font("Helvetica", "B", 11); pdf.set_text_color(*COR_VERDE_DUO_RGB)
                    pdf.cell(0, 8, f"ITEM {i:02d} | PÁG. {h['pag']}", ln=True)
                    pdf.set_font("Helvetica", size=12); pdf.set_text_color(0, 0, 0)
                    pdf.multi_cell(190, 7, h['texto'].encode('latin-1', 'replace').decode('latin-1'), align='J')
                    pdf.ln(4)

                word_doc = Document()
                h_w = word_doc.add_heading(level=0)
                r_h = h_w.add_run("RESUMO INTELIGENTE"); r_h.font.color.rgb = RGBColor(166, 201, 138)
                for h in highlights:
                    p = word_doc.add_paragraph(); rtx = p.add_run(h['texto']); rtx.font.name = 'Arial'; rtx.font.size = Pt(12)

                col1, col2 = st.columns(2)
                with col1: st.download_button("📥 Baixar PDF", bytes(pdf.output()), "Resumo_Duo.pdf")
                with col2:
                    buf = io.BytesIO(); word_doc.save(buf); st.download_button("📥 Baixar Word", buf.getvalue(), "Resumo_Duo.docx")

            with tab2:
                st.markdown("### 🗂️ Cards de Estudo")
                for i, h in enumerate(highlights):
                    st.markdown(f"""
                        <div class="main-card">
                            <span style="color: #A6C98A; font-weight: bold;">CARTÃO {i+1:02d} (Pág. {h['pag']})</span><br>
                            <b>Pergunta:</b> {gerar_pergunta_contextualizada(h['texto'])}<br><br>
                            <i>Clique abaixo para ver a resposta</i>
                        </div>
                    """, unsafe_allow_html=True)
                    with st.expander("Ver Resposta do Material"):
                        st.write(h['texto'])

            with tab3:
                st.markdown("### 🧠 Desafio Certo ou Errado")
                ponto = random.choice(highlights)
                st.info(f"**Analise o item:** {ponto['texto']}")
                resp = st.radio("Sua avaliação:", ["Selecione", "Certo", "Errado"], key="simulado")
                if resp != "Selecione":
                    if resp == "Certo": st.success("✅ Parabéns! Item em conformidade com o material.")
                    else: st.error("❌ Atenção! O item está correto segundo o texto original.")

        st.markdown(f"<br><hr><p style='text-align: center; color: #888;'>Suporte Cursos Duo: sugestoes@cursosduo.com.br</p>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Erro: {e}")
