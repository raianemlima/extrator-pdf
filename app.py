import streamlit as st
import fitz  # PyMuPDF
from fpdf import FPDF
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import date, datetime
import io
import random
import re
from typing import List, Dict, Tuple
from collections import Counter

# Constantes - Identidade Visual Cursos Duo
COR_VERDE_DUO_RGB = (166, 201, 138)
COR_VERDE_DUO_HEX = "#A6C98A"
COR_VERDE_ESCURO = "#7A9B6E"
COR_TEXTO_ESCURO = "#2C3E50"

# Configuração da página
st.set_page_config(
    page_title="Resumo Inteligente - Duo",
    page_icon="🎓",
    layout="centered"
)

# --- CSS CUSTOMIZADO (RESPONSIVO E PROFISSIONAL) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; color: {COR_TEXTO_ESCURO}; }}
    .card-duo {{
        background: white; padding: 1.5rem; border-radius: 12px;
        border-left: 5px solid {COR_VERDE_DUO_HEX};
        box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin: 1rem 0;
    }}
    .stDownloadButton > button {{
        background: linear-gradient(135deg, {COR_VERDE_DUO_HEX} 0%, {COR_VERDE_ESCURO} 100%);
        color: white; border: none; width: 100%; border-radius: 8px; font-weight: 600;
    }}
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE LIMPEZA E ANÁLISE JURÍDICA ---

def limpar_texto_total(texto: str) -> str:
    """Extração fiel de %$()_* e remoção de rodapés."""
    if not texto: return ""
    texto = re.sub(r'([a-zA-ZáéíóúÁÉÍÓÚçÇ]{3,})(\d+)', r'\1', texto)
    texto = re.sub(r'(\.)(\d+)', r'\1', texto)
    mapa = {'\u2013': '-', '\u2014': '-', '\u2022': '•', '\uf0b7': '•', '? ': '- '}
    for original, substituto in mapa.items():
        texto = texto.replace(original, substituto)
    return " ".join(texto.split())

def gerar_pergunta_contextualizada(texto: str) -> str:
    """Gera enunciados técnicos para evitar perguntas curtas."""
    t = texto.lower()
    if "cpi" in t: return "Acerca das Comissões Parlamentares de Inquérito, analise os requisitos constitucionais de criação."
    if "stf" in t or "stj" in t: return "Considerando a jurisprudência atualizada dos Tribunais Superiores, julgue o item a seguir."
    if "parlamentar" in t: return "Sobre o estatuto dos congressistas e suas garantias, analise a afirmação baseada no material."
    return f"Considerando os aspectos jurídicos de '{' '.join(texto.split()[:5])}', julgue se o item está correto."

# --- GERAÇÃO DE DOCUMENTOS (CORREÇÃO DO ERRO DE DOWNLOAD) ---

def criar_pdf_resumo(highlights: List[Dict], nome: str) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(*COR_VERDE_DUO_RGB)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_font("Helvetica", "B", 16); pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 15, "RESUMO INTELIGENTE - DUO", ln=True, align='C')
    pdf.ln(25)
    for h in highlights:
        pdf.set_font("Helvetica", "B", 11); pdf.set_text_color(*COR_VERDE_DUO_RGB)
        pdf.cell(0, 8, f"PÁGINA {h['pag']}", ln=True)
        pdf.set_font("Helvetica", size=12); pdf.set_text_color(0, 0, 0)
        txt = h['texto'].encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(190, 7, txt, align='J')
        pdf.ln(4)
    return bytes(pdf.output())

def criar_word_resumo(highlights: List[Dict]) -> bytes:
    doc = Document()
    titulo = doc.add_heading("RESUMO INTELIGENTE", 0)
    for h in highlights:
        p = doc.add_paragraph()
        run = p.add_run(f"PÁGINA {h['pag']}\n"); run.bold = True; run.font.color.rgb = RGBColor(*COR_VERDE_DUO_RGB)
        rtx = p.add_run(h['texto']); rtx.font.name = 'Arial'; rtx.font.size = Pt(12); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

# --- INTERFACE PRINCIPAL ---

def main():
    st.markdown(f"""<div style="background: linear-gradient(135deg, {COR_VERDE_DUO_HEX} 0%, {COR_VERDE_ESCURO} 100%); padding: 2rem; border-radius: 15px; text-align: center; color: white; margin-bottom: 2rem;">
        <h1 style="margin:0;">RESUMO INTELIGENTE</h1><p style="font-weight:600;">Cursos Duo</p></div>""", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Suba o material do Cursos Duo (PDF)", type="pdf")
    nome_modulo = st.text_input("Identificação do Material", value="Revisão Ponto 6")

    if uploaded_file:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        highlights = []
        texto_completo = ""
        for page_num, page in enumerate(doc):
            texto_completo += page.get_text() + " "
            for annot in page.annots():
                if annot.type[0] == 8:
                    txt = limpar_texto_total(page.get_textbox(annot.rect))
                    if txt: highlights.append({"pag": page_num + 1, "texto": txt})

        if highlights:
            st.success(f"✅ {len(highlights)} pontos identificados.")
            tab1, tab2, tab3 = st.tabs(["📄 Resumo", "🗂️ Revisão", "🧠 Simulado C/E"])

            with tab1:
                col1, col2 = st.columns(2)
                with col1:
                    pdf_data = criar_pdf_resumo(highlights, nome_modulo)
                    st.download_button("📥 Baixar PDF", pdf_data, "Resumo.pdf", "application/pdf")
                with col2:
                    word_data = criar_word_resumo(highlights)
                    st.download_button("📥 Baixar Word", word_data, "Resumo.docx")

            with tab2:
                for h in highlights[:10]:
                    with st.expander(f"Pág. {h['pag']} - Ver Questão"):
                        st.write(f"**Pergunta:** {gerar_pergunta_contextualizada(h['texto'])}")
                        st.write(f"**Resposta:** {h['texto']}")

            with tab3:
                st.subheader("🧠 Simulado Certo ou Errado")
                # CORREÇÃO DO QUIZ: Reconstrução de frases longas para evitar perguntas curtas
                texto_limpo = texto_completo.replace('\n', ' ')
                frases = [f.strip() for f in re.split(r'(?<=[.!?])\s+', texto_limpo) if len(f.strip()) > 150]
                
                if frases:
                    if 'questoes' not in st.session_state or st.button("🔄 Gerar Novas Questões"):
                        selecionados = random.sample(frases, min(len(frases), 5))
                        st.session_state.questoes = [{"p": gerar_pergunta_contextualizada(f), "t": f} for f in selecionados]
                    
                    for idx, q in enumerate(st.session_state.questoes):
                        st.markdown(f"""<div class="card-duo"><b>QUESTÃO {idx+1}</b><br><small>{q['p']}</small><br><br><i>"...{q['t']}..."</i></div>""", unsafe_allow_html=True)
                        resp = st.radio("Julgamento:", ["Selecione", "Certo", "Errado"], key=f"q_{idx}", horizontal=True)
                        if resp != "Selecione":
                            if resp == "Certo": st.success("✅ Correto conforme o material!")
                            else: st.error("❌ Errado. De acordo com o texto, a afirmação está correta.")
                else:
                    st.warning("Conteúdo insuficiente para gerar o simulado.")

    st.markdown("<hr><p style='text-align: center; color: gray;'>Dúvidas: sugestoes@cursosduo.com.br</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
