from flask import Flask, render_template, jsonify, request, send_from_directory
import os  # Biblioteca para operações relacionadas ao sistema de arquivos
# Conexão com o banco de dados definida externamente
from database import get_db_connection
import numpy as np  # Biblioteca NumPy para manipulação de dados numéricos
import urllib.parse  # Para decodificar strings de URL

# Definir o caminho correto para as pastas de templates e arquivos estáticos do frontend
template_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'frontend', 'templates'))
static_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'frontend', 'static'))
media_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'media'))

# Inicializa o Flask com o caminho das pastas de templates e arquivos estáticos
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Função para buscar respostas no banco de dados e formatá-las para gráficos


def obter_dados_grafico(pergunta):
    with get_db_connection() as connection:
        cursor = connection.cursor()
        query = """
        SELECT resposta, COUNT(*) FROM respostas
        WHERE pergunta = %s
        GROUP BY resposta
        """
        cursor.execute(query, (pergunta,))
        results = cursor.fetchall()
        cursor.close()

        # Extrai as respostas e as contagens para construir o gráfico
        labels = [row[0] for row in results]
        data = [row[1] for row in results]

        return {'labels': labels, 'data': data}

# Função para buscar mídias e transcrições do banco de dados


def obter_midias():
    with get_db_connection() as connection:
        cursor = connection.cursor()
        query = """
        SELECT tipo_midia, caminho_arquivo, transcricao_audio, transcricao_video
        FROM midias
        """
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()

        midias = []
        for row in results:
            # Ajusta o caminho para relativo
            caminho_relativo = os.path.relpath(row[1], media_dir)
            midia = {
                'tipo': row[0],  # Tipo da mídia (áudio, imagem, vídeo)
                'caminho': caminho_relativo,  # Caminho relativo do arquivo
                # Transcrição de áudio, se disponível
                'transcricao_audio': row[2],
                # Transcrição de vídeo, se disponível
                'transcricao_video': row[3]
            }
            midias.append(midia)

        return midias

# Rota para fornecer dados de gráfico com base em uma pergunta


@app.route('/dados_grafico')
def dados_grafico():
    pergunta = request.args.get('pergunta')  # Obtém a pergunta da query string
    # Usa a função genérica para obter dados
    dados = obter_dados_grafico(pergunta)
    return jsonify(dados)

# Rota para renderizar um gráfico expandido com nomes de usuários associados às respostas


@app.route('/grafico_expandido')
def grafico_expandido():
    pergunta = request.args.get('pergunta')
    with get_db_connection() as connection:
        cursor = connection.cursor()
        query = """
        SELECT resposta, nome FROM respostas
        JOIN usuarios ON respostas.usuario_id = usuarios.id
        WHERE pergunta = %s
        """
        cursor.execute(query, (pergunta,))
        results = cursor.fetchall()
        cursor.close()

        labels = {}
        for resposta, nome in results:
            if resposta not in labels:
                labels[resposta] = []
            labels[resposta].append(nome)

        return render_template('grafico_expandido.html', pergunta=pergunta, labels=labels)

# Rota para listar os pacientes e retornar em formato JSON


@app.route('/api/pacientes')
def listar_pacientes():
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT id, nome FROM usuarios")
        patients = cursor.fetchall()
        cursor.close()
    return jsonify([{'id': p[0], 'nome': p[1]} for p in patients])

# Rota para renderizar o perfil de um paciente específico


@app.route('/paciente/<int:id>')
def perfil_paciente(id):
    with get_db_connection() as connection:
        cursor = connection.cursor()

        # Busca informações do paciente
        cursor.execute(
            "SELECT nome, usuario_id, data_registro, id FROM usuarios WHERE id = %s", (id,))
        patient = cursor.fetchone()

        # Busca as últimas 5 mensagens do paciente
        cursor.execute("""
            SELECT * FROM respostas
            WHERE usuario_id = %s
            ORDER BY data_resposta DESC
            LIMIT 5
        """, (id,))
        ultimas_mensagens = cursor.fetchall()

        # Busca a última conclusão de diagnóstico do paciente
        cursor.execute("""
            SELECT resposta FROM respostas
            WHERE usuario_id = %s AND pergunta = 'Diagnóstico'
            ORDER BY data_resposta DESC LIMIT 1
        """, (id,))
        ultima_conclusao = cursor.fetchone()

        cursor.close()

    return render_template('perfil_pacientes.html', patient=patient, ultimas_mensagens=ultimas_mensagens, ultima_conclusao=ultima_conclusao[0] if ultima_conclusao else None)

# Rota para buscar todas as mensagens de um paciente


@app.route('/paciente/mensagens-anteriores/<int:usuario_id>')
def mensagens_anteriores(usuario_id):
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT * FROM respostas
            WHERE usuario_id = %s
            ORDER BY data_resposta DESC
        """, (usuario_id,))
        mensagens = cursor.fetchall()
        cursor.close()

    return jsonify(mensagens)

# Rota para servir arquivos de mídia


@app.route('/media/<path:filename>')
def media(filename):
    return send_from_directory(media_dir, filename)

# Rota para fornecer as mídias em formato JSON


@app.route('/obter_midias')
def obter_midias_route():
    midias = obter_midias()
    return jsonify(midias)

# Rota para servir o arquivo index_graphic.html


@app.route('/graphics')
def graphics():
    return render_template('index_graphic.html')

# Rota para contar e retornar o número total de usuários


@app.route('/total_usuarios')
def total_usuarios():
    with get_db_connection() as conn:
        if conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM usuarios")
                total_usuarios = cursor.fetchone()[0]

    return jsonify({'totalUsuarios': total_usuarios})

# Rota principal que renderiza a página index.html


@app.route('/')
def index():
    return render_template('index.html')


# Inicializa o servidor Flask na porta 5001 para desenvolvimento
if __name__ == '__main__':
    app.run(debug=True, port=5001)
