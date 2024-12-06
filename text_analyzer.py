import os
from openai import OpenAI
import textstat
import re
from collections import Counter
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class TextAnalyzer:
    def __init__(self):
        pass

    def analyze_text(self, text):
        if not text.strip():
            return {
                'error': 'O texto está vazio. Por favor, insira algum conteúdo para análise.'
            }

        try:
            analysis = {
                'style_issues': self._check_style(text),
                'grammar_issues': self._check_grammar(text),
                'readability': self._check_readability(text),
                'word_repetition': self._check_word_repetition(text),
                'sentence_length': self._check_sentence_length(text),
                'passive_voice': self._check_passive_voice(text),
                'cliches': self._check_cliches(text),
                'gerund_overuse': self._check_gerund_overuse(text),
                'clarity_issues': self._check_clarity(text),
                'parallelism_issues': self._check_parallelism(text)
            }
            
            # Gera o texto corrigido com base na análise
            analysis['corrected_text'] = self._generate_corrected_text(text, analysis)
            
            return analysis
        except Exception as e:
            return {
                'error': str(e)
            }

    def _check_style(self, text):
        prompt = (
            f"Analise o texto abaixo em português, identificando e explicando desvios de estilo. "
            f"Certifique-se de abordar os seguintes aspectos:\n"
            f"- Presença de vícios de linguagem.\n"
            f"- Uso de palavras vazias ou desnecessárias.\n"
            f"- Escolha inadequada de palavras (complexidade excessiva ou inadequação ao contexto).\n"
            f"- Emprego de substantivos rastejantes.\n\n"
            f"Texto: {text}"
        )
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def _check_grammar(self, text):
        prompt = (
            f"Analise o texto abaixo em português, identificando erros gramaticais, "
            f"incluindo problemas ortográficos, de concordância, regência, e pontuação:\n\n"
            f"Texto: {text}"
        )
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def _check_readability(self, text):
        try:
            return textstat.flesch_reading_ease(text)
        except:
            return 0

    def _check_word_repetition(self, text):
        words = [word.lower() for word in re.findall(r'\w+', text)]
        word_freq = Counter(words)
        return {word: count for word, count in word_freq.items() if count > 2}

    def _check_sentence_length(self, text):
        sentences = re.split(r'[.!?]+', text)
        long_sentences = [sent.strip() for sent in sentences if len(sent.split()) > 20]
        return long_sentences

    def _check_passive_voice(self, text):
        prompt = (
            f"Analise o uso de voz passiva no texto abaixo, indicando exemplos claros e sugerindo "
            f"alternativas em voz ativa, caso aplicável:\n\n"
            f"Texto: {text}"
        )
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def _check_cliches(self, text):
        prompt = (
            f"Identifique o uso de clichês e expressões desgastadas no texto abaixo, explicando "
            f"por que são inadequadas e sugerindo substituições mais criativas ou precisas:\n\n"
            f"Texto: {text}"
        )
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def _check_gerund_overuse(self, text):
        gerund_count = len(re.findall(r'\w+ndo\b', text))
        words = text.split()
        gerund_ratio = gerund_count / len(words) if words else 0
        return {
            'count': gerund_count,
            'ratio': gerund_ratio,
            'excessive': gerund_ratio > 0.1
        }

    def _check_clarity(self, text):
        prompt = (
            f"Analise a clareza do texto abaixo, identificando problemas como:\n"
            f"- Ambiguidades que dificultam a compreensão.\n"
            f"- Falta de coesão entre as ideias.\n"
            f"- Frases ou parágrafos mal conectados.\n"
            f"- Presença de cacofonias ou repetições sonoras.\n\n"
            f"Texto: {text}"
        )
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def _check_parallelism(self, text):
        prompt = (
            f"Analise o texto abaixo em busca de problemas de paralelismo sintático e semântico. "
            f"Identifique casos onde:\n"
            f"- Elementos coordenados não mantêm a mesma estrutura gramatical\n"
            f"- Listas ou enumerações não seguem o mesmo padrão sintático\n"
            f"- Tempos verbais mudam sem justificativa dentro da mesma estrutura\n"
            f"- Há quebra de paralelismo em expressões correlativas (não só... mas também, tanto... quanto)\n\n"
            f"Para cada problema encontrado, indique:\n"
            f"1. O trecho com problema\n"
            f"2. Por que há falta de paralelismo\n"
            f"3. Uma sugestão de correção\n\n"
            f"Texto: {text}"
        )
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def _generate_corrected_text(self, text, analysis_results):
        prompt = (
            f"Reescreva o texto abaixo corrigindo todos os problemas identificados:\n\n"
            f"Problemas encontrados:\n"
            f"1. Problemas gramaticais: {analysis_results['grammar_issues']}\n"
            f"2. Problemas de estilo: {analysis_results['style_issues']}\n"
            f"3. Problemas de clareza: {analysis_results['clarity_issues']}\n"
            f"4. Uso de voz passiva: {analysis_results['passive_voice']}\n"
            f"5. Clichês: {analysis_results['cliches']}\n"
            f"6. Problemas de paralelismo: {analysis_results['parallelism_issues']}\n\n"
            f"Texto original:\n{text}\n\n"
            f"Por favor, forneça uma versão completamente reescrita do texto que corrija todos "
            f"estes problemas, mantendo o significado original mas melhorando a clareza, "
            f"concisão e impacto. Mantenha o mesmo tom do texto original, apenas corrigindo "
            f"os problemas identificados."
        )
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
