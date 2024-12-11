// Função para criar gráfico de pizza
function criarGraficoPizza(ctx, pergunta) {
    let chart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: [],  // As labels serão preenchidas depois
            datasets: [{
                label: 'Respostas',
                data: [],
                backgroundColor: ['#36A2EB', '#FF6384', '#FFCE56'],
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            let label = context.label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += context.raw || '';
                            return label;
                        }
                    }
                },
                datalabels: { // Configuração do plugin
                    color: '#FFFFFF', // Cor do número
                    font: {
                        size: 14, // Tamanho do número
                        weight: 'bold' // Peso do número
                    },
                    textStrokeColor: '#000000', // Cor da borda (preto)
                    textStrokeWidth: 3, // Largura da borda
                    formatter: (value, ctx) => {
                        return value; // Exibe o valor
                    },
                    align: 'center', // Alinhamento (centralizado na fatia)
                    anchor: 'center' // Posição (âncora no centro da fatia)
                }
            }
        },
        plugins: [ChartDataLabels] // Adiciona o plugin
    });

    // Função para buscar os dados do backend e atualizar o gráfico
    function updateChart() {
        fetch(`/dados_grafico?pergunta=${encodeURIComponent(pergunta)}`)
            .then(response => response.json())
            .then(data => {
                chart.data.labels = data.labels;
                chart.data.datasets[0].data = data.data;
                chart.update();  // Atualiza o gráfico com novos dados
            })
            .catch(error => console.error('Erro ao buscar dados:', error));
    }

    // Atualiza o gráfico a cada 30 segundos
    setInterval(updateChart, 30000);
    updateChart();  // Carrega os dados na primeira vez
}


// Função para criar gráfico de donuts
function criarGraficoDonuts(ctx, pergunta) {
    let chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: [],  // As labels serão preenchidas depois
            datasets: [{
                label: 'Respostas',
                data: [],
                backgroundColor: ['#FF6384', '#4BC0C0', '#FFCE56'],
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            let label = context.label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += context.raw || '';
                            return label;
                        }
                    }
                },
                datalabels: { // Configuração do plugin
                    color: '#FFFFFF', // Cor do número
                    font: {
                        size: 14, // Tamanho do número
                        weight: 'bold' // Peso do número
                    },
                    textStrokeColor: '#000000', // Cor da borda (preto)
                    textStrokeWidth: 3, // Largura da borda
                    formatter: (value, ctx) => {
                        return value; // Exibe o valor
                    },
                    align: 'center', // Alinhamento (centralizado na fatia)
                    anchor: 'center' // Posição (âncora no centro da fatia)
                }
            }
        },
        plugins: [ChartDataLabels] // Adiciona o plugin
    });

    // Função para buscar os dados do backend e atualizar o gráfico
    function updateChart() {
        fetch(`/dados_grafico?pergunta=${encodeURIComponent(pergunta)}`)
            .then(response => response.json())
            .then(data => {
                chart.data.labels = data.labels;
                chart.data.datasets[0].data = data.data;
                chart.update();  // Atualiza o gráfico com novos dados
            })
            .catch(error => console.error('Erro ao buscar dados:', error));
    }

    // Atualiza o gráfico a cada 30 segundos
    setInterval(updateChart, 30000);
    updateChart();  // Carrega os dados na primeira vez
}


// Função para criar um gráfico de barras
function criarGraficoBarra(ctx, pergunta, labelX = 'Categorias', labelY = 'Número de Pessoas') {
    let chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],  // As labels serão preenchidas depois
            datasets: [{
                label: 'Respostas',
                data: [],  // Os dados serão preenchidos depois
                backgroundColor: '#36A2EB',  // Cor das barras
                borderColor: '#36A2EB',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: labelX  // Rótulo do eixo X
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: labelY  // Rótulo do eixo Y
                    }
                }
            },
            plugins: {
                legend: {
                    display: false  // Oculta a legenda
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return `Quantidade: ${context.raw}`;
                        }
                    }
                }
            }
        }
    });

    // Função para buscar os dados do backend e atualizar o gráfico
    function updateChart() {
        fetch(`/dados_grafico?pergunta=${encodeURIComponent(pergunta)}`)
            .then(response => response.json())
            .then(data => {
                // Verifica se a pergunta é "Diagnóstico" para definir uma ordem personalizada
                if (pergunta === "Diagnóstico") {
                    const desiredOrder = ['Pré-eclâmpsia', 'Pré-eclâmpsia Grave', 'Eclâmpsia Iminente'];
                    const orderedLabels = [];
                    const orderedData = [];

                    desiredOrder.forEach((label) => {
                        const index = data.labels.indexOf(label);
                        if (index !== -1) {
                            orderedLabels.push(data.labels[index]);
                            orderedData.push(data.data[index]);
                        }
                    });

                    // Atualiza os dados do gráfico com a ordem corrigida
                    chart.data.labels = orderedLabels;
                    chart.data.datasets[0].data = orderedData;
                } else {
                    // Se não for a pergunta "Diagnóstico", usa a ordem padrão dos dados
                    chart.data.labels = data.labels;
                    chart.data.datasets[0].data = data.data;
                }
                
                chart.update();  // Atualiza o gráfico com os dados processados
            })
            .catch(error => console.error('Erro ao buscar dados:', error));
    }

    // Atualiza o gráfico a cada 30 segundos
    setInterval(updateChart, 30000);
    updateChart();  // Carrega os dados na primeira vez
}


// Função para atualizar o total de usuários
function atualizarTotalUsuarios() {
    fetch('/total_usuarios')
        .then(response => response.json())
        .then(data => {
            document.getElementById('total-usuarios').textContent = data.totalUsuarios;
        })
        .catch(error => console.error('Erro ao buscar total de usuários:', error));
}

// Atualiza os dados dos cards de usuários e diagnósticos
function atualizarCards() {
    atualizarTotalUsuarios();
    fetch('/dados_correlacionados')
        .then(response => response.json())
        .then(data => {
            document.getElementById('total-pre-eclampsia').textContent = data.preEclampsia;
            document.getElementById('proteinuria-pre-eclampsia').textContent = data.proteinuria;
            document.getElementById('acido-urico-elevado').textContent = data.acidoUricoElevado;
            document.getElementById('pre-eclampsia-grave').textContent = data.preEclampsiaGrave;
            document.getElementById('eclampsia-iminente').textContent = data.eclampsiaIminente;
        })
        .catch(error => console.error('Erro ao buscar dados correlacionados:', error));
}

// Atualiza os dados dos cards a cada 30 segundos
setInterval(atualizarCards, 30000);
atualizarCards();  // Atualiza os dados na primeira vez


// Função para expandir o gráfico ao clicar no botão
function expandirGrafico(pergunta) {
    window.location.href = `/grafico_expandido?pergunta=${encodeURIComponent(pergunta)}`;
}


// Função específica para criar o gráfico na página expandida
function criarGraficoExpandido(pergunta, labels, data) {
    const ctx = document.getElementById('graficoExpandido').getContext('2d');
    let chart = new Chart(ctx, {
        type: 'pie',  // Você pode ajustar o tipo do gráfico se necessário
        data: {
            labels: labels,
            datasets: [{
                label: 'Respostas',
                data: data,
                backgroundColor: ['#36A2EB', '#FF6384', '#FFCE56'],
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            let label = context.label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += context.raw || '';
                            return label;
                        }
                    }
                },
                datalabels: { // Configuração do plugin
                    color: '#FFFFFF', // Cor do número
                    font: {
                        size: 14, // Tamanho do número
                        weight: 'bold' // Peso do número
                    },
                    textStrokeColor: '#000000', // Cor da borda (preto)
                    textStrokeWidth: 3, // Largura da borda
                    formatter: (value, ctx) => {
                        return value; // Exibe o valor
                    },
                    align: 'center', // Alinhamento (centralizado na fatia)
                    anchor: 'center' // Posição (âncora no centro da fatia)
                }
            }
        },
        plugins: [ChartDataLabels] // Adiciona o plugin
    });
}

// Código para detectar a página de gráfico expandido e renderizar o gráfico
document.addEventListener('DOMContentLoaded', function () {
    const expandidoCanvas = document.getElementById('graficoExpandido');
    if (expandidoCanvas) {
        // Se estivermos na página do gráfico expandido, obter os dados do backend e renderizar
        const pergunta = document.querySelector('h1').innerText.split(' - ')[0]; // Obtém a pergunta do título
        fetch(`/dados_grafico?pergunta=${encodeURIComponent(pergunta)}`)
            .then(response => response.json())
            .then(data => {
                criarGraficoExpandido(pergunta, data.labels, data.data);
            })
            .catch(error => console.error('Erro ao buscar dados:', error));
    }
});

// Crie os gráficos para diferentes perguntas, passando o tipo de gráfico e pergunta
const ctxPressaoArterial = document.getElementById('graficoPizzaPressaoArterial').getContext('2d');
criarGraficoPizza(ctxPressaoArterial, 'Qual foi a sua última medição de pressão arterial?');

const ctxPressao20 = document.getElementById('graficoPizzaPressao20').getContext('2d');
criarGraficoPizza(ctxPressao20, 'Sua pressão arterial elevada foi registrada antes da 20ª semana de gestação?');

const ctxPressao3 = document.getElementById('graficoPizzaPressaoEm3').getContext('2d');
criarGraficoPizza(ctxPressao3, 'Sua pressão arterial está elevada em 3 ocasiões diferentes?');

const ctxExameUrina = document.getElementById('graficoDonutsExameUrina').getContext('2d');
criarGraficoDonuts(ctxExameUrina, 'Você já fez algum exame de urina recente para verificar a presença de proteína (proteinúria)?');

const ctxProteinuria = document.getElementById('graficoBarrasProteinuria').getContext('2d');
criarGraficoBarra(ctxProteinuria, 'Qual foi o resultado do exame de urina?', 'Resultado do Exame de Urina', 'Número de Pessoas');

const ctxELevadoAcidoUrico = document.getElementById('graficoDonutsElevadoAcidoUrico').getContext('2d');
criarGraficoDonuts(ctxELevadoAcidoUrico, 'Seus exames laboratoriais indicaram níveis elevados de ácido úrico (maiores que 6mg/dl)?');

const ctxPreEclampsiaGrave = document.getElementById('graficoDonutsEclampsiaGrave').getContext('2d');
criarGraficoDonuts(ctxPreEclampsiaGrave, 'Você teve algum dos seguintes sintomas ou resultados em exames?\n(Oligúria, Creatinina elevada, Proteinúria massiva, Plaquetopenia, Aumento de TGO/TGP, Desidrogenase lática elevada)');

const ctxEclampsiaIminente = document.getElementById('graficoDonutsEclampsiaIminente').getContext('2d');
criarGraficoDonuts(ctxEclampsiaIminente, 'Você teve algum dos seguintes sintomas recentemente? (Convulsões, Perda de consciência, Confusão mental, Visão turva ou diplopia, Cefaleia intensa, Epigastralgia, Tontura, Escotomas cintilantes)');

const ctxDiagnosticos = document.getElementById('graficoBarrasDiagnosticos').getContext('2d');
criarGraficoBarra(ctxDiagnosticos, 'Diagnóstico', 'Diagnósticos', 'Número de Pacientes');
