
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
from typing import List, Dict

# Constantes
COR_VERDE_DUO_RGB = (166, 201, 138)
COR_VERDE_DUO_HEX = "#A6C98A"

# Configuração da página
st.set_page_config(
    page_title="Resumo Inteligente - Duo",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS customizado para melhor responsividade
st.markdown("""
    <style>
    .main {padding: 1rem;}
    @media (max-width: 768px) {
        .main {padding: 0.5rem;}
    }
    </style>
""", unsafe_allow_html=True)


def limpar_texto_total(texto: str) -> str:
    """
    Limpa e normaliza o texto extraído do PDF.
    
    Args:
        texto: Texto bruto extraído
        
    Returns:
        Texto limpo e normalizado
    """
    if not texto:
        return ""
    
    # Remove números de rodapé colados
    texto = re.sub(r'([a-zA-ZáéíóúÁÉÍÓÚçÇ]{3,})(\d+)', r'\1', texto)
    texto = re.sub(r'(\.)(\d+)', r'\1', texto)
    
    # Mapeamento de caracteres especiais
    mapa_sinais = {
        '\u2013': '-', '\u2014': '-', '\u201c': '"', '\u201d': '"',
        '\u2018': "'", '\u2019': "'", '\u2022': '•', '\uf0b7': '•',
        '\uf02d': '-', '\uf0d8': '>', '\u2026': '...', '\u00a0': ' ',
        '? ': '- '
    }
    
    for original, substituto in mapa_sinais.items():
        texto = texto.replace(original, substituto)
    
    return " ".join(texto.split())


def gerar_pergunta_contextualizada(texto: str) -> str:
    """
    Gera pergunta baseada no conteúdo do destaque.
    
    Args:
        texto: Texto do destaque
        
    Returns:
        Pergunta contextualizada
    """
    t = texto.lower()
    
    # Mapeamento temático
    temas = {
        "cpi": "Como o material define a natureza da CPI e quais são os seus requisitos de criação?",
        "parlamentar|diplomação": "O que o texto explica sobre o início das garantias parlamentares e a imunidade?",
        "labelling|etiquetamento": "Quais são os pontos centrais da Teoria do Etiquetamento e as propostas dos '4 Ds' citadas?",
        "stf|stj": "Qual é o posicionamento atualizado dos Tribunais Superiores sobre este ponto do destaque?",
        "improbidade|lia": "Quais as principais características do ato de improbidade e a exigência de dolo mencionada?"
    }
    
    for palavras_chave, pergunta in temas.items():
        if any(palavra in t for palavra in palavras_chave.split("|")):
            return pergunta
    
    # Fallback: pergunta genérica
    palavras = texto.split()[:6]
    tema = " ".join(palavras).strip(".,;:- ")
    return f"Explique o que o material aborda sobre '{tema}' e qual sua importância no contexto estudado."


def extrair_destaques(pdf_file) -> List[Dict[str, any]]:
    """
    Extrai destaques (highlights) do PDF.
    
    Args:
        pdf_file: Arquivo PDF carregado
        
    Returns:
        Lista de dicionários com página e texto
    """
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    highlights = []
    
    for page_num, page in enumerate(doc):
        for annot in page.annots():
            if annot.type[0] == 8:  # Tipo 8 = Highlight
                texto_extraido = page.get_textbox(annot.rect)
                texto_limpo = limpar_texto_total(texto_extraido)
                
                if texto_limpo:  # Só adiciona se houver conteúdo
                    highlights.append({
                        "pag": page_num + 1,
                        "texto": texto_limpo
                    })
    
    return highlights


def criar_pdf_resumo(highlights: List[Dict], nome_modulo: str) -> bytes:
    """Cria PDF do resumo formatado."""
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho
    pdf.set_fill_color(*COR_VERDE_DUO_RGB)
    pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 15, "RESUMO INTELIGENTE", ln=True, align='C')
    pdf.set_font("Helvetica", size=11)
    pdf.cell(0, 8, nome_modulo, ln=True, align='C')
    pdf.ln(25)
    
    # Conteúdo
    for i, h in enumerate(highlights, 1):
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(*COR_VERDE_DUO_RGB)
        pdf.cell(0, 8, f"ITEM {i:02d} | PÁG. {h['pag']}", ln=True)
        
        pdf.set_font("Helvetica", size=12)
        pdf.set_text_color(0, 0, 0)
        txt_pdf = h['texto'].encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(190, 7, txt_pdf, align='J')
        pdf.ln(4)
    
    return bytes(pdf.output())


def criar_word_resumo(highlights: List[Dict], nome_modulo: str) -> bytes:
    """Cria documento Word do resumo."""
    doc = Document()
    
    # Título
    h_titulo = doc.add_heading(level=0)
    run_titulo = h_titulo.add_run("RESUMO INTELIGENTE")
    run_titulo.font.color.rgb = RGBColor(*COR_VERDE_DUO_RGB)
    
    p_modulo = doc.add_paragraph()
    run_modulo = p_modulo.add_run(nome_modulo)
    run_modulo.bold = True
    
    # Conteúdo
    for i, h in enumerate(highlights, 1):
        p = doc.add_paragraph()
        
        rt = p.add_run(f"ITEM {i:02d} | PÁGINA {h['pag']}\n")
        rt.bold = True
        rt.font.color.rgb = RGBColor(*COR_VERDE_DUO_RGB)
        
        rtx = p.add_run(h['texto'])
        rtx.font.name = 'Arial'
        rtx.font.size = Pt(12)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    # Salvar em buffer
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def criar_pdf_perguntas(highlights: List[Dict]) -> bytes:
    """Cria PDF com roteiro de perguntas e respostas."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    for i, h in enumerate(highlights, 1):
        # Cabeçalho da questão
        pdf.set_fill_color(248, 252, 248)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(60, 90, 60)
        pdf.cell(190, 8, f"  QUESTÃO {i:02d} (Pág. {h['pag']})", ln=True, fill=True, border='B')
        
        # Pergunta
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(0, 0, 0)
        pergunta = gerar_pergunta_contextualizada(h['texto'])
        pdf.multi_cell(190, 6, f"PERGUNTA: {pergunta}", align='L')
        
        pdf.ln(1)
        
        # Resposta
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*COR_VERDE_DUO_RGB)
        pdf.cell(190, 6, "RESPOSTA DO MATERIAL:", ln=True)
        
        pdf.set_font("Helvetica", size=10)
        pdf.set_text_color(20, 20, 20)
        txt_pr = h['texto'].encode('latin-1', 'replace').decode('latin-1')
        pdf.set_draw_color(*COR_VERDE_DUO_RGB)
        pdf.multi_cell(190, 5, txt_pr, align='J', border='L')
        pdf.ln(6)
    
    return bytes(pdf.output())


def criar_pdf_flashcards(highlights: List[Dict]) -> bytes:
    """Cria PDF com flashcards para impressão."""
    pdf = FPDF()
    pdf.add_page()
    
    for i, h in enumerate(highlights, 1):
        pdf.set_fill_color(*COR_VERDE_DUO_RGB)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(190, 8, f" CARTÃO {i:02d} | PÁGINA {h['pag']}", border=1, ln=True, fill=True)
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", size=11)
        txt_f = h['texto'].encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(190, 8, txt_f, border=1, align='J')
        pdf.ln(5)
    
    return bytes(pdf.output())


def renderizar_cabecalho():
    """Renderiza o cabeçalho da aplicação."""
    st.markdown(f"""
        <div style="background-color: {COR_VERDE_DUO_HEX}; padding: 25px; 
                    border-radius: 15px; text-align: center; margin-bottom: 2rem;">
            <h1 style="color: white; margin: 0; font-family: sans-serif; font-size: 1.8em;">
                RESUMO INTELIGENTE
            </h1>
            <p style="color: white; margin: 5px 0 0 0; font-weight: bold;">Cursos Duo</p>
        </div>
    """, unsafe_allow_html=True)


def renderizar_rodape():
    """Renderiza o rodapé da aplicação."""
    st.markdown("""
        <hr>
        <p style='text-align: center; color: gray; font-size: 0.8em;'>
            Dúvidas: sugestoes@cursosduo.com.br
        </p>
    """, unsafe_allow_html=True)


# ==================== INTERFACE PRINCIPAL ====================

def main():
    """Função principal da aplicação."""
    renderizar_cabecalho()
    
    # Upload e configuração
    uploaded_file = st.file_uploader("Suba o material do Cursos Duo (PDF)", type="pdf")
    nome_modulo = st.text_input("Identificação do Material", value="Revisão Ponto 6")
    
    if uploaded_file is None:
        st.info("👆 Faça upload de um PDF com destaques (highlights) para começar.")
        return
    
    try:
        # Extração de destaques
        with st.spinner("Extraindo destaques do PDF..."):
            highlights = extrair_destaques(uploaded_file)
        
        if not highlights:
            st.warning("⚠️ Nenhum destaque (highlight) encontrado no PDF. Certifique-se de marcar os trechos importantes.")
            return
        
        st.success(f"✅ Pronto! {len(highlights)} pontos de estudo identificados.")
        
        # Abas de conteúdo
        tab1, tab2, tab3 = st.tabs(["📄 Resumo", "🗂️ Flashcards & P&R", "🧠 Simulado"])
        
        with tab1:
            st.subheader("Resumo Estruturado")
            
            # Prévia
            with st.expander("📋 Visualizar prévia", expanded=False):
                for i, h in enumerate(highlights[:3], 1):
                    st.markdown(f"**Item {i:02d} | Página {h['pag']}**")
                    st.write(h['texto'])
                    st.divider()
                if len(highlights) > 3:
                    st.caption(f"...e mais {len(highlights) - 3} itens")
            
            # Downloads
            col1, col2 = st.columns(2)
            
            with col1:
                pdf_resumo = criar_pdf_resumo(highlights, nome_modulo)
                st.download_button(
                    "📥 Baixar PDF",
                    pdf_resumo,
                    f"Resumo_{nome_modulo.replace(' ', '_')}.pdf",
                    "application/pdf"
                )
            
            with col2:
                word_resumo = criar_word_resumo(highlights, nome_modulo)
                st.download_button(
                    "📥 Baixar Word",
                    word_resumo,
                    f"Resumo_{nome_modulo.replace(' ', '_')}.docx",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
        
        with tab2:
            st.subheader("Material de Revisão Ativa")
            
            col_x, col_y = st.columns(2)
            
            with col_x:
                pdf_perguntas = criar_pdf_perguntas(highlights)
                st.download_button(
                    "📝 Baixar Roteiro P&R",
                    pdf_perguntas,
                    f"Roteiro_PR_{nome_modulo.replace(' ', '_')}.pdf",
                    "application/pdf"
                )
            
            with col_y:
                pdf_flashcards = criar_pdf_flashcards(highlights)
                st.download_button(
                    "✂️ Baixar Flashcards",
                    pdf_flashcards,
                    f"Flashcards_{nome_modulo.replace(' ', '_')}.pdf",
                    "application/pdf"
                )
        
        with tab3:
            st.subheader("🧠 Simulado Certo ou Errado")
            
            num_questoes = min(len(highlights), 5)
            amostra = random.sample(highlights, num_questoes)
            
            # Estado para controlar respostas
            if 'respostas' not in st.session_state:
                st.session_state.respostas = {}
            
            for idx, item in enumerate(amostra):
                st.markdown(f"**Questão {idx+1}** (Página {item['pag']})")
                st.info(item['texto'])
                
                resp = st.radio(
                    f"Sua avaliação:",
                    ["Selecione", "Certo", "Errado"],
                    key=f"qz_{idx}",
                    horizontal=True
                )
                
                if resp != "Selecione":
                    if resp == "Certo":
                        st.success("✅ Correto! Afirmação condizente com o material.")
                    else:
                        st.error("❌ Errado. De acordo com o material, a afirmação está correta.")
                
                st.divider()
        
        renderizar_rodape()
    
    except Exception as e:
        st.error(f"❌ Erro no processamento: {str(e)}")
        st.exception(e)


if __name__ == "__main__":
    main()
