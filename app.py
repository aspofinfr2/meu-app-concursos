import streamlit as st
import json
import os

# --- FUNÇÕES DE PERSISTÊNCIA (PARA NÃO PERDER OS DADOS) ---
def carregar_dados():
    if os.path.exists("dados_estudos.json"):
        try:
            with open("dados_estudos.json", "r") as f:
                dados_existentes = json.load(f)
            
            materias_desejadas = [
                "Direito Penal", 
                "Direito Administrativo", 
                "Português",
                "Direito Processual Penal",
                "Direitos Humanos",
                "Matemática",
                "Legislação Aplicada à PMERJ"
            ]
            
            for mat in materias_desejadas:
                if mat not in dados_existentes:
                    dados_existentes[mat] = {"acertos": 0, "erros": 0, "ultimo_backup": None}
            
            return dados_existentes
        except:
            pass

    return {
        "Direito Penal": {"acertos": 0, "erros": 0, "ultimo_backup": None},
        "Direito Administrativo": {"acertos": 0, "erros": 0, "ultimo_backup": None},
        "Português": {"acertos": 0, "erros": 0, "ultimo_backup": None},
        "Direito Processual Penal": {"acertos": 0, "erros": 0, "ultimo_backup": None},
        "Direitos Humanos": {"acertos": 0, "erros": 0, "ultimo_backup": None},
        "Matemática": {"acertos": 0, "erros": 0, "ultimo_backup": None},
        "Legislação Aplicada à PMERJ": {"acertos": 0, "erros": 0, "ultimo_backup": None}
    }

def salvar_dados(dados):
    with open("dados_estudos.json", "w") as f:
        json.dump(dados, f)

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Meu App de Estudos", layout="centered")
dados = carregar_dados()

st.title("📚 Dashboard do Concurseiro PMERJ")
st.write("Acompanhe seu progresso acumulado por matéria com porcentagens de rendimento.")

# --- CRIAÇÃO DAS ABAS ---
materias = list(dados.keys())
abas = st.tabs(materias)

# --- LÓGICA DE CADA ABA ---
for i, nome_materia in enumerate(materias):
    if "ultimo_backup" not in dados[nome_materia]:
        dados[nome_materia]["ultimo_backup"] = None

    with abas[i]:
        st.header(nome_materia)
        
        # Coleta os dados históricos armazenados
        acc_acertos = dados[nome_materia]["acertos"]
        acc_erros = dados[nome_materia]["erros"]
        total_historico = acc_acertos + acc_erros
        
        # Cálculo da porcentagem específica da matéria
        if total_historico > 0:
            porcentagem_materia = (acc_acertos / total_historico) * 100
            texto_porcentagem = f"{porcentagem_materia:.2f}%"
        else:
            texto_porcentagem = "0.00%"
        
        # Painel Visual Superior Expandido (Agora com 4 colunas)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Acumulado", total_historico)
        col2.metric("Acertos Totais", acc_acertos)
        col3.metric("Erros Totais", acc_erros)
        col4.metric("Aproveitamento", texto_porcentagem)

        # Botão de Desfazer
        if dados[nome_materia]["ultimo_backup"] is not None:
            if st.button(f"↩️ Desfazer Última Alteração", key=f"undo_{i}"):
                dados[nome_materia]["acertos"] = dados[nome_materia]["ultimo_backup"]["acertos"]
                dados[nome_materia]["erros"] = dados[nome_materia]["ultimo_backup"]["erros"]
                dados[nome_materia]["ultimo_backup"] = None
                salvar_dados(dados)
                st.success("Última alteração desfeita com sucesso!")
                st.rerun()

        st.divider()

        # Formulário para adicionar NOVAS questões
        st.subheader("➕ Adicionar Novo Bloco")
        
        with st.form(key=f"form_{nome_materia}"):
            novo_total_bloco = st.number_input("Total de Questões Feitas", min_value=0, step=1, key=f"tot_{i}")
            novos_acertos = st.number_input("Quantidade de Acertos", min_value=0, step=1, key=f"ac_{i}")
            novos_erros = st.number_input("Quantidade de Erros", min_value=0, step=1, key=f"er_{i}")
            
            botao_salvar = st.form_submit_button("Atualizar Histórico")
            
            if botao_salvar:
                if (novos_acertos + novos_erros) != novo_total_bloco:
                    st.error(f"Erro matemático! A soma de Acertos ({novos_acertos}) e Erros ({novos_erros}) deve ser exatamente igual ao Total de Questões ({novo_total_bloco}).")
                else:
                    dados[nome_materia]["ultimo_backup"] = {
                        "acertos": dados[nome_materia]["acertos"],
                        "erros": dados[nome_materia]["erros"]
                    }
                    
                    dados[nome_materia]["acertos"] += novos_acertos
                    dados[nome_materia]["erros"] += novos_erros
                    
                    salvar_dados(dados)
                    st.success(f"Dados de {nome_materia} atualizados!")
                    st.rerun()

# --- BARRA LATERAL COM RESUMO GERAL ---
st.sidebar.title("📈 Desempenho Global")
total_hits = sum(d["acertos"] for d in dados.values())
total_misses = sum(d["erros"] for d in dados.values())
total_geral_todas_materias = total_hits + total_misses

st.sidebar.write(f"**Total Geral Realizado:** {total_geral_todas_materias} questões")

# Adicionando a porcentagem global na barra lateral
if total_geral_todas_materias > 0:
    porcentagem_global = (total_hits / total_geral_todas_materias) * 100
    st.sidebar.metric(label="Aproveitamento Geral", value=f"{porcentagem_global:.2f}%")
    st.sidebar.progress(total_hits / total_geral_todas_materias)
else:
    st.sidebar.metric(label="Aproveitamento Geral", value="0.00%")