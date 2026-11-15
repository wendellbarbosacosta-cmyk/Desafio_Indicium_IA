# 🏥 Agente de IA para Análise de Dados de SRAG - Desafio Indicium

Este projeto é uma solução de Inteligência Artificial baseada em **Agentes (Agentic AI)**, desenvolvida para a Prova de Conceito (PoC) da Indicium HealthCare Inc. O objetivo é fornecer uma solução automatizada que consulte dados reais de internações por Síndrome Respiratória Aguda Grave (SRAG) do Open DATASUS, gere visualizações gráficas e cruze as métricas com notícias e diretrizes em tempo real para embasar a tomada de decisão clínica e epidemiológica.

## 🧠 Arquitetura e Tecnologias

O projeto utiliza uma arquitetura de grafos com o padrão **ReAct (Reasoning + Acting)**, permitindo que o Agente Orquestrador planeje e acione ferramentas de forma autônoma antes de sintetizar o relatório executivo. O diagrama conceitual detalhado encontra-se em `docs/diagrama_arquitetura_srag.pdf`.

- **Orquestração:** LangChain e LangGraph (`create_react_agent`)
- **LLM (Large Language Model):** Google Gemini (`gemini-3.8-flash`)
- **Banco de Dados:** SQLite (`srag_dados.db` a partir de dados do Open DATASUS)
- **Visualização de Dados:** Pandas e Matplotlib
- **Web Search:** DuckDuckGo Search API
- **Linguagem:** Python 3.10+

## 🛠️ Ferramentas do Agente (Tools)

O agente foi dotado de três ferramentas principais que ele decide, de forma autônoma, quando e como utilizar:
1. **`consultar_banco_srag` (SQL Tool):** Converte linguagem natural em queries SQL analíticas (restritas a `SELECT`) na tabela `srag_info` para calcular as 4 métricas obrigatórias:
   - **Taxa de aumento de casos** (comparativo de janelas móveis de 30 dias)
   - **Taxa de mortalidade** (proporção de óbitos por SRAG sobre o total e casos válidos)
   - **Taxa de ocupação de UTI** (proporção de internações intensivas)
   - **Taxa de vacinação da população** (cobertura vacinal de Covid-19 e Influenza nos casos notificados)
2. **`gerar_graficos_srag` (Custom Python Tool):** Conecta-se ao SQLite, processa as séries temporais e exporta automaticamente os dois gráficos exigidos em alta resolução para a pasta `docs/`:
   - Número diário de casos dos últimos 30 dias (`grafico_diario_30d.png`)
   - Número mensal de casos dos últimos 12 meses (`grafico_mensal_12m.png`)
3. **`buscar_noticias_srag` (Web Tool):** Consulta a internet em tempo real para buscar notas técnicas, alertas epidemiológicos e diretrizes vigentes do Ministério da Saúde.

## 🛡️ Governança, Guardrails e Tratamento de Dados Sensíveis

- **Anonimização e LGPD (`01_preparacao_dados.py`):** O dataset original do Open DATASUS (~100 colunas) passa por um pipeline de higienização prévia que descarta colunas identificáveis e retém exclusivamente variáveis analíticas (`DT_NOTIFIC`, `EVOLUCAO`, `UTI`, `VACINA_COV`, `VACINA`, `SG_UF_NOT`, `NU_IDADE_N`) referentes aos últimos 12 meses.
- **Auditoria e Transparência:** Todas as ações, chamadas de ferramentas e eventos do agente são registrados com carimbo de tempo em `docs/agent_audit.log`.
- **Guardrails de Escopo e Segurança SQL:** O `System Prompt` restringe o agente a responder apenas sobre saúde pública/epidemiologia e proíbe comandos DDL/DML (`DROP`, `DELETE`, `UPDATE`, `INSERT`).
- **Resiliência (Exponential Backoff):** Implementação de retentativas automáticas para contornar oscilações de rede ou limites de taxa da API (erros 429/503).

## 📁 Estrutura do Projeto

    Desafio_Indicium_IA/
    ├── data/
    │   ├── srag_dados.db                          # Banco SQLite higienizado com a tabela 'srag_info'
    │   └── Dicionario_de_Dados_SRAG_Hospitalizado # Dicionário oficial de variáveis do DATASUS
    ├── docs/
    │   ├── diagrama_arquitetura_srag.pdf          # PDF com o Diagrama Conceitual da Arquitetura
    │   ├── agent_audit.log                        # Log de auditoria e rastreabilidade do agente
    │   ├── grafico_diario_30d.png                 # Gráfico: Casos diários (últimos 30 dias)
    │   ├── grafico_mensal_12m.png                 # Gráfico: Casos mensais (últimos 12 meses)
    │   └── relatorio_teste_srag.md                # Output: Relatório executivo gerado pela IA
    ├── src/
    │   ├── 01_preparacao_dados.py                 # Script de limpeza, filtro temporal e carga SQLite
    │   └── 02_agente.py                           # Orquestrador LangGraph, Tools e Guardrails
    ├── .env                                       # Variáveis de ambiente (ignorado pelo Git)
    ├── .gitignore                                 # Filtro de arquivos sensíveis e CSV bruto (>100MB)
    ├── requirements.txt                           # Dependências do projeto
    └── README.md                                  # Documentação principal

## 🚀 Como Executar

**1. Clone o repositório e instale as dependências:**

    git clone https://github.com/wendellbarbosacosta-cmyk/Desafio_Indicium_IA.git
    cd Desafio_Indicium_IA
    pip install -r requirements.txt

**2. Configure a Chave de API:**
Crie um arquivo `.env` na raiz do projeto com a sua chave do Google Gemini:

    GOOGLE_API_KEY="SUA_CHAVE_AQUI"

**3. Execute o Agente:**

    cd src
    python 02_agente.py

O agente exibirá o passo a passo do seu raciocínio no terminal, salvará os gráficos `.png` e exportará o relatório completo em `docs/relatorio_teste_srag.md`.
