import os  # Biblioteca para operações de sistema de arquivos
import whisper  # Biblioteca para transcrição de áudio com modelos de IA
import time  # Para pausas no código
# Para monitoramento do sistema de arquivos em tempo real
from watchdog.observers import Observer
# Para lidar com eventos de arquivos
from watchdog.events import FileSystemEventHandler
# Manipulação de vídeo e legendas
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import moviepy.config as config  # Configuração para MoviePy
# Funções para conexão com o banco de dados
from database import connect_db, close_connection

# Configurar o caminho do executável do ImageMagick para uso com MoviePy
config.change_settings(
    {"IMAGEMAGICK_BINARY": "C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"})

# Caminho da pasta onde os vídeos estão salvos
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
video_directory = os.path.join(base_dir, 'media', 'video')

# Criar pasta para salvar vídeos legendados, caso não exista
legendado_directory = os.path.join(base_dir, 'media', 'legendado')
os.makedirs(legendado_directory, exist_ok=True)

# Carregar o modelo Whisper para transcrição
modelo = whisper.load_model("base")


# Função para verificar se o vídeo já foi legendado
def is_video_legendado(video_path):
    connection = connect_db()
    if connection:
        cursor = connection.cursor()
        # Consultar o status de legendagem no banco de dados
        check_query = """
        SELECT status_legendagem FROM midias WHERE caminho_arquivo = %s
        """
        cursor.execute(check_query, (video_path,))
        result = cursor.fetchone()
        cursor.close()
        close_connection(connection)
        if result and result[0]:  # Se o resultado for True, já foi legendado
            return True
    return False


# Função para atualizar o status de legendagem e salvar transcrição no banco de dados
def atualizar_status_legendagem(video_path, transcricao_texto):
    connection = connect_db()
    if connection:
        cursor = connection.cursor()
        # Atualizar status de legendagem e transcrição no banco de dados
        update_query = """
        UPDATE midias 
        SET status_legendagem = TRUE, transcricao_video = %s 
        WHERE caminho_arquivo = %s
        """
        cursor.execute(update_query, (transcricao_texto, video_path))
        connection.commit()
        cursor.close()
        close_connection(connection)
        print(f"Status de legendagem e texto transcrito atualizado para {
              video_path}")


# Classe para lidar com eventos de criação de arquivos de vídeo
class VideoHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            # Monitorar novos diretórios recursivamente
            observer.schedule(VideoHandler(), event.src_path, recursive=True)
            print(f"Novo diretório detectado e monitorado: {event.src_path}")
        elif event.src_path.endswith(".mp4"):
            video_path = event.src_path
            print(f"Novo arquivo de vídeo detectado: {video_path}")

            # Verificar se o vídeo já foi legendado
            if is_video_legendado(video_path):
                print(f"Vídeo {video_path} já foi legendado anteriormente.")
                return  # Evita legendagem duplicada

            try:
                # Extrair o áudio do vídeo
                video = VideoFileClip(video_path)
                audio_filename = f"{os.path.splitext(video_path)[0]}_audio.wav"
                audio_path = os.path.join(video_directory, audio_filename)
                video.audio.write_audiofile(audio_path)

                # Transcrever o áudio usando Whisper
                resposta = modelo.transcribe(audio_path)
                texto_transcricao_video = resposta['text']

                # Salvar transcrição no banco de dados
                atualizar_status_legendagem(
                    video_path, texto_transcricao_video)

                # Criar clipes de legendas com timestamps
                segments = resposta.get('segments', [])
                if not segments:
                    print(f"Erro: Nenhuma transcrição detectada para o áudio {
                          audio_path}.")
                    return

                # Criação dos clipes de legenda para cada segmento de texto
                subtitle_clips = create_subtitle_clips(segments, video)

                # Combina o vídeo com as legendas
                video_with_subtitles = CompositeVideoClip(
                    [video] + subtitle_clips)

                # Salva o vídeo legendado
                video_output = f"{os.path.splitext(os.path.basename(video_path))[
                    0]}_legendado.mp4"
                video_output_path = os.path.join(
                    legendado_directory, video_output)
                video_with_subtitles.write_videofile(
                    video_output_path, codec='libx264', fps=24, audio_codec="aac")

                print(f"Vídeo legendado salvo em: {video_output_path}")
                video.close()

                # Atualizar o status de legendagem no banco de dados
                atualizar_status_legendagem(
                    video_path, texto_transcricao_video)

            except Exception as e:
                print(f"Erro ao processar o vídeo {video_path}: {e}")


# Função para criar clipes de legendas
def create_subtitle_clips(segments, video):
    clips = []
    for segment in segments:
        text = segment['text'].strip()
        start = segment['start']
        end = segment['end']

        if text:  # Evitar textos vazios
            txt_clip = TextClip(text, fontsize=24,
                                color='white', bg_color='black')
            txt_clip = txt_clip.set_pos(('center', 'bottom')).set_start(
                start).set_duration(end - start)
            clips.append(txt_clip)
    return clips


# Função para monitorar o diretório de vídeo em busca de novos arquivos
def monitor_video_directory():
    print(f"Monitorando o diretório de vídeos: {video_directory}")
    event_handler = VideoHandler()
    observer.schedule(event_handler, video_directory, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


# Instancia o Observer e inicia o monitoramento
observer = Observer()
if __name__ == '__main__':
    monitor_video_directory()
