import os
import json
import uuid
import streamlit as st
from groq import Groq


# ===== CONFIGURAÇÃO INICIAL =====
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

CONVERSAS_PATH = "conversas.json"

def carregar_conversas():
    if os.path.exists(CONVERSAS_PATH):
        with open(CONVERSAS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_conversas(conversas):
    with open(CONVERSAS_PATH, "w", encoding="utf-8") as f:
        json.dump(conversas, f, ensure_ascii=False, indent=4)

# ===== PROMPT DE SISTEMA =====
CUSTOM_PROMPT = """
Você é um assistente de IA especialista em inglês, com foco principal em ensinar brasileiros. Sua missão é ajudar desenvolvedores iniciantes com dúvidas de gramática de forma clara, precisa e útil.

REGRAS DE OPERAÇÃO:
1.  **Foco em Gramática**: Responda apenas a perguntas relacionadas a inglês, gramática e sintaxe.
2.  **Estrutura da Resposta**: 
    * **Explicação Clara**
    * **Exemplo de Uso**
3.  **Clareza e Precisão**
"""

# ===== CARREGAR CONVERSAS SALVAS =====
conversas = carregar_conversas()

# ===== SIDEBAR =====
with st.sidebar:
    st.title("📚 AI Assistant")
    st.markdown("Um assistente de IA focado em te ajudar a aprender Inglês")

    groq_api_key = st.text_input(
        "Insira sua API Key Groq",
        type="password",
        help="Obtenha sua chave em https://console.groq.com/keys"
    )

    st.markdown("---")
    st.subheader("💬 Conversas Salvas")

    conversa_ids = list(conversas.keys())
    conversa_nomes = [conversas[cid]["titulo"] for cid in conversa_ids]

    conversa_selecionada = st.selectbox(
        "Selecione uma conversa",
        options=["Nova conversa"] + conversa_nomes
    )

    if conversa_selecionada == "Nova conversa":
        if st.button("➕ Criar nova conversa"):
            nova_id = str(uuid.uuid4())
            conversas[nova_id] = {"titulo": f"Conversa {len(conversas)+1}", "mensagens": []}
            salvar_conversas(conversas)
            st.session_state.conversa_id = nova_id
            st.rerun()
    else:
        # Seleciona conversa existente
        idx = conversa_nomes.index(conversa_selecionada)
        st.session_state.conversa_id = conversa_ids[idx]

    st.markdown("---")
    st.markdown("Desenvolvido para auxiliar em suas dúvidas de Inglês.")

# ===== ÁREA PRINCIPAL =====
st.title("📚 English AI Assistant")
st.caption("Faça sua pergunta ao assistente")

if "conversa_id" not in st.session_state:
    st.session_state.conversa_id = conversa_ids[0] if conversas else None

if st.session_state.conversa_id:
    conversa_atual = conversas[st.session_state.conversa_id]
else:
    st.warning("Crie uma nova conversa para começar.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = conversa_atual["mensagens"]

# Mostrar mensagens existentes
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ===== CLIENTE GROQ =====
client = None
if groq_api_key:
    try:
        client = Groq(api_key=groq_api_key)
    except Exception as e:
        st.sidebar.error(f"Erro ao inicializar o cliente Groq: {e}")
        st.stop()

# ===== INPUT DO CHAT =====
if prompt := st.chat_input("Qual sua dúvida sobre inglês?"):

    if not client:
        st.warning("Por favor, insira sua API Key da Groq na barra lateral.")
        st.stop()

    # Adiciona pergunta do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Envia histórico + system prompt
    messages_for_api = [{"role": "system", "content": CUSTOM_PROMPT}] + st.session_state.messages

    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                chat_completion = client.chat.completions.create(
                    messages=messages_for_api,
                    model="openai/gpt-oss-20b",
                    temperature=0.7,
                    max_tokens=2048,
                )

                resposta = chat_completion.choices[0].message.content
                st.markdown(resposta)
                st.session_state.messages.append({"role": "assistant", "content": resposta})

                # Atualiza conversa no JSON
                conversa_atual["mensagens"] = st.session_state.messages
                salvar_conversas(conversas)

            except Exception as e:
                st.error(f"Ocorreu um erro: {e}")

# ===== RODAPÉ =====
st.markdown(
    """
    <div style="text-align: center; color: gray;">
        <hr>
        <p>AI Assistant</p>
    </div>
    """,
    unsafe_allow_html=True
)
