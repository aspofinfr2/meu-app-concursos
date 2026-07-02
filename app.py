import streamlit as st
import json

# --- CONFIGURAÇÃO INICIAL DAS MATÉRIAS ---
MATERIAS_PADRAO = [
    "Direito Penal", 
    "Direito Administrativo", 
    "Português",
    "Direito Processual Penal", 
    "Direitos Humanos", 
    "Matemática",
    "Legislação Aplicada à PMERJ"
]

st.set_page_config(page_title="Dashboard PMERJ", layout="centered")

# --- GERENCIAMENTO DE SESSÃO NATIIVA ---
if "dados_estudos" not in st.session_state:
    st.session_state.dados_estudos = {materia: {"acertos": 0, "erros": 0} for materia in MATERIAS_PADRAO}

dados = st.session_state.dados_estudos

# --- BARRA LATERAL: SISTEMA DE BACKUP INDIVIDUAL ---
st.sidebar.title("💾 Salvar/Carregar Progresso")
st.sidebar.write("Como o app não exige login, use os botões abaixo para nunca perder seus dados:")

# 1. Botão para exportar (Baixar os dados atuais)
dados_json_string = json.dumps(dados, ensure_ascii=False, indent=4)
st.sidebar.download_button(
    label="📥 Baixar Meu Progresso",
    data=dados_json_string,
    file_name="progresso_pmerj.json",
    mime="application/json",
    help="Clique aqui para salvar seu histórico no celular antes de fechar a aba."
)

st.sidebar.divider()

# 2. Upload para importar (Recuperar dados salvos)
arquivo_subido = st.sidebar.file_uploader(
    "📤 Carregar Meu Progresso", 
    type=["json"],
    help="Suba seu arquivo 'progresso_pmerj.json' aqui para recuperar suas questões."
)

if arquivo_subido is not None:
    try:
        dados_carregados = json.load(arquivo_subido)
        # Validação simples para garantir que o arquivo é o correto
        if isinstance(dados_carregados, dict) and any(m in dados_carregados for m in MATERIAS_PADRAO):
            st.session_state.dados_estudos = dados_carregados
            st.sidebar.success("Progresso carregado com sucesso!")
            # Evita loops recarregando os dados novos na tela
            dados = st.session_state.dados_estudos
        else:
            st.sidebar.error("Arquivo inválido.")
    except Exception as e:
        st.sidebar.error("Erro ao ler o arquivo.")

# --- TÍTULO PRINCIPAL ---
st.title("📚 Dashboard do Concurseiro PMERJ")
st.write("Acompanhe seu progresso de estudos por matéria.")

# --- CRIAÇÃO DAS ABAS ---
abas = st.tabs(MATERIAS_PADRAO)

# --- LÓGICA DE CADA ABA ---
for i, nome_materia in enumerate(MATERIAS_PADRAO):
    with abas[i]:
        st.header(nome_materia)
        
        if nome_materia not in dados:
            dados[nome_materia] = {"acertos": 0, "erros": 0}
            
        acc_acertos = dados[nome_materia].get("acertos", 0)
        acc_erros = dados[nome_materia].get("erros", 0)
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
                    st.error(f"Erro matemático! A soma de Acertos e Erros deve ser igual ao Total.")
                else:
                    st.session_state.dados_estudos[nome_materia]["acertos"] = acc_acertos + novos_acertos
                    st.session_state.dados_estudos[nome_materia]["erros"] = acc_erros + novos_erros
                    st.success(f"Dados de {nome_materia} atualizados na tela! Lembre-se de baixar seu progresso na barra lateral.")
                    st.rerun()

# --- BARRA LATERAL COM RESUMO GERAL ---
st.sidebar.divider()
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