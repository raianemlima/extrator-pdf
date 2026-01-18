import streamlit as st
import fitz  # PyMuPDF
from fpdf import FPDF
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import date
import io
import random

# Identidade Visual Duo: Verde das barras de título [cite: 3, 27]
COR_VERDE_DUO = (166, 201, 138) 

def limpar_texto(texto):
    """Substitui caracteres especiais e remove quebras internas para justificação"""
    mapa = {
        '\u2013': '-', '\u2014': '-', '\u201c': '"', '\u201d': '"',
        '\u2018': "'", '\u2019': "'", '\u2022': '*', '\u2026': '...'
    }
    for original, substituto in mapa.items():
        texto = texto.replace(original, substituto)
    return " ".join(texto.split())

st.set_page_config(page_title="Duo Study Hub", page_icon="🎓")

# Cabeçalho da Interface Cursos Duo [cite: 1]
st.markdown(f"""
    <div style="background-color: rgb{COR_VERDE_DUO}; padding: 20px; border-radius: 10px; text-align: center;">
        <h1 style="color: white; margin: 0; font-family: Arial, sans-serif;">CURSOS DUO</h1>
        <p style="color: white; margin: 0; font-weight: bold;">Plataforma de Extração e Estudo Ativo</p>
    </div>
    <br>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Suba o material do Cursos Duo (PDF)", type="pdf")
nome_modulo = st.text_input("Nome do Módulo", placeholder="Ex: Direitos Difusos e Coletivos - Ponto 6")

if uploaded_file is not None:
    try:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        highlights = []
        for page_num, page in enumerate(doc):
            for annot in page.annots():
                if annot.type[0] == 8: # Tipo Highlight
                    text = page.get_textbox(annot.rect)
                    if text.strip():
                        highlights.append({"pag": page_num + 1, "texto": limpar_texto(text)})

        if highlights:
            st.success(f"Sucesso! {len(highlights)} destaques processados.")
            tab1, tab2, tab3 = st.tabs(["📄 Downloads do Resumo", "🗂️ Flashcards para Recortar", "🧠 Quiz Dinâmico"])

            # --- TAB 1: DOWNLOADS (PDF E WORD) ---
            with tab1:
                st.write("Selecione o formato desejado para o seu resumo (Arial 12):")
                
                # Gerador PDF (Arial 12 / Helvetica como equivalente seguro)
                pdf = FPDF()
                pdf.add_page()
                pdf.set_fill_color(*COR_VERDE_DUO)
                pdf.rect(0, 0, 210, 40, 'F')
                pdf.set_font("Helvetica", "B", 14)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 10, "RESUMO DESTAQUES - CURSOS DUO", ln=True, align='C')
                pdf.set_font("Helvetica", "I", 12)
                pdf.cell(0, 10, f"Material: {nome_modulo}", ln=True, align='C')
                pdf.ln(25)
                
                pdf.set_font("Helvetica", size=9)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 5, f"Data: {date.today().strftime('%d/%m/%Y')}", ln=True, align='R')
                pdf.ln(5)

                for i, h in enumerate(highlights, 1):
                    pdf.set_font("Helvetica", "B", 11)
                    pdf.set_text_color(*COR_VERDE_DUO)
                    pdf.cell(0, 8, f"ITEM {i:02d} | PÁGINA {h['pag']}", ln=True)
                    pdf.set_font("Helvetica", size=12) 
                    pdf.set_text_color(0, 0, 0)
                    txt_enc = h['texto'].encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 7, txt_enc, align='J')
                    pdf.ln(4)
                
                # Gerador Word (Arial 12)
                word_doc = Document()
                word_doc.add_heading("RESUMO DESTAQUES - CURSOS DUO", 0)
                word_doc.add_paragraph(f"Material: {nome_modulo}")
                word_doc.add_paragraph(f"Gerado em: {date.today().strftime('%d/%m/%Y')}")

                for i, h in enumerate(highlights, 1):
                    p = word_doc.add_paragraph()
                    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    run_title = p.add_run(f"ITEM {i:02d} | PÁGINA {h['pag']}\n")
                    run_title.bold = True
                    run_text = p.add_run(h['texto'])
                    run_text.font.name = 'Arial'
                    run_text.font.size = Pt(12)

                col1, col2 = st.columns(2)
                with col1:
                    st.download_button("📥 Baixar PDF", bytes(pdf.output()), f"Resumo_{nome_modulo}.pdf", "application/pdf")
                with col2:
                    buffer = io.BytesIO()
                    word_doc.save(buffer)
                    st.download_button("📥 Baixar Word", buffer.getvalue(), f"Resumo_{nome_modulo}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

            # --- TAB 2: FLASHCARDS (TABELA PARA RECORTE) ---
            with tab2:
                st.subheader("🗂️ Tabela de Flashcards para Impressão")
                st.write("Cada item abaixo será organizado em uma tabela no PDF para você imprimir e recortar.")
                
                f_pdf = FPDF()
                f_pdf.add_page()
                f_pdf.set_font("Helvetica", "B", 14)
                f_pdf.cell(0, 10, "TABELA DE FLASHCARDS - CURSOS DUO", ln=True, align='C')
                f_pdf.ln(10)

                for i, h in enumerate(highlights, 1):
                    # Desenha a "caixa" do flashcard
                    f_pdf.set_draw_color(*COR_VERDE_DUO)
                    f_pdf.set_fill_color(250, 250, 250)
                    f_pdf.set_font("Helvetica", "B", 10)
                    f_pdf.cell(0, 8, f" CARTÃO {i:02d} | PÁGINA {h['pag']}", border=1, ln=True, fill=True)
                    
                    f_pdf.set_font("Helvetica", size=12)
                    txt_f = h['texto'].encode('latin-1', 'replace').decode('latin-1')
                    f_pdf.multi_cell(0, 10, txt_f, border=1, align='J')
                    f_pdf.ln(5)
                
                st.download_button("✂️ Baixar Flashcards para Recortar", bytes(f_pdf.output()), "flashcards_recorte_duo.pdf", "application/pdf")

            # --- TAB 3: QUIZ DINÂMICO ---
            with tab3:
                st.subheader("🧠 Desafio de Memória Ativa")
                amostra = random.sample(highlights, min(len(highlights), 3))
                for idx, item in enumerate(amostra):
                    palavras = item['texto'].split()
                    if len(palavras) > 5:
                        secreta = max(palavras, key=len).strip(".,;:()")
                        pergunta = item['texto'].replace(secreta, "__________")
                        st.write(f"**Questão {idx+1}:** {pergunta}")
                        resp = st.text_input(f"Complete a lacuna (Pág {item['pag']}):", key=f"qz_{idx}")
                        if st.button(f"Verificar Questão {idx+1}"):
                            if resp.lower().strip() == secreta.lower().strip(): st.success(f"Excelente! A palavra era: {secreta}")
                            else: st.warning(f"Quase! A resposta era: {secreta}")
                        st.divider()

        # Rodapé Institucional [cite: 21]
        st.markdown(f"""
            <hr>
            <p style="text-align: center; color: gray; font-size: 0.8em;">
                Dúvidas e sugestões: <a href="mailto:sugestoes@cursosduo.com.br">sugestoes@cursosduo.com.br</a>
            </p>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Erro ao processar material: {e}")
