import streamlit as st
import fitz  # PyMuPDF
from fpdf import FPDF
from datetime import date

COR_VERDE_DUO = (166, 201, 138) 

st.set_page_config(page_title="Duo Study Hub", page_icon="🎓")

# Cabeçalho Identidade Visual
st.markdown(f"""
    <div style="background-color: rgb{COR_VERDE_DUO}; padding: 20px; border-radius: 10px; text-align: center;">
        <h1 style="color: white; margin: 0; font-family: sans-serif;">CURSOS DUO</h1>
        <p style="color: white; margin: 0; font-weight: bold;">Central de Estudo Ativo</p>
    </div>
    <br>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Suba o material do Cursos Duo (PDF)", type="pdf")
nome_modulo = st.text_input("Tema do Material", placeholder="Ex: Ponto 6 - Processo Coletivo")

if uploaded_file is not None:
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    highlights = []
    for page_num, page in enumerate(doc):
        for annot in page.annots():
            if annot.type[0] == 8: 
                texto_limpo = " ".join(page.get_textbox(annot.rect).split())
                if texto_limpo:
                    highlights.append({"pag": page_num + 1, "texto": texto_limpo})

    if highlights:
        # Criação das Abas de Funcionalidade
        tab1, tab2, tab3 = st.tabs(["📄 Gerar PDF", "🗂️ Flashcards", "🧠 Quiz Rápido"])

        with tab1:
            st.info("Gere seu arquivo de revisão justificado e numerado.")
            # Lógica do PDF (Mesma anterior com ajuste de bytes)
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
            pdf.set_font("Helvetica", size=11)
            pdf.set_text_color(0, 0, 0)
            for i, h in enumerate(highlights, 1):
                txt = h['texto'].encode('latin-1', 'replace').decode('latin-1')
                pdf.set_font("Helvetica", "B", 10)
                pdf.set_text_color(*COR_VERDE_DUO)
                pdf.cell(0, 8, f"ITEM {i:02d} | PÁGINA {h['pag']}", ln=True)
                pdf.set_font("Helvetica", size=11)
                pdf.set_text_color(40, 40, 40)
                pdf.multi_cell(0, 7, txt, align='J')
                pdf.ln(4)
            
            pdf_bytes = bytes(pdf.output())
            st.download_button("📥 Baixar PDF do Resumo", pdf_bytes, f"Resumo_{nome_modulo}.pdf", "application/pdf")

        with tab2:
            st.subheader("🗂️ Seus Flashcards Personalizados")
            st.write("Tente lembrar o conteúdo do grifo antes de revelar a resposta!")
            for i, h in enumerate(highlights, 1):
                with st.expander(f"Cartão {i:02d} - Referência: Página {h['pag']}"):
                    st.write(h['texto'])

        with tab3:
            st.subheader("🧠 Teste de Conhecimento")
            st.write("Baseado nos temas deste módulo (Direitos Coletivos):")
            
            p1 = st.radio("1. O Mandado de Segurança Coletivo exige autorização expressa dos associados?", ["Sim", "Não"])
            if st.button("Conferir Resposta 1"):
                if p1 == "Não": st.success("Correto! Independe de autorização (Súmula 629 STF).")
                else: st.error("Incorreto. A Súmula 629 do STF dispensa autorização.")

            p2 = st.radio("2. A coisa julgada na ACP possui limite territorial?", ["Sim", "Não"])
            if st.button("Conferir Resposta 2"):
                if p2 == "Não": st.success("Correto! O STF declarou a limitação inconstitucional (Tema 1075).")
                else: st.error("Incorreto. O STF superou a territorialidade no Tema 1075.")
    else:
        st.warning("Nenhum destaque encontrado.")
