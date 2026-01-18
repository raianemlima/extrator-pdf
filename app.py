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
    """Analisa o texto e gera uma pergunta estilo banca de concurso"""
    texto_low = texto.lower()
    
    # Dicionário de Gatilhos e Templates de Bancas
    gatilhos = {
        "legitima": "Acerca da legitimidade (ativa/passiva) no tema proposto, quais os principais requisitos e divergências?",
        "teoria": "Explique a base teórica do instituto mencionado e como a doutrina majoritária classifica seus elementos.",
        "súmula": "Qual a posição consolidada dos Tribunais Superiores (STF/STJ) sobre este ponto específico?",
        "stf": "Analise o entendimento do STF citado e as consequências jurídicas de sua aplicação.",
        "stj": "Como o STJ tem decidido sobre esta controvérsia e qual o impacto para a prática jurídica?",
        "art.": "Discorra sobre a previsão legal citada, destacando sua interpretação literal e teleológica.",
        "prazo": "Indique o prazo estabelecido, sua natureza jurídica e as consequências de sua inobservância.",
        "requisito": "Quais são os requisitos essenciais para a configuração deste instituto segundo o material?",
        "competência": "Discorra sobre as regras de competência aplicáveis ao caso, destacando exceções importantes."
    }
    
    for chave, pergunta in gatilhos.items():
        if chave in texto_low:
            return pergunta
            
    # Fallback inteligente: Pega as primeiras palavras e cria um comando de prova
    palavras = texto.split()[:4]
    tema = " ".join(palavras).strip(".,;:-")
    return f"Discorra sobre os principais aspectos, a natureza jurídica e a relevância de: '{tema}'."

def limpar_texto_total(texto):
    """Remove referências de rodapé (ex: Federal5) e mapeia símbolos"""
    # Remove números de rodapé colados (Federal5 -> Federal)
    texto = re.sub(r'([a-zA-ZáéíóúÁÉÍÓÚçÇ]{3,})(\d+)', r'\1', texto)
    texto = re.sub(r'(\.)(\d+)', r'\1', texto)
    
    mapa_sinais = {
        '\u2013': '-', '\u2014': '-', '\u201c': '"', '\u201d': '"',
        '\u2018': "'", '\u2019': "'", '\u2022': '•', '\uf0b7': '•',
        '\uf0d8': '>', '\u2026': '...', '\u00a0': ' '
    }
    for original, substituto in mapa_sinais.items():
        texto = texto.replace(original, substituto)
    return " ".join(texto.split())

st.set_page_config(page_title="Resumo Inteligente - Duo", page_icon="🎓", layout="wide")

# --- CABEÇALHO VISUAL CURSOS DUO ---
st.markdown(f"""
    <div style="background-color: rgb{COR_VERDE_DUO_RGB}; padding: 30px; border-radius: 15px; text-align: center;">
        <h1 style="color: white; margin: 0; font-family: 'Arial Black', sans-serif; letter-spacing: 2px; font-size: 2.5em;">RESUMO INTELIGENTE</h1>
        <p style="color: white; margin: 5px 0 0 0; font-family: Arial, sans-serif; font-size: 1.3em; font-weight: bold;">Cursos Duo</p>
    </div>
    <br>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Suba o material do curso (PDF)", type="pdf")
nome_modulo = st.text_input("Tema do Módulo", placeholder="Ex: Criminologia - Labelling Approach")

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
            st.success(f"Otimização finalizada! {len(highlights)} pontos de estudo gerados.")
            tab1, tab2 = st.tabs(["📄 Downloads do Resumo", "🧠 Estudo Ativo (Flashcards/P&R)"])

            with tab1:
                # PDF FORMATO PADRÃO
                pdf = FPDF()
                pdf.add_page()
                pdf.set_fill_color(*COR_VERDE_DUO_RGB)
                pdf.rect(0, 0, 210, 45, 'F')
                pdf.set_font("Helvetica", "B", 18); pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 15, "RESUMO INTELIGENTE", ln=True, align='C')
                pdf.set_font("Helvetica", "B", 14); pdf.cell(0, 10, "Cursos Duo", ln=True, align='C')
                pdf.ln(25); pdf.set_font("Helvetica", size=10); pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 5, f"Material: {nome_modulo} | {date.today().strftime('%d/%m/%Y')}", ln=True, align='R')
                pdf.ln(5)

                for i, h in enumerate(highlights, 1):
                    pdf.set_font("Helvetica", "B", 11); pdf.set_text_color(*COR_VERDE_DUO_RGB)
                    pdf.cell(0, 8, f"ITEM {i:02d} | PÁGINA {h['pag']}", ln=True)
                    pdf.set_font("Helvetica", size=12); pdf.set_text_color(0, 0, 0)
                    pdf.multi_cell(0, 7, h['texto'].encode('latin-1', 'replace').decode('latin-1'), align='J')
                    pdf.ln(4)
                
                # WORD FORMATO PADRÃO (Título Verde)
                word_doc = Document()
                h_w = word_doc.add_heading(level=0)
                r_h = h_w.add_run("RESUMO INTELIGENTE"); r_h.font.color.rgb = RGBColor(166, 201, 138)
                word_doc.add_paragraph("Cursos Duo").bold = True
                for i, h in enumerate(highlights, 1):
                    p = word_doc.add_paragraph()
                    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    rt = p.add_run(f"ITEM {i:02d} | PÁGINA {h['pag']}\n"); rt.bold = True; rt.font.color.rgb = RGBColor(166, 201, 138)
                    rtx = p.add_run(h['texto']); rtx.font.name = 'Arial'; rtx.font.size = Pt(12)

                c1, c2 = st.columns(2)
                with c1: st.download_button("📥 Baixar PDF", bytes(pdf.output()), "Resumo_Duo.pdf")
                with c2:
                    buf = io.BytesIO(); word_doc.save(buf)
                    st.download_button("📥 Baixar Word", buf.getvalue(), "Resumo_Duo.docx")

            with tab2:
                st.subheader("Roteiro de Questões Discursivas (Banca Duo)")
                
                # PDF P&R COM DESIGN ADAPTADO
                pr_pdf = FPDF()
                pr_pdf.set_auto_page_break(auto=True, margin=15)
                pr_pdf.add_page()
                
                # Título Principal do Roteiro
                pr_pdf.set_font("Helvetica", "B", 16); pr_pdf.set_text_color(*COR_VERDE_DUO_RGB)
                pr_pdf.cell(0, 10, "ROTEIRO P&R - ESTUDO ATIVO", ln=True, align='C')
                pr_pdf.ln(5)

                for i, h in enumerate(highlights, 1):
                    # Box de Pergunta com Fundo Suave
                    pr_pdf.set_fill_color(248, 252, 248)
                    pr_pdf.set_font("Helvetica", "B", 12); pr_pdf.set_text_color(60, 90, 60)
                    pr_pdf.cell(0, 10, f"  QUESTÃO {i:02d} (Pág. {h['pag']})", ln=True, fill=True)
                    
                    # Pergunta Gerada Inteligente
                    pergunta_banca = gerar_pergunta_inteligente(h['texto'])
                    pr_pdf.set_font("Helvetica", "B", 11); pr_pdf.set_text_color(40, 40, 40)
                    pr_pdf.multi_cell(0, 8, f"ENUNCIADO: {pergunta_banca}", align='L')
                    
                    # Resposta Padrão Banca
                    pr_pdf.ln(2)
                    pr_pdf.set_font("Helvetica", "B", 10); pr_pdf.set_text_color(*COR_VERDE_DUO_RGB)
                    pr_pdf.cell(0, 8, "PADRÃO DE RESPOSTA (DESTAQUE DO MATERIAL):", ln=True)
                    
                    pr_pdf.set_font("Helvetica", size=11); pr_pdf.set_text_color(20, 20, 20)
                    txt_pr = h['texto'].encode('latin-1', 'replace').decode('latin-1')
                    pr_pdf.multi_cell(0, 7, txt_pr, align='J', border='L')
                    pr_pdf.ln(8)
                    pr_pdf.line(10, pr_pdf.get_y(), 200, pr_pdf.get_y())
                    pr_pdf.ln(5)

                col_a, col_b = st.columns(2)
                with col_a: st.download_button("📝 Baixar Roteiro P&R", bytes(pr_pdf.output()), "Roteiro_PR_Duo.pdf")
                
                # Flashcards Inteligentes (Design Adaptado)
                f_pdf = FPDF()
                f_pdf.add_page()
                for i, h in enumerate(highlights, 1):
                    f_pdf.set_fill_color(*COR_VERDE_DUO_RGB); f_pdf.set_text_color(255, 255, 255)
                    f_pdf.set_font("Helvetica", "B", 10)
                    f_pdf.cell(190, 8, f" CARTÃO {i:02d} | PÁGINA {h['pag']}", border=1, ln=True, fill=True)
                    f_pdf.set_text_color(0, 0, 0); f_pdf.set_font("Helvetica", size=11)
                    txt_f = h['texto'].encode('latin-1', 'replace').decode('latin-1')
                    f_pdf.multi_cell(190, 8, txt_f, border=1, align='J')
                    f_pdf.ln(6)
                with col_b: st.download_button("✂️ Baixar Flashcards", bytes(f_pdf.output()), "Flashcards_Duo.pdf")

    except Exception as e:
        st.error(f"Erro inesperado: {e}")
