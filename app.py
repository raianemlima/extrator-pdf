import streamlit as st
import fitz  # PyMuPDF
import pandas as pd

st.set_page_config(page_title="Extrator de Destaques", page_icon="📝")

st.title("📝 Extrator de Grifos em PDF")
st.write("Suba o seu PDF para listar todos os textos que você destacou com marca-texto.")

# Upload do arquivo
uploaded_file = st.file_uploader("Escolha um arquivo PDF", type="pdf")

if uploaded_file is not None:
    # Abrir o PDF usando o buffer do arquivo subido
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    
    highlights = []

    # Percorrer as páginas
    for page_num, page in enumerate(doc):
        # Buscar anotações na página
        for annot in page.annots():
            # O tipo 8 corresponde ao Highlight (marca-texto)
            if annot.type[0] == 8:
                # Extrair o texto que está sob a área da anotação
                text = page.get_textbox(annot.rect)
                highlights.append({
                    "Página": page_num + 1,
                    "Texto Destacado": text.strip()
                })

    if highlights:
        st.success(f"Encontramos {len(highlights)} destaques!")
        
        # Criar um DataFrame para exibir bonitinho
        df = pd.DataFrame(highlights)
        
        # Exibir na tela
        st.table(df)
        
        # Botão para baixar como CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Baixar destaques como CSV",
            data=csv,
            file_name="destaques_pdf.csv",
            mime="text/csv",
        )
    else:
        st.warning("Nenhum destaque (marca-texto) foi encontrado neste PDF.")
