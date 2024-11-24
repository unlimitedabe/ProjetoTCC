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
            '1': 'Proteinúria ≥ 300mg/24h',
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
    if question_id in ["2", "3", "4", "6", "7", "8", "9"]:
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

    current_question_id = context.user_data.get('question_id', '1')
    current_question = questions.get(current_question_id)

    # Se a pergunta atual é Sim/Não, valida e salva como 'Sim' ou 'Não'
    # IDs das perguntas de Sim/Não
    if current_question_id in ["2", "3", "4", "6", "7", "8", "9"]:
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
        await update.message.reply_text("Diagnóstico: Hipertensão Arterial Crônica (HAS Crônica).")
        salvar_resposta(user_id, 'Diagnóstico Hipertensão',
                        'Hipertensão Arterial Crônica')
        # Segue para pergunta sobre proteinúria
        context.user_data['question_id'] = '4'
        await enviar_pergunta(update, context, '4')
    elif next_step == 'diagnostico_hipertensao_gestacional':
        await update.message.reply_text("Diagnóstico: Hipertensão Gestacional.")
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
        await update.message.reply_text("Diagnóstico: Pré-eclâmpsia. Encaminhamento ao serviço de alto risco recomendado.")
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
        context.user_data.clear()  # Finaliza a interação
    elif next_step == 'diagnostico_pre_eclampsia_grave':
        await update.message.reply_text("Diagnóstico: Pré-eclâmpsia Grave. Encaminhamento ao serviço de alto risco recomendado.")
        salvar_resposta(
            user_id, 'Diagnóstico', 'Pré-eclâmpsia Grave')
        # context.user_data.clear()
        context.user_data['question_id'] = '9'
        await enviar_pergunta(update, context, '9')
    elif next_step == 'diagnostico_eclampsia_iminente':
        await update.message.reply_text("Diagnóstico: Eclâmpsia Iminente. Você apresenta risco iminente de eclâmpsia. Encaminhamento imediato ao serviço de alto risco é recomendado.")
        salvar_resposta(
            user_id, 'Diagnóstico', 'Eclâmpsia Iminente')
        context.user_data.clear()
    else:
        # Atribui o próximo question_id no contexto do usuário e faz a próxima pergunta
        context.user_data['question_id'] = next_step
        await enviar_pergunta(update, context, next_step)


# Função para iniciar a conversa
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    # Resetar o contexto do usuário ao iniciar uma nova conversa
    context.user_data.clear()  # Limpar as respostas anteriores

    # Obtém o nome do usuário
    nome_usuario = update.message.from_user.first_name

    # Verifica se o usuário já está no banco de dados, e insere se necessário
    verificar_ou_inserir_usuario(user_id, nome_usuario)

    # Enviar a primeira pergunta
    context.user_data['question_id'] = '1'  # Inicia na primeira pergunta
    await enviar_pergunta(update, context, '1')


# Função para verificar se o usuário existe na tabela usuarios, e inseri-lo se não existir
def verificar_ou_inserir_usuario(usuario_id, nome_usuario):
    with get_db_connection() as connection:
        if connection:
            try:
                with connection.cursor() as cursor:
                    # Verificar se o usuário já existe
                    cursor.execute(
                        "SELECT 1 FROM usuarios WHERE usuario_id = %s", (usuario_id,))
                    if cursor.fetchone() is None:
                        # Se o usuário não existir, insira o usuário na tabela
                        insert_query = "INSERT INTO usuarios (usuario_id, nome) VALUES (%s, %s)"
                        cursor.execute(
                            insert_query, (usuario_id, nome_usuario))
                        connection.commit()  # Confirma a inserção do usuário
                        print(
                            f"Usuário {usuario_id} inserido no banco de dados.")

                        # Pausa breve para garantir que o commit seja refletido (para teste)
                        time.sleep(2)
                    else:
                        print(
                            f"Usuário {usuario_id} já existe no banco de dados.")
            except Exception as e:
                print(f"Erro ao verificar ou inserir usuário: {e}")


# Função para salvar respostas no banco de dados
def salvar_resposta(telegram_user_id, pergunta, resposta):
    usuario_id = get_usuario_id_by_telegram_id(telegram_user_id)
    # if usuario_id:
    with get_db_connection() as connection:
        if connection:
            try:
                with connection.cursor() as cursor:
                    insert_query = """
                    INSERT INTO respostas (usuario_id, pergunta, resposta)
                    VALUES (%s, %s, %s)
                    """
                    cursor.execute(
                        insert_query, (usuario_id, pergunta, resposta))
                    connection.commit()
                    print(f"Resposta salva no banco de dados: {resposta}")
            except Exception as e:
                print(f"Erro ao salvar resposta: {e}")


# Busca o id do usuário no banco de dados baseado no user_id do Telegram.
def get_usuario_id_by_telegram_id(telegram_user_id):
    with get_db_connection() as connection:
        if connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT id FROM usuarios WHERE usuario_id = %s", (telegram_user_id,))
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
        "7482188034:AAFMjb13uoC3amBEM21Mr6t9JEDMw1mYykA").request(request).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_message))
    # application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    # application.add_handler(MessageHandler(filters.VOICE, handle_audio))
    # application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    application.run_polling()


if __name__ == '__main__':
    main()
