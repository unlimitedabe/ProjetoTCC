# **Autor: Rafael de Matos Abe**
# **Co-Autor: Gabriel Fellipe Felix Lima**
# **Orientador: Talles Marcelo Gonçalves de Andrade Barbosa**
# **Universidade: Pontifícia Universidade Católica de Goiás**
# **Trabalho de Conclusão de Curso**
# **Projeto: Customização do Telegram Para Aplicações em Saúde (Telemonitoramento para Gestantes em Situação de Risco de Pré-eclâmpsia e Eclâmpsia)**

## **Descrição do Projeto**
Este projeto visa criar um sistema de **telemonitoramento** para gestantes em risco de **hipertensão arterial crônica**, **pré-eclâmpsia** e **eclâmpsia iminente**, utilizando o **Telegram** como plataforma base. O sistema possibilita:
- Envio e monitoramento de respostas de pacientes.
- Integração com mídias (áudios, vídeos e fotos).
- Análise e visualização de dados através de uma interface gráfica.

O fluxo de monitoramento é baseado no trabalho de **LIMA, Gabriel Fellipe Felix**, descrito em:  
>LIMA, Gabriel Fellipe Felix. **Desenvolvimento de um software para apoio ao diagnóstico da gestação de alto risco**. Programa de Iniciação Científica: PIBITI/CNPq. Orientador: Talles Marcelo Gonçalves de Andrade Barbosa. Goiânia: Pontifícia Universidade Católica de Goiás, 2023. Disponível em: <https://sistemas.pucgoias.edu.br/sigep/espelhoIniciacaoCientifica/show/22534>. Acesso em: 09 out. 2024.

---

## **Requisitos do Sistema**
- **Telegram Bot Token:** Configure no arquivo `bot.py` com o seu token.
- **Banco de Dados PostgreSQL:** Configure no arquivo `database.py` com os dados do seu banco.
- **Python:** Versão 3.12.2.
- Dependências adicionais:
  - Flask
  - Chart.js
  - ffmpeg-7.0.2
  - ImageMagick-7.1.1
  - MoviePy
  - Whisper
  - Watchdog

---

## **Funcionalidades**
### **Chatbot**
- Envia perguntas e coleta respostas (sim/não, numéricas, texto, áudios, vídeos, fotos).
- Realiza transcrição de áudios e legendagem de vídeos.
- Organiza e armazena as respostas no banco de dados.

### **Interface Gráfica**
- Exibe gráficos dinâmicos com os dados coletados.
- Possibilita a análise detalhada do histórico do paciente.
- Organiza arquivos enviados (áudios, vídeos, imagens) de forma clara.

---

## **Diagrama de Implantação**
A seguir, a estrutura de comunicação do sistema:

![image](https://github.com/user-attachments/assets/07227ec2-4ce8-43c6-bec9-2f1d2bb56347)


---

## **Estrutura do Banco de Dados**
O modelo de relacionamento do banco de dados foi desenhado para suportar as funcionalidades de armazenamento e organização de respostas, conforme descrito abaixo:

![image](https://github.com/user-attachments/assets/ba995969-814f-4c2c-887d-16e66633c741)


---

## **Casos de Uso**
Os casos de uso foram baseados no trabalho de Gabriel Lima e possibilitam:
- Diagnóstico de hipertensão arterial crônica, pré-eclâmpsia e eclâmpsia iminente.
- Monitoramento contínuo de sinais clínicos como pressão arterial e proteinúria.
- Acompanhamento e encaminhamento adequado.

>LIMA, Gabriel Fellipe Felix. **Desenvolvimento de um software para apoio ao diagnóstico da gestação de alto risco**. Programa de Iniciação Científica: PIBITI/CNPq. Orientador: Talles Marcelo Gonçalves de Andrade Barbosa. Goiânia: Pontifícia Universidade Católica de Goiás, 2023. Disponível em: <https://sistemas.pucgoias.edu.br/sigep/espelhoIniciacaoCientifica/show/22534>. Acesso em: 09 out. 2024.

### **Fluxos**
1. Diagnóstico de Pré-eclâmpsia:
![image](https://github.com/user-attachments/assets/ff53704c-db60-4870-817c-c7a4f3d8dd96)

2. Diagnóstico de Pré-eclâmpsia Grave:
![image](https://github.com/user-attachments/assets/f1a3145e-ac17-4978-90e9-db7a69abdef1)

3. Diagnóstico de Eclâmpsia Iminente:
![image](https://github.com/user-attachments/assets/9415ebd2-bf06-43bc-9191-94a68f7aa5e3)

---

## **Estrutura do Projeto**
A estrutura foi organizada para separar claramente o backend, frontend e armazenamento de mídias:

```
backend/
    ├── app.py
    ├── bot.py
    ├── database.py
    ├── legendagem.py
    ├── transcricao.py
frontend/
    ├── static/
    │   ├── css/
    │   ├── js/
    ├── templates/
media/
    ├── audio/
    ├── video/
    ├── images/
```

---

## **Como Rodar o Projeto**
### 0. Crie seu database
Nesse projeto foi utilizando o postgresql, e o script está no backend/script_database.txt

### 1. Configurar o `bot.py`
Substitua o token pelo do seu bot:

```python
application = ApplicationBuilder().token("SEU_TOKEN_AQUI").request(request).build()
```

### 2. Configurar o `database.py`
Adapte as credenciais do banco de dados:

```python
connection = psycopg2.connect(
    host="seu_host",
    database="seu_database",
    user="seu_user",
    password="sua_senha",
    port="sua_porta"
)
```

### 3. Instalar Dependências
Use o comando abaixo para instalar as bibliotecas necessárias:
```bash
pip install -r requirements.txt
```

### 4. Executar o Sistema
Inicie o bot e o servidor do Flask, entre no diretorio backend e rode:
```bash
python app.py
```

---

## **Licenciamento**
Este projeto utiliza as seguintes bibliotecas e tecnologias, todas com licenciamento adequado:

### **Linguagens de Programação**
- **Python**: Versão 3.12.2.  
  Licença: Python Software Foundation License.  
  Copyright: © Python Software Foundation.

---

### **Frameworks e Bibliotecas**

#### **Backend e Integração**
- **Flask**: Framework leve para construção de APIs e aplicações web.  
  Licença: BSD 3-Clause License.  
  Copyright: © Pallets Project.

- **Flask-Talisman**: Biblioteca para melhorar a segurança HTTP em aplicações Flask.  
  Licença: MIT License.  
  Copyright: © Pallets Project.

- **psycopg2**: Driver para interação com bancos de dados PostgreSQL.  
  Licença: LGPL.  
  Copyright: © Federico Di Gregorio.

- **Python Telegram Bot**: Integração com a API do Telegram para criar bots.  
  Licença: LGPL 3.0.  
  Copyright: © Python Telegram Bot Community.

- **Unidecode**: Biblioteca para remoção de acentos e caracteres especiais.  
  Licença: GPL.  
  Copyright: © Tomaz Solc.

#### **Frontend**
- **Chart.js**: Biblioteca JavaScript para renderização de gráficos.  
  Licença: MIT License.  
  Copyright: © Chart.js Contributors.

#### **Mídia e Transcrição**
- **MoviePy**: Biblioteca para edição de vídeos.  
  Licença: MIT License.  
  Copyright: © Zulko.

- **Whisper**: Modelo de IA para transcrição de áudio.  
  Licença: MIT License.  
  Copyright: © OpenAI.

- **Watchdog**: Biblioteca para monitoramento de arquivos em tempo real.  
  Licença: Apache License 2.0.  
  Copyright: © Contributors of Watchdog.

#### **Manipulação de Dados**
- **NumPy**: Biblioteca para computação numérica.  
  Licença: BSD License.  
  Copyright: © NumPy Developers.

- **Pandas**: Biblioteca para manipulação e análise de dados.  
  Licença: BSD 3-Clause License.  
  Copyright: © pandas development team.

---

### **Ferramentas**
- **PgAdmin 4**: Ferramenta para administração de bancos de dados PostgreSQL.  
  Licença: PostgreSQL License.  
  Copyright: © PostgreSQL Global Development Group.

- **DBeaver**: Ferramenta para visualização e administração de bancos de dados.  
  Licença: Apache License 2.0.  
  Copyright: © DBeaver Corporation.

- **VS Code**: IDE para desenvolvimento de software.  
  Licença: MIT License.  
  Copyright: © Microsoft Corporation.

- **Lucidchart**: Plataforma para criação de diagramas UML.  
  Licença: Proprietária.  
  Copyright: © Lucid Software.

---

### **Ferramentas de Mídia**
- **FFmpeg**: Software para processamento de áudio e vídeo.  
  Licença: LGPL 2.1 ou GPL 2.0 (escolha do desenvolvedor).  
  Copyright: © FFmpeg Developers.

- **ImageMagick**: Biblioteca para edição de imagens.  
  Licença: Apache License 2.0.  
  Copyright: © ImageMagick Studio LLC.

---

### **Dependências Adicionais**
Para uma lista completa das dependências instaladas no ambiente virtual, consulte o arquivo `requirements.txt` no repositório. As bibliotecas listadas incluem, mas não se limitam a:
- **OpenPyXL**: Manipulação de arquivos Excel.  
  Licença: MIT License.  
  Copyright: © Contributors.

- **TQDM**: Barra de progresso em Python.  
  Licença: MIT License.  
  Copyright: © Contributors.

- **SpeechRecognition**: Reconhecimento de fala em Python.  
  Licença: BSD License.  
  Copyright: © Contributors.

---

## **Trabalhos Futuros**
As possíveis melhorias e expansões do sistema incluem:
- **Novos Casos de Uso**: Adicionar outros casos de uso relacionados a área da saúde.
- **Integração com IA**: Usar IA para interpretar dados enviados e personalizar respostas.
- **Testes com Outras Plataformas**: Explorar a aplicação em plataformas como WhatsApp ou Signal.

---

## **Vídeo Apresentação do TCC**
O vídeo de apresentação do projeto sendo executando está disponível no seguinte drive:
[https://drive.google.com/drive/folders/1dv9AD24964Er97L_K5HMkxa0c8RNLRoz?usp=drive_link](https://drive.google.com/drive/folders/1dv9AD24964Er97L_K5HMkxa0c8RNLRoz?usp=sharing)

---
