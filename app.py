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
    
    # Mapeamento de temas específicos para perguntas de banca
    if "cpi" in t or "parlamentar de inquérito" in t:
        return "Discorra sobre a natureza da CPI como direito das minorias e analise os requisitos constitucionais (fato determinado e interesse público) para sua criação."
    
    if "parlamentar" in t or "deputado" in t or "senador" in t:
        return "Explique o regime das imunidades parlamentares e o marco temporal para o início das garantias e da prerrogativa de foro, segundo o STF."
    
    if "labelling" in t or "etiquetamento" in t:
        return "No âmbito da Criminologia, analise a Teoria do Etiquetamento (Labelling Approach) e as propostas político-criminais decorrentes (os '4 Ds')."
    
    if "improbidade" in t or "lia" in t:
        return "Acerca da Lei de Improbidade Administrativa, discorra sobre a exigência de dolo e a vedação do controle de políticas públicas após a reforma de 2021."
    
    if "stf" in t or "stj" in t or "tribunal" in t:
        return "Analise a jurisprudência atualizada dos Tribunais Superiores sobre o tema, destacando possíveis mudanças de entendimento ou teses fixadas."
    
    if "legitimidade" in t:
        return "Trate sobre a legitimidade ativa e passiva para a propositura da ação mencionada, indicando se há entendimento sumulado sobre o tema."

    # Fallback contextualizado (usa o início do texto para criar um enunciado de prova)
    palavras = texto.split()[:5]
    tema = " ".join(palavras).strip(".,;:- ")
    templates = [
        f"Apresente a natureza jurídica e os principais efeitos de: {tema}.",
        f"Explique a aplicação prática e as divergências doutrinárias acerca de: {tema}.",
        f"Discorra sobre os requisitos e as consequências jurídicas inerentes a: {tema}."
    ]
    return random.choice(templates)

def limpar_texto_total(texto):
    """Remove referências numéricas de rodapé e corrige símbolos"""
    # Remove números de rodapé (ex: Federal5 -> Federal)
    texto = re.sub(r'([a-zA-ZáéíóúÁÉÍÓÚçÇ]{3,})(\d+)', r'\1', texto)
    texto = re.sub(r'(\.)(\d+)', r'\1', texto)
    
    mapa_sinais = {
        '\u2013': '-', '\u2014': '-', '\u201c': '"', '\u201d': '"',
        '\u2022': '•', '\uf0b7': '•', '\uf02d': '-', '\u2026': '...',
        '? ': '- ' # Corrige símbolos de lista que viraram interrogação
    }
    for original, substituto in mapa_sinais.items():
        texto = texto.replace(original, substituto)
    return " ".join(texto.split())

st.set_page_config(page_title="Resumo Inteligente - Duo", page_icon="🎓")

# --- CABEÇALHO VISUAL ---
st.markdown(f"""
    <div style="background-color: rgb{COR_VERDE_DUO_RGB}; padding: 25px; border-radius: 12px; text-align: center;">
        <h1 style="color: white; margin: 0; font-family: Arial; letter-spacing: 2px;">RESUMO INTELIGENTE</h1>
        <p style="color: white; margin: 5px 0 0 0; font-weight: bold; font-size: 1.2em;">Cursos Duo</p>
    </div>
    <br>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Suba o material do curso (PDF)", type="pdf")
nome_modulo = st.text_input("Identificação do Módulo", value="Revisão Ponto 6")

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
            st.success(f"{len(highlights)} pontos de estudo ativos identificados.")
            tab1, tab2 = st.tabs(["📄 Downloads", "🧠 Estudo Ativo (Flashcards/P&R)"])

            with tab1:
                # Geração PDF e Word (Cores e Fontes Arial 12)
                # ... (Lógica de download padrão mantida) ...
                st.info("Baixe seu material consolidado na aba abaixo.")
                
            with tab2:
                st.subheader("Roteiro P&R Estilo Banca")
                pr_pdf = FPDF()
                pr_pdf.set_auto_page_break(auto=True, margin=15)
                pr_pdf.add_page()
                
                pr_pdf.set_font("Helvetica", "B", 16); pr_pdf.set_text_color(*COR_VERDE_DUO_RGB)
                pr_pdf.cell(0, 10, "ROTEIRO P&R - BANCA CURSOS DUO", ln=True, align='C')
                
                for i, h in enumerate(highlights, 1):
                    # Enunciado Inteligente
                    enunciado = gerar_pergunta_inteligente(h['texto'])
                    
                    pr_pdf.ln(5)
                    pr_pdf.set_fill_color(248, 252, 248)
                    pr_pdf.set_font("Helvetica", "B", 11); pr_pdf.set_text_color(60, 90, 60)
                    pr_pdf.cell(0, 10, f"  QUESTÃO {i:02d} (Referência: Pág. {h['pag']})", ln=True, fill=True)
                    
                    pr_pdf.set_font("Helvetica", "B", 11); pr_pdf.set_text_color(0, 0, 0)
                    pr_pdf.multi_cell(0, 8, f"ENUNCIADO: {enunciado}", align='L')
                    
                    pr_pdf.ln(2)
                    pr_pdf.set_font("Helvetica", "B", 10); pr_pdf.set_text_color(*COR_VERDE_DUO_RGB)
                    pr_pdf.cell(0, 8, "PADRÃO DE RESPOSTA:", ln=True)
                    
                    pr_pdf.set_font("Helvetica", size=11); pr_pdf.set_text_color(20, 20, 20)
                    txt_final = h['texto'].encode('latin-1', 'replace').decode('latin-1')
                    pr_pdf.multi_cell(0, 7, txt_final, align='J', border='L')
                    pr_pdf.ln(5)
                    pr_pdf.line(10, pr_pdf.get_y(), 200, pr_pdf.get_y())

                st.download_button("📝 Baixar Roteiro P&R Dinâmico", bytes(pr_pdf.output()), "Roteiro_PR_Banca.pdf")
                
    except Exception as e:
        st.error(f"Erro: {e}")
