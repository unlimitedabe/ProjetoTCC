import subprocess  # Biblioteca para criar e gerenciar subprocessos
import os  # Biblioteca para operações relacionadas ao sistema de arquivos

# Defina o caminho para os seus scripts
bot_script = os.path.join("bot.py")  # Script principal do bot
# Script para transcrição de áudio
transcricao_script = os.path.join("transcricao.py")
# Script para legendagem de vídeos
legendagem_script = os.path.join("legendagem.py")
# Script para API (gerenciamento de dados e rotas)
api_script = os.path.join("api.py")


def run_script(script_path):
    """Função para rodar um script em um subprocesso."""
    # Cria um subprocesso para executar o script em Python
    return subprocess.Popen(["python", script_path])


def main():
    print("Iniciando todos os processos...")

    # Inicia bot.py
    bot_process = run_script(bot_script)
    print("Bot rodando...")

    # Inicia transcricao.py
    transcricao_process = run_script(transcricao_script)
    print("Transcrição rodando...")

    # Inicia legendagem.py
    legendagem_process = run_script(legendagem_script)
    print("Legendagem rodando...")

    # Inicia api.py
    api_process = run_script(api_script)
    print("API rodando...")

    try:
        # Mantém o aplicativo rodando enquanto os subprocessos estão ativos
        bot_process.wait()
        transcricao_process.wait()
        legendagem_process.wait()
        api_process.wait()

    except KeyboardInterrupt:
        # Se o programa for interrompido com Ctrl+C, encerra todos os subprocessos
        print("\nEncerrando todos os processos...")
        bot_process.terminate()
        transcricao_process.terminate()
        legendagem_process.terminate()
        api_process.terminate()


if __name__ == '__main__':
    main()  # Executa a função main se o script for executado diretamente
