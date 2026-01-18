import streamlit as st
import fitz  # PyMuPDF
from fpdf import FPDF
from datetime import date
import random

# Cor verde oficial do Cursos Duo [cite: 3, 27]
COR_VERDE_DUO = (166, 201, 138) 

def limpar_caracteres_especiais(texto):
    """Substitui caracteres que costumam virar '?' no PDF"""
    mapa = {
        '\u2013': '-', # en dash
        '\u2014': '-', # em dash
        '\u201c': '"', # smart quote open
        '\u201d': '"', # smart quote close
        '\u2018': "'", # smart quote single open
        '\u2019': "'", # smart quote single close
        '\u2022': '*', # bullet point
        '\u2026': '...' # ellipsis
    }
    for original, substituto in mapa.items():
        texto = texto.replace(original, substituto)
    
    # Remove quebras de linha internas para garantir a justificação 'J'
    return " ".join(texto.split())

st.set_page_config(page_title="Duo Study Hub", page_icon="🎓")

# Cabeçalho da Interface
st.markdown(f"""
    <div style="background-color: rgb{COR_VERDE_DUO}; padding: 20px; border-radius: 10px; text-align: center;">
        <h1 style="color: white; margin: 0; font-family: sans-serif;">CURSOS DUO</h1>
        <p style="color: white; margin: 0; font-weight: bold;">Plataforma de Estudo Ativo e Revisão</p>
    </div>
    <br>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Suba o material do Cursos Duo (PDF)", type="pdf")
nome_modulo = st.text_input("Identificação do Tema", placeholder="Ex: Ponto 6 - Processo Coletivo")

if uploaded_file is not None:
    try:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        highlights = []

        for page_num, page in enumerate(doc):
            for annot in page.annots():
                if annot.type[0] == 8: 
                    text = page.get_textbox(annot.rect)
                    if text.strip():
                        texto_tratado = limpar_caracteres_especiais(text)
                        highlights.append({"pag": page_num + 1, "texto": texto_tratado})

        if highlights:
            st.success(f"Material processado! Encontramos {len(highlights)} destaques.")
            
            tab1, tab2, tab3 = st.tabs(["📄 Resumo em PDF", "🗂️ Flashcards", "🧠 Quiz de Memória"])

            with tab1:
                pdf = FPDF()
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.add_page()
                
                # Cabeçalho Identidade Duo [cite: 1, 33]
                pdf.set_fill_color(*COR_VERDE_DUO)
                pdf.rect(0, 0, 210, 40, 'F')
                pdf.set_font("Helvetica", "B", 14)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 10, "RESUMO DESTAQUES - CURSOS DUO", ln=True, align='C')
                pdf.set_font("Helvetica", "I", 12)
                pdf.cell(0, 10, f"Material: {nome_modulo if nome_modulo else 'Revisão Geral'}", ln=True, align='C')
                
                pdf.ln(25)
                
                # Data [cite: 4, 180]
                pdf.set_font("Helvetica", size=9)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 5, f"Gerado em: {date.today().strftime('%d/%m/%Y')}", ln=True, align='R')
                pdf.ln(5)
                
                # Destaques Justificados e Numerados
                pdf.set_font("Helvetica", size=11)
                pdf.set_text_color(0, 0, 0)
                for i, h in enumerate(highlights, 1):
                    pdf.set_font("Helvetica", "B", 10)
                    pdf.set_text_color(*COR_VERDE_DUO)
                    pdf.cell(0, 8, f"ITEM {i:02d} | PÁGINA {h['pag']}", ln=True)
                    
                    pdf.set_font("Helvetica", size=11)
                    pdf.set_text_color(40, 40, 40)
                    # Codificação segura para evitar '?'
                    txt_final = h['texto'].encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 7, txt_final, align='J')
                    pdf.ln(5)

                # Rodapé com e-mail do curso [cite: 21, 150]
                pdf.set_y(-20)
                pdf.set_font("Helvetica", "I", 8)
                pdf.set_text_color(150, 150, 150)
                pdf.cell(0, 10, "Dúvidas e sugestões: sugestoes@cursosduo.com.br", align='C')

                pdf_bytes = bytes(pdf.output())
                st.download_button("📥 Baixar PDF do Resumo", pdf_bytes, f"Resumo_{nome_modulo}.pdf", "application/pdf")

            with tab2:
                st.subheader("🗂️ Flashcards Interativos")
                for i, h in enumerate(highlights, 1):
                    with st.expander(f"CARTÃO {i:02d} (Pág. {h['pag']})"):
                        st.write(h['texto'])

            with tab3:
                st.subheader("🧠 Quiz de Memória Ativa")
                st.write("Complete as lacunas dos seus próprios grifos para fixar o conteúdo:")
                
                amostra = random.sample(highlights, min(len(highlights), 3))
                for idx, item in enumerate(amostra):
                    palavras = item['texto'].split()
                    if len(palavras) > 6:
                        longas = [p for p in palavras if len(p) > 7]
                        if longas:
                            secreta = random.choice(longas).strip(".,;:()")
                            pergunta = item['texto'].replace(secreta, "__________")
                            st.markdown(f"**Questão {idx+1}:**")
                            st.write(f"*{pergunta}*")
                            resp = st.text_input(f"Sua resposta (Pág {item['pag']}):", key=f"quiz_{idx}")
                            if st.button(f"Checar {idx+1}"):
                                if resp.lower().strip() == secreta.lower().strip():
                                    st.success(f"Correto! A palavra é **{secreta}**.")
                                else:
                                    st.warning(f"A palavra correta era **{secreta}**.")
                            st.divider()

    except Exception as e:
        st.error(f"Erro ao processar o material: {e}")
