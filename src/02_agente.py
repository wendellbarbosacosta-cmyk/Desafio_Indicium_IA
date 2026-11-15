import os
import logging
import time
import sqlite3
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Modo sem janela para rodar em threads
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from langchain_community.tools import QuerySQLDatabaseTool, DuckDuckGoSearchRun
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage, HumanMessage

# 1. GOVERNANÇA: Configuração limpa do Logging
os.makedirs('../docs', exist_ok=True)
logging.basicConfig(
    filename='../docs/agent_audit.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

load_dotenv()

# 2. FERRAMENTA 3: Geração Automatizada dos Gráficos Obrigatórios
@tool
def gerar_graficos_srag() -> str:
    """Gera os dois gráficos obrigatórios de SRAG (casos diários nos últimos 30 dias e casos mensais nos últimos 12 meses) a partir do banco SQLite e salva na pasta docs."""
    logging.info("Acionando ferramenta de geração de gráficos...")
    try:
        conn = sqlite3.connect("../data/srag_dados.db")
        df = pd.read_sql_query("SELECT DT_NOTIFIC FROM srag_info", conn)
        conn.close()

        df['DT_NOTIFIC'] = pd.to_datetime(df['DT_NOTIFIC'], errors='coerce')
        df = df.dropna(subset=['DT_NOTIFIC'])
        data_max = df['DT_NOTIFIC'].max()

        # Gráfico 1: Número diário de casos dos últimos 30 dias
        corte_30d = data_max - pd.Timedelta(days=30)
        df_30d = df[df['DT_NOTIFIC'] > corte_30d]
        diario = df_30d.groupby(df_30d['DT_NOTIFIC'].dt.date).size()

        plt.figure(figsize=(10, 5))
        plt.plot(diario.index, diario.values, marker='o', color='#005b96', linewidth=2)
        plt.title('Número Diário de Casos de SRAG (Últimos 30 Dias)', fontsize=13, fontweight='bold')
        plt.xlabel('Data da Notificação')
        plt.ylabel('Quantidade de Casos')
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        caminho_g1 = '../docs/grafico_diario_30d.png'
        plt.savefig(caminho_g1, dpi=150)
        plt.close()

        # Gráfico 2: Número mensal de casos dos últimos 12 meses
        df['ANO_MES'] = df['DT_NOTIFIC'].dt.to_period('M').astype(str)
        mensal = df.groupby('ANO_MES').size().tail(12)

        plt.figure(figsize=(10, 5))
        barras = plt.bar(mensal.index, mensal.values, color='#2a9d8f', edgecolor='black')
        plt.title('Número Mensal de Casos de SRAG (Últimos 12 Meses)', fontsize=13, fontweight='bold')
        plt.xlabel('Mês/Ano')
        plt.ylabel('Quantidade de Casos')
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.6)
        for barra in barras:
            yval = barra.get_height()
            plt.text(barra.get_x() + barra.get_width()/2.0, yval, int(yval), va='bottom', ha='center', fontsize=9)
        plt.tight_layout()
        caminho_g2 = '../docs/grafico_mensal_12m.png'
        plt.savefig(caminho_g2, dpi=150)
        plt.close()

        logging.info("Gráficos gerados com sucesso em ../docs/")
        return (
            "Gráficos gerados com sucesso! "
            "Arquivos salvos: 'grafico_diario_30d.png' e 'grafico_mensal_12m.png'. "
            "Inclua-os no relatório Markdown usando exatamente a sintaxe: "
            "![Casos Diários - Últimos 30 Dias](grafico_diario_30d.png) e "
            "![Casos Mensais - Últimos 12 Meses](grafico_mensal_12m.png)"
        )
    except Exception as e:
        logging.error(f"Erro ao gerar gráficos: {e}")
        return f"Erro ao gerar gráficos: {e}"

def criar_agente():
    logging.info("Inicializando o Agente e conectando ao banco de dados SQLite...")
    
    # FERRAMENTA 1: Banco de Dados
    db = SQLDatabase.from_uri("sqlite:///../data/srag_dados.db")
    sql_tool = QuerySQLDatabaseTool(db=db)
    sql_tool.name = "consultar_banco_srag"
    sql_tool.description = (
        "Use esta ferramenta para executar consultas SQL (APENAS SELECT) na tabela 'srag_info'. "
        "Colunas disponíveis: DT_NOTIFIC (timestamp), EVOLUCAO (1.0=Cura, 2.0=Óbito por SRAG, 3.0=Óbito outras causas, 9.0=Ignorado), "
        "UTI (1.0=Sim, 2.0=Não, 9.0=Ignorado), VACINA_COV (1.0=Sim, 2.0=Não, 9.0=Ignorado), "
        "VACINA (1.0=Sim, 2.0=Não, 9.0=Ignorado), SG_UF_NOT, NU_IDADE_N."
    )

    # FERRAMENTA 2: Busca na Web
    search_tool = DuckDuckGoSearchRun()
    search_tool.name = "buscar_noticias_srag"
    search_tool.description = "Use esta ferramenta para buscar notícias recentes no Brasil sobre SRAG, covid-19, influenza e surtos respiratórios."

    tools = [sql_tool, search_tool, gerar_graficos_srag]

    # LLM: Configuração do modelo
    llm = ChatGoogleGenerativeAI(model="gemini-3.8-flash", temperature=0.2)

    # ARQUITETURA LANGGRAPH
    agente = create_react_agent(llm, tools)
    
    logging.info("Agente instanciado com sucesso.")
    return agente

def salvar_relatorio_md(conteudo, nome_arquivo="relatorio_teste_srag.md"):
    # Caso o modelo retorne uma lista de blocos (formato multimodal), extrai apenas o texto
    if isinstance(conteudo, list):
        textos = [bloco.get("text", "") for bloco in conteudo if isinstance(bloco, dict) and "text" in bloco]
        conteudo = "\n".join(textos)
        
    caminho = f"../docs/{nome_arquivo}"
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print(f"\n[SUCESSO] Relatório Markdown salvo em: {caminho}")
    logging.info(f"Relatório Markdown gerado e salvo em {caminho}")

if __name__ == "__main__":
    print("Iniciando a construção do Agente...")
    agente_srag = criar_agente()
    print("Agente pronto! Ele tem acesso ao banco SQL, busca web e gerador de gráficos.")
    
    system_prompt = """Você é um Engenheiro de IA e Analista de Dados Sênior da Indicium HealthCare.
    Sua missão é gerar um Relatório Automatizado de Inteligência Epidemiológica sobre SRAG.
    
    DIRETRIZES DE EXECUÇÃO E FORMATAÇÃO:
    1. EFICIÊNCIA SQL: Faça uma ÚNICA consulta SQL otimizada na tabela 'srag_info' para extrair todas as 4 métricas obrigatórias:
       - Taxa de aumento de casos (compare o volume dos últimos 30 dias com os 30 dias imediatamente anteriores usando a coluna DT_NOTIFIC).
       - Taxa de mortalidade (proporção de EVOLUCAO = 2.0 sobre o total geral e sobre os casos com desfecho válido EVOLUCAO IN (1.0, 2.0, 3.0)).
       - Taxa de ocupação de UTI (proporção de UTI = 1.0 sobre o total geral e sobre os casos válidos UTI IN (1.0, 2.0)).
       - Taxa de vacinação da população (proporção de pacientes vacinados contra Covid-19 [VACINA_COV = 1.0] e Gripe [VACINA = 1.0]).
    2. GRÁFICOS OBRIGATÓRIOS: Chame obrigatoriamente a ferramenta 'gerar_graficos_srag' e insira os links Markdown das duas imagens geradas (`![Casos Diários](grafico_diario_30d.png)` e `![Casos Mensais](grafico_mensal_12m.png)`) em uma seção de Evolução Temporal no relatório.
    3. CONTEXTO EM TEMPO REAL: Use 'buscar_noticias_srag' para buscar notícias e diretrizes recentes sobre SRAG no Brasil para embasar os números.
    4. ESTRUTURA EXECUTIVA: Use cabeçalhos (## e ###), apresente as 4 métricas em uma Tabela Markdown consolidada e explique o significado clínico e epidemiológico de cada métrica.

    GUARDRAILS (REGRAS ESTRITAS DE COMPORTAMENTO):
    1. ESCOPO: Responda APENAS sobre saúde, epidemiologia (SRAG, Covid-19, Influenza) e dados hospitalares.
    2. SEGURANÇA SQL: Utilize APENAS comandos SELECT. Nunca execute UPDATE, DELETE, DROP ou INSERT.
    3. PRIVACIDADE E DADOS SENSÍVEIS: Nunca exponha dados individuais de pacientes; reporte apenas agregações estatísticas.
    4. EXPLICABILIDADE: Toda métrica e gráfico deve conter comentários analíticos claros sobre o cenário atual.
    """
    
    pergunta_relatorio = (
        "Gere o relatório completo da PoC Indicium HealthCare contendo: "
        "1) As 4 métricas obrigatórias extraídas do banco de dados (taxa de aumento de casos, taxa de mortalidade, taxa de ocupação de UTI e taxa de vacinação da população); "
        "2) A geração e inclusão dos dois gráficos obrigatórios (diário dos últimos 30 dias e mensal dos últimos 12 meses); "
        "3) Contextualização com notícias e diretrizes recentes sobre SRAG buscadas na internet."
    )

    teste = {
        "messages": [
            SystemMessage(content=system_prompt),
            HumanMessage(content=pergunta_relatorio)
        ]
    }
    
    max_tentativas = 5
    espera_inicial = 30
    
    for tentativa in range(1, max_tentativas + 1):
        try:
            print(f"\nTentativa {tentativa} de {max_tentativas}...")
            resposta = agente_srag.invoke(teste)
            
            print("\n--- PASSO A PASSO DO AGENTE (RACIOCÍNIO) ---")
            for mensagem in resposta['messages']:
                mensagem.pretty_print()
            
            texto_final = resposta['messages'][-1].content
            salvar_relatorio_md(texto_final)
            break
        except Exception as e:
            print(f"Erro na tentativa {tentativa}: {e}")
            if tentativa < max_tentativas:
                print(f"Aguardando {espera_inicial} segundos antes de tentar novamente...")
                time.sleep(espera_inicial)
                espera_inicial *= 2
            else:
                print("\nTodas as tentativas falharam devido à instabilidade do servidor ou cota esgotada.")