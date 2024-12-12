from flask import Flask, render_template, jsonify, session, request, send_from_directory, abort, send_file
import secrets
import os  # Biblioteca para operações relacionadas ao sistema de arquivos
# Conexão com o banco de dados definida externamente
from database import get_db_connection
import numpy as np  # Biblioteca NumPy para manipulação de dados numéricos
import urllib.parse  # Para decodificar strings de URL
from flask_talisman import Talisman
import pandas as pd

# Definir o caminho correto para as pastas de templates e arquivos estáticos do frontend
template_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'frontend', 'templates'))
static_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'frontend', 'static'))
media_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'media'))

# Inicializa o Flask com o caminho das pastas de templates e arquivos estáticos
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Aplica configurações de cabeçalhos de segurança
Talisman(app, content_security_policy={
    # Recursos do próprio domínio
    'default-src': "'self'",
    # Permitir scripts do domínio e CDN
    'script-src': "'self' 'unsafe-inline' https://cdn.jsdelivr.net",
    'style-src': "'self' 'unsafe-inline'",              # Permitir estilos inline
    # Permitir imagens do domínio e base64
    'img-src': "'self' data:'",
    # Permitir conexões com APIs externas
    'connect-src': "'self' https://api.exemplo.com"
})


@app.before_request
def csrf_protect():
    if request.method == "POST":
        token = session.get("csrf_token")
        request_token = request.headers.get("X-CSRF-Token")
        if not token or not request_token or token != request_token:
            abort(403)


@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'GET':
        # Gera um token CSRF para a sessão
        session['csrf_token'] = secrets.token_hex(16)
        return render_template('form.html', csrf_token=session['csrf_token'])
    # Processa requisição POST
    return 'Formulário enviado com sucesso'


@app.route('/processar_dados', methods=['POST'])
def processar_dados():
    user_input = request.json.get('input')
    if not user_input.isalnum():
        return jsonify({'error': 'Entrada inválida'}), 400
    # Processar dado válido
    return jsonify({'message': 'Entrada processada com sucesso'})


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
        SELECT tipo_midia, caminho_arquivo, transcricao_audio, transcricao_video, status_legendagem
        FROM midias
        """
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()

        midias = []
        for row in results:
            tipo_midia, caminho_arquivo, transcricao_audio, transcricao_video, status_legendagem = row

            if tipo_midia == 'video' and status_legendagem:
                # Substituir caminho para o vídeo legendado
                caminho_arquivo = os.path.join('legendado', os.path.basename(
                    caminho_arquivo).replace('.mp4', '_legendado.mp4'))
            else:
                # Ajustar caminho relativo para outros tipos de mídia
                caminho_arquivo = os.path.relpath(caminho_arquivo, media_dir)

            midia = {
                'tipo': tipo_midia,
                'caminho': caminho_arquivo,  # Caminho atualizado
                'transcricao_audio': transcricao_audio,
                'transcricao_video': transcricao_video
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
        query = "SELECT id, nome FROM usuarios"
        cursor.execute(query)  # Sem parâmetros
        patients = cursor.fetchall()
        cursor.close()
    return jsonify([{'id': p[0], 'nome': p[1]} for p in patients])


# Rota para renderizar o perfil de um paciente específico
@app.route('/paciente/<int:id>')
def perfil_paciente(id):
    with get_db_connection() as connection:
        cursor = connection.cursor()

        # Buscar informações do paciente
        query_patient = """
        SELECT nome, usuario_id, data_registro, id 
        FROM usuarios 
        WHERE id = %s
        """
        cursor.execute(query_patient, (id,))
        patient = cursor.fetchone()

        # Buscar as últimas 5 mensagens do paciente
        query_messages = """
        SELECT * FROM respostas
        WHERE usuario_id = %s
        ORDER BY data_resposta DESC
        LIMIT 5
        """
        cursor.execute(query_messages, (id,))
        ultimas_mensagens = cursor.fetchall()

        # Buscar a última conclusão de diagnóstico do paciente
        query_diagnosis = """
        SELECT resposta 
        FROM respostas
        WHERE usuario_id = %s AND pergunta = 'Diagnóstico'
        ORDER BY data_resposta DESC
        LIMIT 1
        """
        cursor.execute(query_diagnosis, (id,))
        ultima_conclusao = cursor.fetchone()
        cursor.close()

    return render_template(
        'perfil_pacientes.html',
        patient=patient,
        ultimas_mensagens=ultimas_mensagens,
        ultima_conclusao=ultima_conclusao[0] if ultima_conclusao else None
    )


# Rota para buscar todas as mensagens de um paciente
@app.route('/paciente/mensagens-anteriores/<int:usuario_id>')
def mensagens_anteriores(usuario_id):
    with get_db_connection() as connection:
        cursor = connection.cursor()
        query = """
        SELECT * FROM respostas
        WHERE usuario_id = %s
        ORDER BY data_resposta DESC
        """
        cursor.execute(query, (usuario_id,))
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


# Rota para retornar os dados da tabela resposta
@app.route('/export/respostas_excel', methods=['GET'])
def export_excel():
    with get_db_connection() as connection:
        if connection:
            try:
                # Query para pegar os dados da tabela respostas
                query = "SELECT * FROM respostas"
                df = pd.read_sql_query(query, connection)

                # Cria um arquivo Excel temporário
                file_path = "respostas_export.xlsx"
                df.to_excel(file_path, index=False)

                # Envia o arquivo para download
                return send_file(file_path, as_attachment=True)
            except Exception as e:
                return {"error": f"Erro ao exportar: {e}"}, 500


# Rota para retornar os dados da tabela usuarios
@app.route('/export/usuarios_excel', methods=['GET'])
def export_usuarios():
    with get_db_connection() as connection:
        if connection:
            try:
                # Query para pegar os dados da tabela usuarios
                query = "SELECT * FROM usuarios"
                df = pd.read_sql_query(query, connection)

                # Cria um arquivo Excel temporário
                file_path = "usuarios_export.xlsx"
                df.to_excel(file_path, index=False)

                # Envia o arquivo para download
                return send_file(file_path, as_attachment=True)
            except Exception as e:
                return {"error": f"Erro ao exportar: {e}"}, 500


# Rota principal que renderiza a página index.html
@app.route('/')
def index():
    return render_template('index.html')


# Inicializa o servidor Flask na porta 5001 para desenvolvimento
if __name__ == '__main__':
    app.run(debug=True, port=5001)
