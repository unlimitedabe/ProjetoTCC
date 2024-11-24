// scripts_general.js
function showTab(tabId) {
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => tab.style.display = 'none');
    document.getElementById(`tab-${tabId}`).style.display = 'block';

    // Alternar a classe 'active' nos botões
    const buttons = document.querySelectorAll('nav button');
    buttons.forEach(button => {
        button.classList.remove('active'); // Remove a classe de todos os botões
    });
    document.querySelector(`nav button[onclick="showTab('${tabId}')"]`).classList.add('active'); // Adiciona a classe no botão ativo
}