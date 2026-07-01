import streamlit as st
import json
from streamlit_local_storage import LocalStorage

# Inicializa o gerenciador de armazenamento do navegador
local_storage = LocalStorage()

# Lista de matérias do concurso PMERJ
MATERIAS_PADRAO = [
    "Direito Penal", 
    "Direito Administrativo", 
    "Português",
    "Direito Processual Penal", 
    "Direitos Humanos", 
    "Matemática",
    "Legislação Aplicada à PMERJ"
]

# Chave usada para salvar no navegador do cliente
CHAVE_STORAGE = "progresso_pmerj_app"

# 1. Tenta buscar os dados salvos no navegador do usuário (usando getItem)
dados_salvos_string = local_storage.getItem(CHAVE_STORAGE)

# 2. Se encontrar os dados no navegador dele, carrega. Se não, começa zerado.
if dados_salvos_string:
    try:
        dados = json.loads(dados_salvos_string)
    except:
        dados = {materia: {"acertos": 0, "erros": 0} for materia in MATERIAS_PADRAO}
else:
    dados = {materia: {"acertos": 0, "erros": 0} for materia in MATERIAS_PADRAO}

# --- TITULO PRINCIPAL ---
st.title("📚 Dashboard do Concurseiro PMERJ")
st.write("Acompanhe seu progresso por matéria com porcentagens de rendimento de forma individual.")

# --- CRIAÇÃO DAS ABAS ---
abas = st.tabs(MATERIAS_PADRAO)

# --- LÓGICA DE CADA ABA ---
for i, nome_materia in enumerate(MATERIAS_PADRAO):
    with abas[i]:
        st.header(nome_materia)
        
        if nome_materia not in dados:
            dados[nome_materia] = {"acertos": 0, "erros": 0}
            
        acc_acertos = dados[nome_materia]["acertos"]
        acc_erros = dados[nome_materia]["erros"]
        total_historico = acc_acertos + acc_erros
        
        if total_historico > 0:
            porcentagem_materia = (acc_acertos / total_historico) * 100
            texto_porcentagem = f"{porcentagem_materia:.2f}%"
        else:
            texto_porcentagem = "0.00%"
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Acumulado", total_historico)
        col2.metric("Acertos Totais", acc_acertos)
        col3.metric("Erros Totais", acc_erros)
        col4.metric("Aproveitamento", texto_porcentagem)

        st.divider()

        st.subheader("➕ Adicionar Novo Bloco")
        
        with st.form(key=f"form_{nome_materia}"):
            novo_total_bloco = st.number_input("Total de Questões Feitas", min_value=0, step=1, key=f"tot_{i}")
            novos_acertos = st.number_input("Quantidade de Acertos", min_value=0, step=1, key=f"ac_{i}")
            novos_erros = st.number_input("Quantidade de Erros", min_value=0, step=1, key=f"er_{i}")
            
            botao_salvar = st.form_submit_button("Atualizar Histórico")
            
            if botao_salvar:
                if (novos_acertos + novos_erros) != novo_total_bloco:
                    st.error(f"Erro matemático! A soma de Acertos ({novos_acertos}) e Erros ({novos_erros}) deve ser igual ao Total ({novo_total_bloco}).")
                else:
                    # Atualiza a estrutura de dados local
                    dados[nome_materia]["acertos"] += novos_acertos
                    dados[nome_materia]["erros"] += novos_erros
                    
                    # Salva a nova versão direto no navegador do cliente (usando setItem)
                    local_storage.setItem(CHAVE_STORAGE, json.dumps(dados))
                    
                    st.success(f"Dados de {nome_materia} atualizados com sucesso!")
                    st.rerun()

# --- BARRA LATERAL COM RESUMO GERAL ---
st.sidebar.title("📈 Desempenho Global")
total_hits = sum(d.get("acertos", 0) for d in dados.values())
total_misses = sum(d.get("erros", 0) for d in dados.values())
total_geral_todas_materias = total_hits + total_misses

st.sidebar.write(f"**Total Geral Realizado:** {total_geral_todas_materias} questões")

if total_geral_todas_materias > 0:
    porcentagem_global = (total_hits / total_geral_todas_materias) * 100
    st.sidebar.metric(label="Aproveitamento Geral", value=f"{porcentagem_global:.2f}%")
    st.sidebar.progress(total_hits / total_geral_todas_materias)
else:
    st.sidebar.metric(label="Aproveitamento Geral", value="0.00%")

st.sidebar.divider()

if st.sidebar.button("🗑️ Resetar Todo o Histórico"):
    dados_zerados = {materia: {"acertos": 0, "erros": 0} for materia in MATERIAS_PADRAO}
    local_storage.setItem(CHAVE_STORAGE, json.dumps(dados_zerados))
    st.rerun()