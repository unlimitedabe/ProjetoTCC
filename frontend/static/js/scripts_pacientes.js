// Função para carregar a lista de pacientes
function loadPatients() {
    fetch('/api/pacientes')  // Rota que retorna a lista de pacientes
        .then(response => response.json())
        .then(patients => {
            const patientList = document.getElementById('patientList');
            patientList.innerHTML = '';  // Limpa a lista
            patients.forEach(patient => {
                const li = document.createElement('li');
                li.textContent = patient.nome;
                // Abre o perfil do paciente em uma nova aba ao clicar
                li.onclick = () => window.open(`/paciente/${patient.id}`, '_blank');
                patientList.appendChild(li);
            });
        })
        .catch(error => console.error('Erro ao carregar pacientes:', error));
}


// Função para exibir mídias relacionadas a cada paciente
function exibirMidias() {
    fetch('/obter_midias')
        .then(response => response.json())
        .then(midias => {
            const midiasContainer = document.getElementById('midias-container');
            midiasContainer.innerHTML = ''; // Limpar o container anterior

            midias.forEach(midia => {
                const midiaDiv = document.createElement('div');
                midiaDiv.className = 'midia-item';

                // Verifica o tipo de mídia para exibir no formato adequado
                if (midia.tipo === 'audio') {
                    const audioElement = document.createElement('audio');
                    audioElement.src = `/media/${midia.caminho}`;  // Usar caminho direto
                    audioElement.controls = true;
                    midiaDiv.appendChild(audioElement);

                    // Exibir a transcrição do áudio
                    if (midia.transcricao_audio) {
                        const transcricaoAudio = document.createElement('p');
                        transcricaoAudio.textContent = `Transcrição: ${midia.transcricao_audio}`;
                        midiaDiv.appendChild(transcricaoAudio);
                    }

                } else if (midia.tipo === 'foto') {
                    const imgElement = document.createElement('img');
                    imgElement.src = `/media/${midia.caminho}`;  // Usar caminho direto
                    imgElement.alt = 'Imagem do paciente';
                    imgElement.style.width = '200px';
                    midiaDiv.appendChild(imgElement);

                } else if (midia.tipo === 'video') {
                    const videoElement = document.createElement('video');
                    videoElement.src = `/media/${midia.caminho}`;  // Usar caminho direto
                    videoElement.controls = true;
                    midiaDiv.appendChild(videoElement);

                    // Exibir a transcrição do vídeo
                    if (midia.transcricao_video) {
                        const transcricaoVideo = document.createElement('p');
                        transcricaoVideo.textContent = `Transcrição: ${midia.transcricao_video}`;
                        midiaDiv.appendChild(transcricaoVideo);
                    }
                }

                midiasContainer.appendChild(midiaDiv);
            });
        })
        .catch(error => console.error('Erro ao buscar mídias:', error));
}

// Função para mostrar mensagens anteriores
function mostrarMensagensAnteriores() {
    // Aqui você pode adicionar a lógica para carregar mensagens adicionais via AJAX
    const historicoContainer = document.getElementById('historico-respostas');
    fetch('/paciente/mensagens-anteriores')  // Ajuste conforme sua rota
        .then(response => response.json())
        .then(mensagens => {
            mensagens.forEach(mensagem => {
                const li = document.createElement('li');
                li.textContent = `${mensagem[2]} (${mensagem[4]}): ${mensagem[3]}`;
                historicoContainer.appendChild(li);
            });
        })
        .catch(error => console.error('Erro ao carregar mensagens anteriores:', error));
}

// Função para mostrar mensagens anteriores
function mostrarMensagensAnteriores(patientId) {
    console.error('Erro ao carregar mensagens anteriores:', patientId)
    const historicoContainer = document.getElementById('historico-respostas');
    fetch(`/paciente/mensagens-anteriores/${patientId}`)
        .then(response => response.json())
        .then(mensagens => {
            historicoContainer.innerHTML = '';  // Limpar as mensagens atuais para evitar duplicação
            mensagens.forEach(mensagem => {
                const li = document.createElement('li');
                li.textContent = `${mensagem[2]} (${mensagem[4]}): ${mensagem[3]}`;  // Exibir data e mensagem
                historicoContainer.appendChild(li);
            });
            document.getElementById('ver-mais').style.display = 'none';  // Esconder o botão após exibir todas
        })
        .catch(error => console.error('Erro ao carregar mensagens anteriores:', error));
}


// Função para buscar pacientes na lista
document.getElementById('searchBar').addEventListener('input', function() {
    const query = this.value.toLowerCase();
    const items = document.querySelectorAll('#patientList li');
    items.forEach(item => {
        item.style.display = item.textContent.toLowerCase().includes(query) ? '' : 'none';
    });
});

// Função para exibir o perfil de um paciente
function showPatientProfile(patientId) {
    window.location.href = `/paciente/${patientId}`;  // Redireciona para a página do perfil
}

// Carrega a lista de pacientes ao iniciar a aba
loadPatients();
