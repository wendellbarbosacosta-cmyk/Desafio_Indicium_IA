# 🏥 Agente de IA para Análise de Dados de SRAG - Desafio Indicium

Este projeto é uma solução de Inteligência Artificial baseada em **Agentes (Agentic AI)**, desenvolvida para o Desafio Indicium. O objetivo é fornecer uma interface de análise de dados automatizada sobre a Síndrome Respiratória Aguda Grave (SRAG), cruzando dados hospitalares estruturados com informações em tempo real da internet.

## 🧠 Arquitetura e Tecnologias

O projeto foi construído utilizando a arquitetura de grafos para agentes, garantindo um raciocínio lógico (ReAct) antes da execução de ferramentas.

- **Orquestração:** LangChain e LangGraph
- **LLM (Large Language Model):** Google Gemini (gemini-3.8-flash)
- **Banco de Dados:** SQLite (com base em dados públicos de SRAG)
- **Web Search:** DuckDuckGo Search API
- **Linguagem:** Python 3.10+

## 🛠️ Ferramentas do Agente

O agente foi dotado de duas ferramentas principais que ele decide, de forma autônoma, quando utilizar:
1. **`consultar_banco_srag` (SQL Tool):** Permite ao agente converter linguagem natural em queries SQL complexas (APENAS `SELECT`) para extrair métricas de casos, internações em UTI e evolução dos pacientes a partir do banco de dados local.
2. **`buscar_noticias_srag` (Web Tool):** Permite ao agente consultar a internet em tempo real para buscar notas técnicas, recomendações do Ministério da Saúde e notícias recentes.

## 🛡️ Governança e Guardrails

Para garantir a segurança e o tom executivo do assistente, foram implementados *Guardrails* rigorosos no `System Prompt`:
- **Foco Estrito (Escopo):** O agente recusa automaticamente responder a qualquer pergunta que fuja do tema de saúde, SRAG ou dados hospitalares.
- **Segurança SQL:** O agente está bloqueado para realizar operações destrutivas (`DROP`, `DELETE`, `UPDATE`, `INSERT`).
- **Explicabilidade:** Toda métrica extraída deve ser traduzida para o jargão de saúde pública, explicando o seu impacto assistencial.
- **Formatação Executiva:** Geração automática de relatórios finais em Markdown com tabelas organizadas e bullet points direcionados à tomada de decisão.

## 📁 Estrutura do Projeto

    Desafio_Indicium_IA/
    ├── data/
    │   ├── srag_dados.db         # Banco de dados SQLite com a tabela 'srag_info'
    │   └── Dicionario_de_Dados...# Dicionário de variáveis do Ministério da Saúde
    ├── docs/
    │   ├── agent_audit.log       # Log de execução e auditoria do agente
    │   └── relatorio_teste_srag.md # Output: Relatório gerado autonomamente pela IA
    ├── src/
    │   ├── 01_preparacao_dados.py# Script de ingestão do CSV para o SQLite
    │   └── 02_agente.py          # Script principal com a orquestração do LangGraph
    ├── .env                      # Variáveis de ambiente (Chave de API do Google)
    ├── requirements.txt          # Dependências do projeto
    └── README.md                 # Documentação

## 🚀 Como Executar

**1. Clone o repositório e instale as dependências:**
    
    git clone https://github.com/wendellbarbosacosta-cmyk/Desafio_Indicium_IA.git
    cd Desafio_Indicium_IA
    pip install -r requirements.txt

**2. Configure a Chave de API:**
Crie um arquivo `.env` na raiz do projeto e adicione a sua chave da Google Gemini API:
    
    GOOGLE_API_KEY="SUA_CHAVE_AQUI"

**3. Execute o Agente:**
    
    cd src
    python 02_agente.py

O agente demonstrará o seu raciocínio (passo a passo) no terminal e gerará o relatório formatado na pasta `docs/`.