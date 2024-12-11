import os  # Biblioteca para operações de sistema de arquivos
import whisper  # Biblioteca para transcrição de áudio usando modelos de IA
import time  # Para pausar o código
# Para monitorar o sistema de arquivos em tempo real
from watchdog.observers import Observer
# Para lidar com eventos no sistema de arquivos
from watchdog.events import FileSystemEventHandler
# Funções para conexão com o banco de dados
from database import connect_db, close_connection

# Caminho da pasta onde os áudios estão salvos
base_dir = os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))  # Caminho até /ProjetoTCC
audio_directory = os.path.join(base_dir, 'media', 'audio')

# Criar pasta para salvar transcrições, se não existir
transcription_directory = os.path.join(base_dir, 'media', 'transcricao')
os.makedirs(transcription_directory, exist_ok=True)

# Carregar o modelo Whisper para transcrição de áudio
modelo = whisper.load_model("base")

# Função para verificar se o áudio já foi transcrito, usando uma flag no banco de dados


def is_audio_transcrito(audio_path):
    connection = connect_db()
    if connection:
        cursor = connection.cursor()
        # Consultar o status de transcrição no banco de dados
        check_query = """
        SELECT status_transcricao FROM midias WHERE caminho_arquivo = %s
        """
        cursor.execute(check_query, (audio_path,))
        result = cursor.fetchone()
        cursor.close()
        close_connection(connection)
        if result and result[0]:  # Se o resultado for True, já foi transcrito
            return True
    return False

# Função para atualizar o status de transcrição no banco e salvar a transcrição


def atualizar_status_transcricao(audio_path, transcricao_texto):
    connection = connect_db()
    if connection:
        cursor = connection.cursor()
        # Atualizar status e texto de transcrição no banco de dados
        update_query = """
        UPDATE midias 
        SET status_transcricao = TRUE, transcricao_audio = %s 
        WHERE caminho_arquivo = %s
        """
        cursor.execute(update_query, (transcricao_texto, audio_path))
        connection.commit()
        cursor.close()
        close_connection(connection)
        print(f"Status de transcrição e texto transcrito atualizado para {
              audio_path}")

# Classe para lidar com eventos de criação de arquivos no diretório de áudio


class AudioHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            # Caso um novo diretório seja criado, monitorá-lo recursivamente
            observer.schedule(AudioHandler(), event.src_path, recursive=True)
            print(f"Novo diretório detectado e monitorado: {event.src_path}")
        elif event.src_path.endswith(".wav") or event.src_path.endswith(".ogg"):
            audio_path = event.src_path
            print(f"Novo arquivo de áudio detectado: {audio_path}")

            # Verificar se o áudio já foi transcrito
            if is_audio_transcrito(audio_path):
                print(f"Áudio {audio_path} já foi transcrito anteriormente.")
                return  # Evita retranscrever

            try:
                # Fazer a transcrição usando o modelo Whisper
                resposta = modelo.transcribe(audio_path)

                # Imprimir a transcrição no terminal
                print("Transcrição:")
                print(resposta['text'])

                # Obter o texto da transcrição
                texto_transcricao = resposta['text']

                # Salvar a transcrição no banco de dados
                atualizar_status_transcricao(audio_path, texto_transcricao)

                # Salvar a transcrição em um arquivo .txt na pasta de transcrições
                transcricao_filename = f"{os.path.splitext(
                    os.path.basename(audio_path))[0]}.txt"
                transcricao_path = os.path.join(
                    transcription_directory, transcricao_filename)

                with open(transcricao_path, 'w', encoding='utf-8') as f:
                    f.write(resposta['text'])
                print(f"Transcrição salva em: {transcricao_path}")

            except Exception as e:
                print(f"Erro ao transcrever o áudio {audio_path}: {e}")

# Função para monitorar o diretório de áudio em busca de novos arquivos


def monitor_audio_directory():
    print(f"Monitorando o diretório de áudio: {audio_directory}")
    event_handler = AudioHandler()
    observer.schedule(event_handler, audio_directory, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)  # Mantém o monitoramento em execução
    except KeyboardInterrupt:
        observer.stop()  # Para o monitoramento ao interromper o programa
    observer.join()


# Instancia o Observer e inicia o monitoramento
observer = Observer()
if __name__ == '__main__':
    monitor_audio_directory()
