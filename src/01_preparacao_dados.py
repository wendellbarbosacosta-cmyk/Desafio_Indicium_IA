import pandas as pd
import sqlite3
from datetime import datetime, timedelta

def preparar_banco_dados():
    print("Iniciando a leitura do CSV...")
    caminho_csv = 'data/dados_srag.csv'
    
    # 1. Carregar os dados brutos
    df = pd.read_csv(caminho_csv, sep=';', low_memory=False)
    
    # 2. SELEÇÃO DE COLUNAS E TRATAMENTO DE DADOS SENSÍVEIS
    # Selecionado apenas o necessário.
    colunas_interesse = [
        'DT_NOTIFIC',  # Data da notificação (Aumento de casos)
        'EVOLUCAO',    # Óbito ou Cura (Mortalidade)
        'UTI',         # Internação em UTI (Ocupação UTI)
        'VACINA_COV',  # Vacina Covid (Taxa de vacinação)
        'VACINA',      # Vacina Gripe (Taxa de vacinação)
        'SG_UF_NOT',   # Estado (Contexto geográfico)
        'NU_IDADE_N'   # Idade (Contexto demográfico)
    ]
    
    # Manter apenas as colunas que existem no CSV 
    colunas_presentes = [col for col in colunas_interesse if col in df.columns]
    df_limpo = df[colunas_presentes].copy()
    
    # 3. FILTRO DE TEMPO (Últimos 12 meses)
    print("Filtrando os últimos 12 meses...")
    df_limpo['DT_NOTIFIC'] = pd.to_datetime(df_limpo['DT_NOTIFIC'], errors='coerce')
    
    # Remover linhas com datas inválidas ou nulas
    df_limpo = df_limpo.dropna(subset=['DT_NOTIFIC'])
    
    # Descobrir a data mais recente no banco e subtrair 365 dias
    data_maxima = df_limpo['DT_NOTIFIC'].max()
    data_corte = data_maxima - timedelta(days=365)
    
    # Aplicar o filtro
    df_limpo = df_limpo[df_limpo['DT_NOTIFIC'] >= data_corte]
    
    # 4. SALVAR NO BANCO DE DADOS SQLITE
    print("Criando o banco de dados SQLite...")
    # CORREÇÃO AQUI: removido o '../' para salvar na mesma pasta do CSV
    caminho_db = 'data/srag_dados.db'
    conexao = sqlite3.connect(caminho_db)
    
    # Salvar o dataframe como uma tabela chamada 'srag_info'
    df_limpo.to_sql('srag_info', conexao, if_exists='replace', index=False)
    conexao.close()
    
    print(f"Pronto! Banco de dados criado em: {caminho_db}")
    print(f"Total de registros mantidos (últimos 12 meses): {len(df_limpo)}")

if __name__ == "__main__":
    preparar_banco_dados()