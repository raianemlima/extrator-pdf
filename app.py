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
    """Mapeia símbolos complexos para evitar o erro '?' observado no material de Criminologia"""
    mapa_sinais = {
        '\u2013': '-', '\u2014': '-', '\u201c': '"', '\u201d': '"',
        '\u2018': "'", '\u2019': "'", '\u2022': '•', '\uf0b7': '•',
        '\uf02d': '-', '\uf0d8': '>', '\u2026': '...', '\u00a0': ' ',
        '\u2010': '-', '\u2011': '-', '\u00ba': 'º', '\u00aa': 'ª',
        '? ': '- ', ' :': ':' # Ajuste para erros de renderização comuns
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
            tab1, tab2, tab3 = st.tabs(["📄 Downloads do Resumo", "🗂️ Flashcards Premium", "🧠 Quiz Dinâmico"])

            with tab1:
                # GERAÇÃO PDF (Arial/Helvetica 12)
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
                    txt_enc = h['texto'].encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 7, txt_enc, align='J')
                    pdf.ln(4)
                
                # GERAÇÃO WORD (Título Verde)
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
                    run_text.font.name = 'Arial'
                    run_text.font.size = Pt(12)

                c1, c2 = st.columns(2)
                with c1: st.download_button("📥 Baixar em PDF", bytes(pdf.output()), "Resumo_Duo.pdf")
                with c2:
                    buf = io.BytesIO()
                    word_doc.save(buf)
                    st.download_button("📥 Baixar em Word", buf.getvalue(), "Resumo_Duo.docx")

            with tab2:
                st.subheader("🗂️ Flashcards de Memória Ativa")
                st.write("Cartões prontos para impressão e perguntas de fixação:")
                
                # PDF de Flashcards Inteligentes (2 por página, Frente/Verso simulado)
                f_pdf = FPDF()
                f_pdf.set_auto_page_break(auto=True, margin=15)
                
                for i, h in enumerate(highlights, 1):
                    f_pdf.add_page()
                    # Cabeçalho do Cartão
                    f_pdf.set_fill_color(*COR_VERDE_DUO_RGB)
                    f_pdf.rect(10, 10, 190, 20, 'F')
                    f_pdf.set_font("Helvetica", "B", 14)
                    f_pdf.set_text_color(255, 255, 255)
                    f_pdf.set_xy(10, 15)
                    f_pdf.cell(190, 10, f"FLASHCARD {i:02d} | ORIGEM: PÁGINA {h['pag']}", align='C')
                    
                    # Espaço da Pergunta (Estudo Ativo)
                    f_pdf.ln(25)
                    f_pdf.set_font("Helvetica", "B", 12)
                    f_pdf.set_text_color(*COR_VERDE_DUO_RGB)
                    f_pdf.cell(0, 10, "CONCEITO PARA REVISAR:", ln=True)
                    
                    # Conteúdo (Resposta/Destaque)
                    f_pdf.set_font("Helvetica", size=12)
                    f_pdf.set_text_color(40, 40, 40)
                    txt_flash = h['texto'].encode('latin-1', 'replace').decode('latin-1')
                    f_pdf.multi_cell(0, 8, txt_flash, align='J', border=0)
                    
                    # Linha de Corte
                    f_pdf.set_y(260)
                    f_pdf.set_draw_color(200, 200, 200)
                    f_pdf.dashed_line(10, 270, 200, 270)

                col_x, col_y = st.columns(2)
                with col_x:
                    st.download_button("✂️ Baixar Flashcards (Modo Recorte)", bytes(f_pdf.output()), "Flashcards_Duo_Premium.pdf")
                
                # Roteiro P&R
                pr_pdf = FPDF()
                pr_pdf.add_page()
                pr_pdf.set_font("Helvetica", "B", 16)
                pr_pdf.cell(0, 10, "ROTEIRO P&R - ESTUDO ATIVO", ln=True, align='C')
                for i, h in enumerate(highlights, 1):
                    pr_pdf.ln(5)
                    pr_pdf.set_font("Helvetica", "B", 11)
                    pr_pdf.set_text_color(*COR_VERDE_DUO_RGB)
                    pr_pdf.cell(0, 8, f"QUESTÃO {i:02d} (Pág. {h['pag']}):", ln=True)
                    pr_pdf.set_font("Helvetica", "I", 11)
                    pr_pdf.set_text_color(50, 50, 50)
                    pr_pdf.multi_cell(0, 6, "Como você explicaria este ponto central do material?", align='L')
                    pr_pdf.set_font("Helvetica", size=11)
                    pr_pdf.set_text_color(0, 0, 0)
                    txt_pr = h['texto'].encode('latin-1', 'replace').decode('latin-1')
                    pr_pdf.multi_cell(0, 7, f"RESPOSTA: {txt_pr}", align='J', border='L')
                
                with col_y:
                    st.download_button("📝 Baixar Roteiro P&R", bytes(pr_pdf.output()), "Roteiro_PR_Duo.pdf")

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
