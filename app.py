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

def limpar_texto_total(texto):
    """Extração fiel de todos os símbolos %$()_* e remoção de rodapés numéricos"""
    # 1. Remove números de rodapé colados ao final das palavras (ex: Federal5 -> Federal)
    texto = re.sub(r'([a-zA-ZáéíóúÁÉÍÓÚçÇ]{3,})(\d+)', r'\1', texto)
    texto = re.sub(r'(\.)(\d+)', r'\1', texto)
    
    # 2. Mapeamento de sinais para compatibilidade total com PDF
    mapa_sinais = {
        '\u2013': '-', '\u2014': '-', '\u201c': '"', '\u201d': '"',
        '\u2018': "'", '\u2019': "'", '\u2022': '•', '\uf0b7': '•',
        '\uf02d': '-', '\uf0d8': '>', '\u2026': '...', '\u00a0': ' ',
        '? ': '- ' # Correção para marcadores que viram interrogação
    }
    for original, substituto in mapa_sinais.items():
        texto = texto.replace(original, substituto)
    
    # Mantém fielmente % $ ( ) _ * conforme solicitado
    return " ".join(texto.split())

def gerar_enunciado_prova(texto):
    """Gera um enunciado específico e técnico conforme o tema detectado"""
    t = texto.lower()
    if "cpi" in t: return "Analise a CPI sob a ótica do direito das minorias e seus requisitos constitucionais."
    if "parlamentar" in t: return "Discorra sobre o regime de imunidades e o marco temporal da diplomação."
    if "labelling" in t: return "Analise a Teoria do Etiquetamento e as propostas político-criminais decorrentes."
    if "stf" in t or "stj" in t: return "Analise a jurisprudência atualizada dos Tribunais Superiores sobre o tema."
    return f"Sobre o tema abordado na página, julgue o item a seguir:"

# Configuração para Mobile/Tablet [layout centered é melhor para telas menores]
st.set_page_config(page_title="Resumo Inteligente - Duo", page_icon="🎓", layout="centered")

# Cabeçalho Visual Duo
st.markdown(f"""
    <div style="background-color: rgb{COR_VERDE_DUO_RGB}; padding: 25px; border-radius: 15px; text-align: center;">
        <h1 style="color: white; margin: 0; font-family: sans-serif; font-size: 1.8em;">RESUMO INTELIGENTE</h1>
        <p style="color: white; margin: 5px 0 0 0; font-weight: bold;">Cursos Duo</p>
    </div>
    <br>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Suba o material do Cursos Duo (PDF)", type="pdf")
nome_modulo = st.text_input("Identificação do Material", value="Revisão Estratégica")

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
            st.success(f"{len(highlights)} pontos identificados para estudo.")
            
            # Abas otimizadas para toque (Mobile/iPad)
            tab1, tab2, tab3 = st.tabs(["📄 Resumo", "🗂️ Flashcards & P&R", "🧠 Simulado C/E"])

            with tab1:
                # Geração de PDF e Word (Arial 12 + Título Verde)
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
                    txt_seguro = h['texto'].encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(190, 7, txt_seguro, align='J')
                    pdf.ln(4)

                word_doc = Document()
                h_w = word_doc.add_heading(level=0)
                r_h = h_w.add_run("RESUMO INTELIGENTE"); r_h.font.color.rgb = RGBColor(166, 201, 138)
                for i, h in enumerate(highlights, 1):
                    p = word_doc.add_paragraph()
                    rt = p.add_run(f"ITEM {i:02d} | PÁGINA {h['pag']}\n"); rt.bold = True; rt.font.color.rgb = RGBColor(166, 201, 138)
                    rtx = p.add_run(h['texto']); rtx.font.name = 'Arial'; rtx.font.size = Pt(12); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

                # Botões de download responsivos
                c1, c2 = st.columns(2)
                with c1: st.download_button("📥 PDF", bytes(pdf.output()), "Resumo_Duo.pdf")
                with c2:
                    buf = io.BytesIO(); word_doc.save(buf)
                    st.download_button("📥 Word", buf.getvalue(), "Resumo_Duo.docx")

            with tab2:
                # Flashcards e Roteiro P&R adaptados para a página
                st.write("Materiais para revisão ativa:")
                
                # PDF Flashcards (Grade de Recorte Otimizada)
                f_pdf = FPDF()
                f_pdf.add_page()
                for i, h in enumerate(highlights, 1):
                    f_pdf.set_fill_color(*COR_VERDE_DUO_RGB); f_pdf.set_text_color(255, 255, 255)
                    f_pdf.set_font("Helvetica", "B", 10)
                    f_pdf.cell(190, 8, f" CARTÃO {i:02d} | PÁGINA {h['pag']}", border=1, ln=True, fill=True)
                    f_pdf.set_text_color(0, 0, 0); f_pdf.set_font("Helvetica", size=11)
                    txt_f = h['texto'].encode('latin-1', 'replace').decode('latin-1')
                    f_pdf.multi_cell(190, 8, txt_f, border=1, align='J')
                    f_pdf.ln(5)

                # PDF Roteiro P&R (Sem Título Repetitivo)
                pr_pdf = FPDF()
                pr_pdf.add_page()
                for i, h in enumerate(highlights, 1):
                    pr_pdf.set_fill_color(248, 252, 248)
                    pr_pdf.set_font("Helvetica", "B", 10); pr_pdf.set_text_color(60, 90, 60)
                    pr_pdf.cell(190, 8, f"  QUESTÃO {i:02d} (Pág. {h['pag']})", ln=True, fill=True, border='B')
                    pr_pdf.set_font("Helvetica", size=10); pr_pdf.set_text_color(0, 0, 0)
                    txt_pr = h['texto'].encode('latin-1', 'replace').decode('latin-1')
                    pr_pdf.multi_cell(190, 6, f"ENUNCIADO: {gerar_enunciado_prova(h['texto'])}\nRESPOSTA: {txt_pr}", align='J', border='L')
                    pr_pdf.ln(5)

                st.download_button("✂️ Baixar Flashcards", bytes(f_pdf.output()), "Flashcards_Duo.pdf")
                st.download_button("📝 Baixar Roteiro P&R", bytes(pr_pdf.output()), "Roteiro_PR_Duo.pdf")

            with tab3:
                st.subheader("🧠 Simulado Certo ou Errado")
                st.write("Julgue os itens abaixo de acordo com o material:")
                
                amostra = random.sample(highlights, min(len(highlights), 3))
                for idx, item in enumerate(amostra):
                    st.info(f"**Item {idx+1}:** {item['texto']}")
                    resp = st.radio(f"Situação do Item {idx+1}:", ["Selecione", "Certo", "Errado"], key=f"quiz_{idx}")
                    
                    if resp != "Selecione":
                        if resp == "Certo":
                            st.success("✅ Correto! Esta é uma afirmação literal do seu material.")
                        else:
                            st.error("❌ Errado. De acordo com o material, a afirmação está correta.")
                    st.divider()

        st.markdown(f"<hr><p style='text-align: center; color: gray; font-size: 0.8em;'>Dúvidas: sugestoes@cursosduo.com.br</p>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Erro no processamento: {e}")
