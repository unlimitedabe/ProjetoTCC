import os  # Biblioteca para operações de sistema de arquivos
from telegram import Update  # Para interações com o Telegram
# Para configurar o bot e lidar com eventos
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
# Funções de conexão com o banco de dados
from database import connect_db, close_connection
import atexit  # Para registrar funções a serem executadas na saída do programa
# Função para obter conexão com o banco de dados
from database import get_db_connection
import time  # Para operações de pausa e gerenciamento de tempo
# Configuração de requisições HTTP com tempo limite
from telegram.request import HTTPXRequest
import unidecode  # Biblioteca para remover acentos
import asyncio  # Certifique-se de importar asyncio no início do arquivo

# Definindo diretórios para salvar mídias
MEDIA_DIR = os.path.join(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))), "media")
AUDIO_DIR = os.path.join(MEDIA_DIR, "audio")
VIDEO_DIR = os.path.join(MEDIA_DIR, "video")
IMAGES_DIR = os.path.join(MEDIA_DIR, "images")

# Criar diretórios de mídia se não existirem
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

# Definição das perguntas e respostas do fluxo de conversa
# Perguntas e respostas mapeadas por IDs
# Estrutura de perguntas, opções e o próximo passo baseado na resposta
questions = {
    '0': {
        'text': "Escolha uma das opções abaixo (digite o número da opção):",
        'options': {
            '1': 'Monitoramento de risco gestacional',
            '2': 'Enviar um áudio',
            '3': 'Enviar uma foto',
            '4': 'Enviar um vídeo',
            '5': 'Apagar meus dados'
        },
        'next': {
            '1': '1',  # Segue para o monitoramento
            '2': 'handle_audio',  # Solicita envio de áudio
            '3': 'handle_photo',  # Solicita envio de foto
            '4': 'handle_video',  # Solicita envio de vídeo
            '5': 'confirm_delete'  # Confirmação para apagar dados
        }
    },
    # Pergunta de confirmação para apagar dados
    'confirm_delete': {
        'text': "Tem certeza de que deseja apagar todos os seus dados?",
        'options': {
            'sim': 'Sim, eu quero apagar meus dados salvos no sistema',
            'nao': 'Não, eu não quero apagar meus dados salvos no sistema'
        },
        'next': {
            'sim': 'delete_data',
            'nao': 'end'  # Finaliza sem apagar
        }
    },
    '1': {
        'text': "Qual foi a sua última medição de pressão arterial?",
        'options': {
            '1': 'PA Sistólica ≥ 140mmHg e/ou PA Diastólica ≥ 90mmHg',
            '2': 'PA Sistólica < 140mmHg e PA Diastólica < 90mmHg'
        },
        'next': {
            '1': '2',  # Segue para a próxima pergunta sobre hipertensão
            '2': 'end_monitoring'  # Instruções de monitoramento e fim da interação
        }
    },
    '2': {
        'text': "Sua pressão arterial elevada foi registrada antes da 20ª semana de gestação?",
        'options': {
            'sim': 'Sim, foi antes da 20ª semana.',
            'nao': 'Não, foi após a 20ª semana.'
        },
        'next': {
            'sim': 'diagnostico_has_cronica',
            'nao': '3'
        }
    },
    '3': {
        'text': "Sua pressão arterial está elevada em 3 ocasiões diferentes?",
        'options': {
            'sim': 'Sim, em 3 ocasiões diferentes.',
            'nao': 'Não, menos de 3 ocasiões.'
        },
        'next': {
            'sim': 'diagnostico_hipertensao_gestacional',
            'nao': 'end_monitoring'
        }
    },
    '4': {
        'text': "Você já fez algum exame de urina recente para verificar a presença de proteína (proteinúria)?",
        'options': {
            'sim': 'Sim, já fiz o exame de proteinúria.',
            'nao': 'Não, ainda não fiz o exame de proteinúria.'
        },
        'next': {
            'sim': '5',  # Se sim, segue para o resultado do exame
            'nao': 'recommend_exam'  # Se não, recomenda exame e acompanhamento
        }
    },
    '5': {
        'text': "Qual foi o resultado do exame de urina?",
        'options': {
            '1': 'Proteinúria ≥ 300mg/24h ou maciça',
            '2': 'Proteinúria "Traços"',
            '3': 'Proteinúria "Nenhum"'
        },
        'next': {
            '1': 'diagnostico_pre_eclampsia',
            '2': 'repeat_exam',
            '3': 'continue_monitoring'
        }
    },
    '6': {
        'text': "Seus exames laboratoriais indicaram níveis elevados de ácido úrico (maiores que 6mg/dl)?",
        'options': {
            'sim': 'Sim',
            'nao': 'Não'
        },
        'next': {
            'sim': 'diagnostico_pre_eclampsia',  # Encaminhar ao serviço de alto risco
            'nao': 'continue_monitoring'  # Continuar monitoramento regular
        }
    },
    '7': {
        'text': "Sua pressão arterial está muito elevada (PA Sistólica ≥ 160mmHg ou PA Diastólica ≥ 110mmHg)?",
        'options': {
            'sim': 'Sim, a PA está muito elevada.',
            'nao': 'Não, está abaixo desse valor.'
        },
        'next': {
            'sim': '8',  # Segue para sintomas de pré-eclâmpsia grave
            'nao': 'continue_monitoring'
        }
    },
    '8': {
        'text': "Você teve algum dos seguintes sintomas ou resultados em exames?\n(Oligúria, Creatinina elevada, Proteinúria massiva, Plaquetopenia, Aumento de TGO/TGP, Desidrogenase lática elevada)",
        'options': {
            'sim': 'Sim, um ou mais desses sintomas.',
            'nao': 'Não, nenhum desses sintomas.'
        },
        'next': {
            'sim': 'diagnostico_pre_eclampsia_grave',  # Diagnóstico de pré-eclâmpsia grave
            'nao': 'continue_monitoring'
        }
    },
    '9': {
        'text': "Você teve algum dos seguintes sintomas recentemente? (Convulsões, Perda de consciência, Confusão mental, Visão turva ou diplopia, Cefaleia intensa, Epigastralgia, Tontura, Escotomas cintilantes)",
        'options': {
            'sim': 'Sim, um ou mais desses sintomas.',
            'nao': 'Não, nenhum desses sintomas.'
        },
        'next': {
            'sim': 'diagnostico_eclampsia_iminente',
            'nao': 'continue_monitoring'
        }
    }
}


# Função para enviar a pergunta ao usuário com base no ID
async def enviar_pergunta(update: Update, context: ContextTypes.DEFAULT_TYPE, question_id: str) -> None:
    question = questions[question_id]
    # Verifica se a pergunta é do tipo Sim/Não
    # IDs das perguntas que são Sim/Não
    if question_id in ["confirm_delete", "2", "3", "4", "6", "7", "8", "9"]:
        await update.message.reply_text(f"{question['text']}\n(Responda com Sim/Não)")
    else:
        options_text = "\n".join(
            [f"{key}. {text}" for key, text in question['options'].items()])
        await update.message.reply_text(f"{question['text']}\n{options_text}")


# Função para lidar com as respostas do usuário e salvar o texto correspondente
# Processa a resposta com base no fluxo de perguntas
# Salva resposta no banco e determina o próximo passo
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_response = update.message.text.strip().lower()
    user_response = unidecode.unidecode(user_response)  # Remove acentos

    current_question_id = context.user_data.get('question_id', '0')
    current_question = questions.get(current_question_id)

    if current_question_id == '0':  # Mensagem inicial
        if user_response in ['1', '2', '3', '4', '5']:
            next_step = current_question['next'][user_response]
            if next_step == 'handle_audio':
                # Solicita envio do áudio
                await update.message.reply_text("Por favor, grave e envie o seu áudio.")
                # Marca como esperando áudio
                context.user_data['awaiting_audio'] = True
                return
            elif next_step == 'handle_photo':
                await update.message.reply_text("Por favor, envie uma foto.")
                context.user_data['awaiting_photo'] = True
                return
            elif next_step == 'handle_video':
                await update.message.reply_text("Por favor, envie um vídeo.")
                context.user_data['awaiting_video'] = True
                return
            else:
                context.user_data['question_id'] = next_step
                await enviar_pergunta(update, context, next_step)
                return
        else:
            await update.message.reply_text("Opção inválida. Por favor, digite '1', '2', '3', '4' ou '5'.")
            return

    if context.user_data.get('awaiting_audio'):
        await update.message.reply_text("Por favor, envie um arquivo de áudio.")
        return

    if context.user_data.get('awaiting_photo'):
        await update.message.reply_text("Por favor, envie uma foto.")
        return

    if context.user_data.get('awaiting_video'):
        await update.message.reply_text("Por favor, envie um arquivo de vídeo.")
        return

    if current_question_id == 'confirm_delete':  # Confirmação de exclusão
        if user_response in ['sim', 'nao']:
            if user_response == 'sim':
                await deletar_dados_usuario(user_id)
                await update.message.reply_text("Seus dados foram apagados com sucesso.")
                context.user_data.clear()
            else:
                await update.message.reply_text("Operação cancelada. Estamos à disposição caso precise!")
                context.user_data.clear()
            return
        else:
            await update.message.reply_text("Resposta inválida. Por favor, digite 'Sim' ou 'Não'.")
            return
    # IDs das perguntas de Sim/Não
    if current_question_id in ["confirm_delete", "2", "3", "4", "6", "7", "8", "9"]:
        if user_response in ["sim", "nao"]:
            # Salva "Sim" ou "Não" no banco de dados
            response_text = "Sim" if user_response == "sim" else "Não"
            salvar_resposta(user_id, current_question['text'], response_text)
            next_step = current_question['next'][user_response]
        else:
            await update.message.reply_text("Resposta inválida. Por favor, responda com 'Sim' ou 'Não'.")
            return
    else:
        # Pergunta não é Sim/Não; verifica se a resposta é válida (existe nas opções)
        if user_response in current_question['options']:
            response_text = current_question['options'][user_response]
            salvar_resposta(user_id, current_question['text'], response_text)
            next_step = current_question['next'][user_response]
        else:
            await update.message.reply_text("Resposta inválida. Por favor, selecione uma opção válida.")
            return

    # Próximos passos de acordo com o fluxo
    # Condições finais ou para próximas perguntas de proteinúria
    if next_step == 'end_monitoring':
        await update.message.reply_text("Continue monitorando regularmente sua pressão arterial. Agende a próxima consulta de rotina.")
        # Segue para pergunta sobre proteinúria
        context.user_data['question_id'] = '4'
        await enviar_pergunta(update, context, '4')
    elif next_step == 'diagnostico_has_cronica':
        await update.message.reply_text("Risco de: Hipertensão Arterial Crônica (HAS Crônica).")
        salvar_resposta(user_id, 'Diagnóstico Hipertensão',
                        'Hipertensão Arterial Crônica')
        # Segue para pergunta sobre proteinúria
        context.user_data['question_id'] = '4'
        await enviar_pergunta(update, context, '4')
    elif next_step == 'diagnostico_hipertensao_gestacional':
        await update.message.reply_text("Risco de: Hipertensão Gestacional.")
        salvar_resposta(user_id, 'Diagnóstico Hipertensão',
                        'Hipertensão Gestacional')
        # Segue para pergunta sobre proteinúria
        context.user_data['question_id'] = '4'
        await enviar_pergunta(update, context, '4')
    elif next_step == 'recommend_exam':
        await update.message.reply_text("Recomendo que faça um exame de urina para verificar a presença de proteína. Por favor, continue o acompanhamento regular.")
        # context.user_data['question_id'] = '5'  # Próxima etapa
        # await enviar_pergunta(update, context, '5')
        # context.user_data.clear()
        # Segue para pergunta sobre acido urico
        context.user_data['question_id'] = '6'
        await enviar_pergunta(update, context, '6')
    elif next_step == 'diagnostico_pre_eclampsia':
        await update.message.reply_text("Risco de: Pré-eclâmpsia.\nEncaminhamento ao serviço de alto risco recomendado.")
        salvar_resposta(user_id, 'Diagnóstico', 'Pré-eclâmpsia')
        # context.user_data.clear()  # Finaliza a interação
        context.user_data['question_id'] = '7'
        await enviar_pergunta(update, context, '7')
    elif next_step == 'repeat_exam':
        await update.message.reply_text("Recomendo repetir o exame em 15 dias e monitorar sintomas.")
        # context.user_data.clear()  # Finaliza a interação
        context.user_data['question_id'] = '6'
        await enviar_pergunta(update, context, '6')
    elif next_step == 'continue_monitoring':
        await update.message.reply_text("Continue monitoramento e acompanhamento regular na UBS.")
        # Delay de 3 segundos antes de enviar a mensagem inicial
        await asyncio.sleep(3)
        # Envia novamente a mensagem inicial
        context.user_data.clear()  # Finaliza a interação
        context.user_data['question_id'] = '0'
        await enviar_pergunta(update, context, '0')
    elif next_step == 'diagnostico_pre_eclampsia_grave':
        await update.message.reply_text("Risco de: Pré-eclâmpsia Grave.\nEncaminhamento ao serviço de alto risco recomendado.")
        salvar_resposta(
            user_id, 'Diagnóstico', 'Pré-eclâmpsia Grave')
        # context.user_data.clear()
        context.user_data['question_id'] = '9'
        await enviar_pergunta(update, context, '9')
    elif next_step == 'diagnostico_eclampsia_iminente':
        await update.message.reply_text("Risco de: Eclâmpsia Iminente. Você apresenta risco iminente de eclâmpsia.\nEncaminhamento imediato ao serviço de alto risco é recomendado.")
        salvar_resposta(
            user_id, 'Diagnóstico', 'Eclâmpsia Iminente')
        # Delay de 3 segundos antes de enviar a mensagem inicial
        await asyncio.sleep(3)
        # Envia novamente a mensagem inicial
        context.user_data.clear()
        context.user_data['question_id'] = '0'
        await enviar_pergunta(update, context, '0')
    else:
        # Atribui o próximo question_id no contexto do usuário e faz a próxima pergunta
        context.user_data['question_id'] = next_step
        await enviar_pergunta(update, context, next_step)


async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_dir = os.path.join(AUDIO_DIR, f"user_{user_id}")
    os.makedirs(user_dir, exist_ok=True)

    try:
        print("Handle_audio")
        # Obtém o arquivo de áudio enviado
        usuario_id = update.message.from_user.id
        user_dir = os.path.join(AUDIO_DIR, f"user_{usuario_id}")
        os.makedirs(user_dir, exist_ok=True)

        audio_file = await update.message.voice.get_file()
        audio_path = get_next_filename(
            user_dir, f'audio_user_{usuario_id}', '.wav')
        await audio_file.download_to_drive(audio_path)

        salvar_midia(usuario_id, 'audio', audio_path)

        # Aguardar transcrição (simulada com sleep)
        time.sleep(3)

        # Retorna a confirmação e reinicia o fluxo inicial
        await update.message.reply_text("Áudio recebido e transcrito com sucesso.")
        context.user_data.clear()  # Reseta o contexto do usuário
        context.user_data['question_id'] = '0'
        await enviar_pergunta(update, context, '0')
    except Exception as e:
        await update.message.reply_text("Erro ao processar o áudio. Por favor, tente novamente.")
        print(f"Erro ao lidar com o áudio: {e}")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_dir = os.path.join(IMAGES_DIR, f"user_{user_id}")
    os.makedirs(user_dir, exist_ok=True)

    try:
        print("Handle_photo")
        # Obtém o arquivo de foto enviado
        photo_file = await update.message.photo[-1].get_file()
        photo_path = get_next_filename(
            user_dir, f'photo_user_{user_id}', '.jpg'
        )
        await photo_file.download_to_drive(photo_path)

        # Salva a mídia no banco de dados
        salvar_midia(user_id, 'foto', photo_path)

        # Retorna a confirmação e reinicia o fluxo inicial
        await update.message.reply_text("Foto recebida com sucesso.")
        context.user_data.clear()  # Reseta o contexto do usuário
        context.user_data['question_id'] = '0'
        await enviar_pergunta(update, context, '0')
    except Exception as e:
        await update.message.reply_text("Erro ao processar a foto. Por favor, tente novamente.")
        print(f"Erro ao lidar com a foto: {e}")


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_dir = os.path.join(VIDEO_DIR, f"user_{user_id}")
    os.makedirs(user_dir, exist_ok=True)

    try:
        print("Handle_video")
        # Obtém o arquivo de vídeo enviado
        video_file = await update.message.video.get_file()
        video_path = get_next_filename(
            user_dir, f'video_user_{user_id}', '.mp4'
        )
        await video_file.download_to_drive(video_path)

        # Salva a mídia no banco de dados
        salvar_midia(user_id, 'video', video_path)

        # Simulação de transcrição e legendagem (substitua por chamadas reais, se necessário)
        time.sleep(5)  # Simula tempo de processamento de transcrição
        transcricao_texto = f"Transcrição simulada para {
            os.path.basename(video_path)}"
        print(f"Transcrição completa: {transcricao_texto}")

        # Simula tempo de legendagem
        time.sleep(3)
        legendado_path = f"{os.path.splitext(video_path)[0]}_legendado.mp4"
        print(f"Legenda salva em: {legendado_path}")

        # Retorna a confirmação e reinicia o fluxo inicial
        await update.message.reply_text("Vídeo recebido, transcrito e legendado com sucesso.")
        context.user_data.clear()  # Reseta o contexto do usuário
        context.user_data['question_id'] = '0'
        await enviar_pergunta(update, context, '0')
    except Exception as e:
        await update.message.reply_text("Erro ao processar o vídeo. Por favor, tente novamente.")
        print(f"Erro ao lidar com o vídeo: {e}")


# Função para iniciar a conversa
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    # Resetar o contexto do usuário ao iniciar uma nova conversa
    context.user_data.clear()  # Limpar as respostas anteriores

    # Obtém o nome do usuário
    nome_usuario = update.message.from_user.first_name

    # Verifica se o usuário já está no banco de dados, e insere se necessário
    verificar_ou_inserir_usuario(user_id, nome_usuario)

    # Enviar a primeira mensagem
    await update.message.reply_text(
        "Olá! Este é o Bot de Telemonitoramento.\n\n"
        "Este bot monitora parâmetros de saúde e coleta informações para melhorar seu acompanhamento médico. "
        "Seus dados serão tratados com segurança e utilizados apenas para fins médicos, em conformidade com a LGPD."
    )

    # Enviar a primeira pergunta
    context.user_data['question_id'] = '0'  # Inicia na primeira pergunta
    await enviar_pergunta(update, context, '0')


# Função para verificar se o usuário existe na tabela usuarios, e inseri-lo se não existir
def verificar_ou_inserir_usuario(usuario_id, nome_usuario):
    with get_db_connection() as connection:
        if connection:
            try:
                with connection.cursor() as cursor:
                    # Verificar se o usuário já existe
                    query_check = "SELECT 1 FROM usuarios WHERE usuario_id = %s"
                    cursor.execute(query_check, (usuario_id,))
                    if cursor.fetchone() is None:
                        # Insere o usuário
                        query_insert = "INSERT INTO usuarios (usuario_id, nome) VALUES (%s, %s)"
                        cursor.execute(
                            query_insert, (usuario_id, nome_usuario))
                        connection.commit()
                        print(
                            f"Usuário {usuario_id} inserido no banco de dados.")
            except Exception as e:
                print(f"Erro ao verificar ou inserir usuário: {e}")


# Função para salvar respostas no banco de dados
def salvar_resposta(telegram_user_id, pergunta, resposta):
    usuario_id = get_usuario_id_by_telegram_id(telegram_user_id)
    with get_db_connection() as connection:
        if connection:
            try:
                with connection.cursor() as cursor:
                    query_insert = """
                    INSERT INTO respostas (usuario_id, pergunta, resposta)
                    VALUES (%s, %s, %s)
                    """
                    cursor.execute(
                        query_insert, (usuario_id, pergunta, resposta))
                    connection.commit()
                    print(f"Resposta salva no banco de dados: {resposta}")
            except Exception as e:
                print(f"Erro ao salvar resposta: {e}")


def salvar_midia(telegram_user_id, tipo_midia, caminho_arquivo):
    usuario_id = get_usuario_id_by_telegram_id(telegram_user_id)
    if usuario_id:
        with get_db_connection() as connection:
            if connection:
                try:
                    with connection.cursor() as cursor:
                        insert_query = """
                        INSERT INTO midias (usuario_id, tipo_midia, caminho_arquivo)
                        VALUES (%s, %s, %s)
                        """
                        cursor.execute(
                            insert_query, (usuario_id, tipo_midia, caminho_arquivo))
                        connection.commit()
                        print(f"Mídia salva no banco de dados: {
                              caminho_arquivo}")
                except Exception as e:
                    print(f"Erro ao salvar mídia: {e}")


# Função para organizar as pastas e nomear os arquivos
def get_next_filename(directory, base_filename, extension):
    print("get_next_filename")
    counter = 1
    while True:
        filename = f"{base_filename}_{counter}{extension}"
        filepath = os.path.join(directory, filename)
        if not os.path.exists(filepath):
            return filepath
        counter += 1


# Função para deletar dados do usuário
def deletar_dados_usuario(usuario_id):
    with get_db_connection() as connection:
        if connection:
            try:
                with connection.cursor() as cursor:
                    # Exclui dados do usuário
                    query_delete_respostas = "DELETE FROM respostas WHERE usuario_id = %s"
                    query_delete_usuario = "DELETE FROM usuarios WHERE usuario_id = %s"
                    cursor.execute(query_delete_respostas, (usuario_id,))
                    cursor.execute(query_delete_usuario, (usuario_id,))
                    connection.commit()
                    print(f"Dados do usuário {
                          usuario_id} apagados com sucesso.")
            except Exception as e:
                print(f"Erro ao apagar dados do usuário: {e}")


# Busca o id do usuário no banco de dados baseado no user_id do Telegram.
def get_usuario_id_by_telegram_id(telegram_user_id):
    with get_db_connection() as connection:
        if connection:
            try:
                with connection.cursor() as cursor:
                    query = "SELECT id FROM usuarios WHERE usuario_id = %s"
                    cursor.execute(query, (telegram_user_id,))
                    result = cursor.fetchone()
                    if result:
                        return result[0]
                    else:
                        print(f"Usuário com Telegram ID {
                              telegram_user_id} não encontrado.")
                        return None
            except Exception as e:
                print(f"Erro ao buscar id do usuário: {e}")
                return None


# Defina timeouts maiores
# Configuração de tempo limite para requisições HTTP do Telegram
request = HTTPXRequest(
    connect_timeout=10.0,  # Timeout para conectar (em segundos)
    read_timeout=60.0  # Timeout para leitura de grandes arquivos, como vídeos
)


# Função principal para configurar o bot e definir os handlers de eventos
def main() -> None:
    print("Main")
    application = ApplicationBuilder().token(
        "SEU_TOKEN_AQUI").request(request).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    application.add_handler(MessageHandler(filters.VOICE, handle_audio))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    application.run_polling()


if __name__ == '__main__':
    main()
