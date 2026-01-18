import streamlit as st
import fitz  # PyMuPDF
from fpdf import FPDF
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import date
import io
import random

# Cor verde extraída das barras de título do material enviado
COR_VERDE_DUO = (166, 201, 138) 

def limpar_texto(texto):
    """Corrige caracteres especiais para evitar '?' e remove quebras internas"""
    mapa = {
        '\u2013': '-', '\u2014': '-', '\u201c': '"', '\u201d': '"',
        '\u2018': "'", '\u2019': "'", '\u2022': '*', '\u2026': '...'
    }
    for original, substituto in mapa.items():
        texto = texto.replace(original, substituto)
    return " ".join(texto.split())

st.set_page_config(page_title="Resumo Inteligente - Duo", page_icon="🎓")

# --- INTERFACE VISUAL DO APP ---
st.markdown(f"""
    <div style="background-color: rgb{COR_VERDE_DUO}; padding: 25px; border-radius: 12px; text-align: center; border: 1px solid #d1e7dd;">
        <h1 style="color: white; margin: 0; font-family: Arial, sans-serif; letter-spacing: 2px; font-size: 2.2em;">RESUMO INTELIGENTE</h1>
        <p style="color: white; margin: 5px 0 0 0; font-family: Arial, sans-serif; font-size: 1.4em; font-weight: bold; opacity: 0.9;">Cursos Duo</p>
    </div>
    <br>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Suba o material em PDF para processamento", type="pdf")
nome_modulo = st.text_input("Identificação do Material", placeholder="Ex: Direitos Difusos e Coletivos - Ponto 6")

if uploaded_file is not None:
    try:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        highlights = []
        for page_num, page in enumerate(doc):
            for annot in page.annots():
                if annot.type[0] == 8: # Highlight
                    text = page.get_textbox(annot.rect)
                    if text.strip():
                        highlights.append({"pag": page_num + 1, "texto": limpar_texto(text)})

        if highlights:
            st.success(f"Sucesso! {len(highlights)} destaques identificados.")
            tab1, tab2, tab3 = st.tabs(["📄 Downloads", "✂️ Flashcards para Recortar", "🧠 Quiz Ativo"])

            # --- TAB 1: DOWNLOADS (PDF E WORD) ---
            with tab1:
                st.write("Baixe seu resumo formatado em **Arial 12**:")
                
                # PDF
                pdf = FPDF()
                pdf.add_page()
                pdf.set_fill_color(*COR_VERDE_DUO)
                pdf.rect(0, 0, 210, 45, 'F')
                pdf.set_font("Helvetica", "B", 18)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 15, "RESUMO INTELIGENTE", ln=True, align='C')
                pdf.set_font("Helvetica", "B", 14)
                pdf.cell(0, 10, "Cursos Duo", ln=True, align='C')
                
                pdf.ln(25)
                pdf.set_font("Helvetica", "I", 10)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 5, f"Material: {nome_modulo} | Gerado em: {date.today().strftime('%d/%m/%Y')}", ln=True, align='R')
                pdf.ln(5)

                for i, h in enumerate(highlights, 1):
                    pdf.set_font("Helvetica", "B", 11)
                    pdf.set_text_color(*COR_VERDE_DUO)
                    pdf.cell(0, 8, f"ITEM {i:02d} | PÁGINA {h['pag']}", ln=True)
                    pdf.set_font("Helvetica", size=12) # Tamanho 12
                    pdf.set_text_color(0, 0, 0)
                    txt_enc = h['texto'].encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 7, txt_enc, align='J')
                    pdf.ln(4)
                
                # WORD
                word_doc = Document()
                word_doc.add_heading("RESUMO INTELIGENTE", 0)
                word_doc.add_paragraph("Cursos Duo").bold = True
                word_doc.add_paragraph(f"Material: {nome_modulo} | Data: {date.today().strftime('%d/%m/%Y')}")

                for i, h in enumerate(highlights, 1):
                    p = word_doc.add_paragraph()
                    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    run_title = p.add_run(f"ITEM {i:02d} | PÁGINA {h['pag']}\n")
                    run_title.bold = True
                    run_title.font.color.rgb = (166, 201, 138)
                    run_text = p.add_run(h['texto'])
                    run_text.font.name = 'Arial'
                    run_text.font.size = Pt(12)

                c1, c2 = st.columns(2)
                with c1: st.download_button("📥 Baixar PDF", bytes(pdf.output()), f"Resumo_Duo.pdf", "application/pdf")
                with c2:
                    buf = io.BytesIO()
                    word_doc.save(buf)
                    st.download_button("📥 Baixar Word", buf.getvalue(), f"Resumo_Duo.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

            # --- TAB 2: FLASHCARDS (TABELA) ---
            with tab2:
                st.subheader("✂️ Flashcards para Impressão")
                f_pdf = FPDF()
                f_pdf.add_page()
                f_pdf.set_font("Helvetica", "B", 14)
                f_pdf.cell(0, 10, "TABELA DE FLASHCARDS - CURSOS DUO", ln=True, align='C')
                f_pdf.ln(10)

                for i, h in enumerate(highlights, 1):
                    f_pdf.set_draw_color(*COR_VERDE_DUO)
                    f_pdf.set_fill_color(245, 245, 245)
                    f_pdf.set_font("Helvetica", "B", 10)
                    f_pdf.cell(0, 8, f" CARTÃO {i:02d} | PÁGINA {h['pag']}", border=1, ln=True, fill=True)
                    f_pdf.set_font("Helvetica", size=12)
                    txt_f = h['texto'].encode('latin-1', 'replace').decode('latin-1')
                    f_pdf.multi_cell(0, 10, txt_f, border=1, align='J')
                    f_pdf.ln(5)
                
                st.download_button("✂️ Baixar Flashcards (PDF)", bytes(f_pdf.output()), "flashcards_duo.pdf", "application/pdf")

            # --- TAB 3: QUIZ ---
            with tab3:
                st.subheader("🧠 Quiz de Recuperação Ativa")
                amostra = random.sample(highlights, min(len(highlights), 3))
                for idx, item in enumerate(amostra):
                    palavras = item['texto'].split()
                    if len(palavras) > 5:
                        secreta = max(palavras, key=len).strip(".,;:()")
                        pergunta = item['texto'].replace(secreta, "__________")
                        st.write(f"**Questão {idx+1}:** {pergunta}")
                        resp = st.text_input(f"Complete a lacuna (Pág {item['pag']}):", key=f"qz_{idx}")
                        if st.button(f"Verificar Questão {idx+1}"):
                            if resp.lower().strip() == secreta.lower().strip(): st.success(f"Correto! A palavra era: {secreta}")
                            else: st.warning(f"Resposta correta: {secreta}")
                        st.divider()

        st.markdown(f"""
            <hr><p style="text-align: center; color: gray; font-size: 0.8em;">
            Dúvidas e sugestões: <a href="mailto:sugestoes@cursosduo.com.br">sugestoes@cursosduo.com.br</a> [cite: 21, 30, 54]
            </p>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Erro no processamento: {e}")
