# --- MELHORIA NA FUNÇÃO DE GERAÇÃO DE PERGUNTAS ---
def gerar_pergunta_contextualizada(texto: str, analise: Dict = None) -> str:
    """Gera enunciado técnico e completo condizente com o conteúdo do card."""
    if not analise:
        analise = analisar_conteudo_juridico(texto)
    
    t = texto.lower()
    
    # Mapeamento temático para enunciados assertivos de banca
    if "cpi" in t or "comissão parlamentar" in t:
        return "Acerca das Comissões Parlamentares de Inquérito (CPI), analise a validade do ato de criação considerando a natureza de direito das minorias e a exigência de fato determinado."
    
    if "stf" in t or "stj" in t or "sumula" in t:
        return "Considerando a jurisprudência consolidada dos Tribunais Superiores e as recentes alterações de entendimento citadas no material, julgue o item a seguir."
    
    if "parlamentar" in t or "imunidade" in t:
        return "No que tange ao estatuto dos congressistas, analise a extensão das imunidades material e formal em face da diplomação e do exercício do mandato."
    
    if "lia" in t or "improbidade" in t:
        return "Sobre a Lei de Improbidade Administrativa e suas alterações recentes, julgue a descrição da conduta e o elemento subjetivo (dolo) exigido para a configuração do ato."

    if "labelling" in t or "etiquetamento" in t:
        return "No contexto da Criminologia Crítica, analise a aplicação da Teoria do Etiquetamento e as reações sociais descritas no trecho."

    # Fallback inteligente para evitar perguntas curtas
    palavras = [p for p in texto.split() if len(p) > 3]
    tema = " ".join(palavras[:6]).strip(".,;:- ")
    return f"Considerando os aspectos doutrinários e a fundamentação legal sobre '{tema}', analise se a afirmação a seguir está correta."

# --- MELHORIA NA ABA DE SIMULADO (TAB 3) ---
with tab3:
    st.subheader("🧠 Simulado Certo ou Errado")
    st.write("Julgue os itens baseados integralmente no conteúdo do seu material:")
    
    # Correção na extração: Juntamos o texto e dividimos por blocos de parágrafos reais
    # Removemos quebras de linha simples que quebram frases e usamos duplo enter
    texto_processado = texto_completo.replace('-\n', '').replace('\n', ' ')
    # Dividimos em frases ou blocos de pelo menos 150 caracteres para não ficar "curto"
    blocos = [b.strip() for b in re.split(r'(?<=[.!?])\s+', texto_processado) if len(b.strip()) > 150]
    
    if not blocos:
        st.warning("⚠️ O conteúdo do PDF é muito curto ou não possui parágrafos estruturados para o simulado.")
    else:
        # Define 5 questões para o simulado
        num_questoes = min(len(blocos), 5)
        
        if 'simulado_sessao' not in st.session_state or st.button("🔄 Gerar Novas Questões"):
            selecionados = random.sample(blocos, num_questoes)
            st.session_state.simulado_sessao = [
                {'enunciado': gerar_pergunta_contextualizada(b), 'item': b} 
                for b in selecionados
            ]
        
        for idx, q in enumerate(st.session_state.simulado_sessao):
            st.markdown(f"""
                <div class="card-duo">
                    <p style="color: {COR_VERDE_DUO_HEX}; font-weight: bold; margin-bottom: 5px;">QUESTÃO {idx+1:02d}</p>
                    <p style="font-size: 0.95rem; margin-bottom: 10px;"><b>ENUNCIADO:</b> {q['enunciado']}</p>
                    <hr style="margin: 10px 0; border: 0.5px solid #eee;">
                    <p style="font-style: italic; background: #fafafa; padding: 10px; border-radius: 5px;">
                        "...{q['item']}..."
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            resp = st.radio(
                "Sua avaliação:",
                ["Selecione", "Certo", "Errado"],
                key=f"simu_resp_{idx}",
                horizontal=True
            )
            
            if resp != "Selecione":
                if resp == "Certo":
                    st.success("✅ **Correto!** O item está em perfeita consonância com o material.")
                else:
                    st.error("❌ **Incorreto.** No contexto deste material de estudo, esta afirmação é considerada correta.")
            st.markdown("<br>", unsafe_allow_html=True)
