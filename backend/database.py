import psycopg2
from contextlib import contextmanager


# Função para conectar ao banco de dados
def connect_db():
    try:
        connection = psycopg2.connect(
            host="localhost",  # Endereço do servidor
            database="aurora_db_3",  # Nome do banco de dados
            user="postgres",  # Seu usuário no PostgreSQL
            password="root1",  # Senha do PostgreSQL
            port="5435"  # Porta do PostgreSQL
        )
        return connection
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None


# Context manager para garantir que a conexão seja fechada corretamente
@contextmanager
def get_db_connection():
    connection = connect_db()
    try:
        if connection is not None:
            yield connection
        else:
            print("Falha ao obter conexão.")
    except Exception as e:
        print(f"Erro durante operação no banco de dados: {e}")
    finally:
        if connection:
            connection.close()


# Função para fechar a conexão (se for usada sem o context manager)
def close_connection(connection):
    if connection:
        connection.close()
