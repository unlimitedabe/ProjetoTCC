import psycopg2
from contextlib import contextmanager


# Função para conectar ao banco de dados
def connect_db():
    try:
        connection = psycopg2.connect(
            host="seu_host",  # Endereço do servidor
            database="seu_database",  # Nome do banco de dados
            user="seu_user",  # Seu usuário no PostgreSQL
            password="sua_senha",  # Senha do PostgreSQL
            port="sua_porta"  # Porta do PostgreSQL
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
