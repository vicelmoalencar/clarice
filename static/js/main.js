var quill = new Quill('#editor', {
    theme: 'snow',
    modules: {
        toolbar: [
            [{ 'header': [1, 2, 3, false] }],
            ['bold', 'italic', 'underline', 'strike'],
            [{ 'color': [] }, { 'background': [] }],
            [{ 'align': [] }],
            ['clean'],
            ['link']
        ]
    },
    placeholder: 'Comece a escrever aqui...'
});

document.getElementById('analyzeButton').addEventListener('click', function() {
    const content = quill.root.innerHTML;
    
    // Remover tags HTML para análise
    const plainText = content.replace(/<[^>]*>/g, '');
    
    fetch('/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content: plainText })
    })
    .then(response => response.json())
    .then(data => {
        displayAnalysis(data);
        highlightIssues(data, quill);
        displaySuggestedText(data, plainText);
    })
    .catch(error => {
        console.error('Erro na análise:', error);
        alert('Erro ao analisar o texto');
    });
});

document.getElementById('saveButton').addEventListener('click', function() {
    const content = quill.root.innerHTML;
    const plainText = quill.getText();
    const title = prompt('Digite um título para o texto:');
    
    if (!title) return;

    const textData = {
        title: title,
        content: content,
        plainText: plainText,
        date: new Date().toISOString(),
        preview: plainText.slice(0, 150) + (plainText.length > 150 ? '...' : '')
    };
    
    fetch('/save', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(textData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            loadSavedTexts();
            alert('Texto salvo com sucesso!');
        } else {
            alert('Erro ao salvar o texto');
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao salvar o texto');
    });
});

function loadSavedTexts() {
    fetch('/get_saved_texts')
        .then(response => response.json())
        .then(texts => {
            const grid = document.getElementById('savedTextsGrid');
            grid.innerHTML = '';
            
            texts.forEach(text => {
                const card = createTextCard(text);
                grid.appendChild(card);
            });
        })
        .catch(error => {
            console.error('Erro ao carregar textos:', error);
        });
}

function createTextCard(text) {
    const card = document.createElement('div');
    card.className = 'text-card';
    
    const formattedDate = new Date(text.date).toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    
    card.innerHTML = `
        <div class="text-card-header">
            <h3 class="text-card-title">${text.title}</h3>
            <span class="text-card-date">${formattedDate}</span>
        </div>
        <div class="text-card-preview">${text.preview}</div>
        <div class="text-card-actions">
            <button class="text-card-button edit" data-id="${text.id}">Editar</button>
            <button class="text-card-button delete" data-id="${text.id}">Excluir</button>
        </div>
    `;
    
    // Adiciona evento de clique para expandir/recolher
    card.addEventListener('click', function(e) {
        if (!e.target.classList.contains('text-card-button')) {
            this.classList.toggle('expanded');
            const preview = this.querySelector('.text-card-preview');
            if (this.classList.contains('expanded')) {
                preview.textContent = text.plainText;
            } else {
                preview.textContent = text.preview;
            }
        }
    });
    
    // Adiciona eventos para os botões
    const editButton = card.querySelector('.edit');
    editButton.addEventListener('click', function(e) {
        e.stopPropagation();
        quill.root.innerHTML = text.content;
    });
    
    const deleteButton = card.querySelector('.delete');
    deleteButton.addEventListener('click', function(e) {
        e.stopPropagation();
        if (confirm('Tem certeza que deseja excluir este texto?')) {
            deleteText(text.id);
        }
    });
    
    return card;
}

function deleteText(textId) {
    fetch(`/delete_text/${textId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            loadSavedTexts();
        } else {
            alert('Erro ao excluir o texto');
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao excluir o texto');
    });
}

document.addEventListener('DOMContentLoaded', loadSavedTexts);

function displayAnalysis(data) {
    // Estilo
    document.getElementById('styleIssues').innerHTML = formatAnalysisText(data.style_issues);
    
    // Gramática
    document.getElementById('grammarIssues').innerHTML = formatAnalysisText(data.grammar_issues);
    
    // Legibilidade
    const readabilityScore = data.readability;
    document.getElementById('readabilityScore').innerHTML = `
        <div class="score">${readabilityScore.toFixed(1)}</div>
        <div class="score-label">${getReadabilityLabel(readabilityScore)}</div>
    `;
    
    // Palavras repetidas
    const repetitionHtml = Object.entries(data.word_repetition)
        .map(([word, count]) => `<div class="repetition-item">
            <span class="word">${word}</span>
            <span class="count">${count}x</span>
        </div>`)
        .join('');
    document.getElementById('wordRepetition').innerHTML = repetitionHtml;
    
    // Frases longas
    const longSentencesHtml = data.sentence_length
        .map(sentence => `<div class="long-sentence">${sentence}</div>`)
        .join('');
    document.getElementById('sentenceLength').innerHTML = longSentencesHtml;
    
    // Problemas de paralelismo
    document.getElementById('parallelismIssues').innerHTML = formatAnalysisText(data.parallelism_issues);
    
    // Voz passiva
    document.getElementById('passiveVoice').innerHTML = formatAnalysisText(data.passive_voice);
    
    // Sugestões de Correção
    const suggestions = [];
    
    // Adiciona sugestões baseadas em problemas gramaticais
    if (data.grammar_issues) {
        suggestions.push(...data.grammar_issues.split('\n').filter(issue => issue.trim()));
    }
    
    // Adiciona sugestões baseadas em problemas de estilo
    if (data.style_issues) {
        suggestions.push(...data.style_issues.split('\n').filter(issue => issue.trim()));
    }
    
    // Adiciona sugestões para frases longas
    data.sentence_length.forEach(sentence => {
        suggestions.push(`Considere dividir esta frase longa: "${sentence}"`);
    });
    
    // Exibe as sugestões no card
    const suggestionsHtml = suggestions.length > 0
        ? suggestions.map(suggestion => `<div class="suggestion-item">${suggestion}</div>`).join('')
        : '<div class="no-issues">Não há sugestões de correção</div>';
    
    document.getElementById('correctionSuggestions').innerHTML = suggestionsHtml;
    
    // Clichês
    document.getElementById('cliches').innerHTML = formatAnalysisText(data.cliches);
    
    // Gerúndio
    const gerundData = data.gerund_overuse;
    document.getElementById('gerundUse').innerHTML = `
        <div>Ocorrências: ${gerundData.count}</div>
        <div>Proporção: ${(gerundData.ratio * 100).toFixed(1)}%</div>
        ${gerundData.excessive ? '<div class="warning">Uso excessivo detectado</div>' : ''}
    `;
    
    // Clareza
    document.getElementById('clarity').innerHTML = formatAnalysisText(data.clarity_issues);
}

function formatAnalysisText(text) {
    if (!text) return '<div class="no-issues">Nenhum problema encontrado</div>';
    return text.split('\n').map(line => `<div>${line}</div>`).join('');
}

function getReadabilityLabel(score) {
    if (score >= 80) return 'Muito fácil de ler';
    if (score >= 70) return 'Fácil de ler';
    if (score >= 60) return 'Moderadamente fácil';
    if (score >= 50) return 'Moderado';
    if (score >= 30) return 'Difícil';
    return 'Muito difícil';
}

// Função para destacar problemas no texto
function highlightIssues(data, quill) {
    // Limpa formatações anteriores
    const text = quill.getText();
    quill.removeFormat(0, text.length);
    
    // Cores para diferentes tipos de problemas
    const colors = {
        grammar: '#ff6b6b',  // Vermelho para problemas gramaticais
        style: '#ffd93d',    // Amarelo para problemas de estilo
        longSentence: '#4dabf7', // Azul para frases longas
        passive: '#a8e6cf',  // Verde claro para voz passiva
        gerund: '#ff9f43',   // Laranja para gerúndios
        parallelism: '#b197fc' // Roxo para problemas de paralelismo
    };

    // Marca problemas gramaticais
    if (data.grammar_issues) {
        markIssues(data.grammar_issues, text, quill, { color: colors.grammar, title: 'Erro gramatical' });
    }

    // Marca problemas de estilo
    if (data.style_issues) {
        markIssues(data.style_issues, text, quill, { color: colors.style, title: 'Problema de estilo' });
    }

    // Marca frases longas
    data.sentence_length.forEach(sentence => {
        const index = text.indexOf(sentence);
        if (index !== -1) {
            quill.formatText(index, sentence.length, {
                background: colors.longSentence,
                title: 'Frase muito longa'
            });
        }
    });

    // Marca voz passiva
    if (data.passive_voice) {
        markIssues(data.passive_voice, text, quill, { color: colors.passive, title: 'Voz passiva' });
    }

    // Marca problemas de paralelismo
    if (data.parallelism_issues) {
        markIssues(data.parallelism_issues, text, quill, { color: colors.parallelism, title: 'Problema de paralelismo' });
    }
}

// Função auxiliar para marcar problemas no texto
function markIssues(issues, text, quill, format) {
    const issueList = issues.split('\n').filter(i => i.trim());
    issueList.forEach(issue => {
        // Extrai o trecho problemático do texto (assumindo que está entre aspas ou é a primeira palavra)
        const match = issue.match(/"([^"]+)"/) || issue.match(/^(\w+)/);
        if (match) {
            const problematicText = match[1];
            let index = text.indexOf(problematicText);
            while (index !== -1) {
                quill.formatText(index, problematicText.length, {
                    background: format.color,
                    title: format.title
                });
                index = text.indexOf(problematicText, index + 1);
            }
        }
    });
}

// Função para exibir texto com sugestões de correção
function displaySuggestedText(data, originalText) {
    // Cria o HTML para exibir o texto corrigido
    const correctedTextHtml = `
        <div class="corrected-text-container">
            <h3>Texto Corrigido</h3>
            <div class="corrected-text">${data.corrected_text}</div>
            <div class="corrections-legend">
                <h4>Legenda das Marcações no Texto Original:</h4>
                <div class="legend-item">
                    <span class="color-sample" style="background: #ff6b6b"></span>
                    <span>Erro gramatical</span>
                </div>
                <div class="legend-item">
                    <span class="color-sample" style="background: #ffd93d"></span>
                    <span>Problema de estilo</span>
                </div>
                <div class="legend-item">
                    <span class="color-sample" style="background: #4dabf7"></span>
                    <span>Frase longa</span>
                </div>
                <div class="legend-item">
                    <span class="color-sample" style="background: #a8e6cf"></span>
                    <span>Voz passiva</span>
                </div>
                <div class="legend-item">
                    <span class="color-sample" style="background: #b197fc"></span>
                    <span>Problema de paralelismo</span>
                </div>
            </div>
        </div>
    `;

    // Adiciona o texto corrigido ao painel de análise
    const correctedTextElement = document.createElement('div');
    correctedTextElement.className = 'analysis-section';
    correctedTextElement.innerHTML = correctedTextHtml;
    
    // Remove qualquer versão anterior do texto corrigido
    const existingCorrectedText = document.querySelector('.corrected-text-container');
    if (existingCorrectedText) {
        existingCorrectedText.parentElement.remove();
    }
    
    // Adiciona o novo texto corrigido no topo do painel de análise
    document.getElementById('analysisPanel').insertBefore(
        correctedTextElement,
        document.getElementById('analysisPanel').firstChild
    );
}
