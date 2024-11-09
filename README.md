# Gerador de Baselines de Segurança com I.A.

Este projeto utiliza o [Streamlit](https://streamlit.io/) e a API da [OpenAI](https://openai.com/) para gerar baselines de segurança automatizados para serviços de tecnologia. A aplicação permite selecionar vendors, tecnologias específicas e idioma do documento para consultar conteúdos da web, consolidá-los em Markdown e gerar um documento HTML final.

## Funcionalidades

- **Seleção de Vendors, Tecnologias e Idiomas**: Carrega configurações para os vendors AWS e Azure, permitindo selecionar tecnologias específicas e o idioma do documento (PT-BR, EN-US, ES-ES).
- **Geração de ID Único**: Gera um ID único com base no vendor, tecnologia, classificação, versão, ano e revisão.
- **Processamento de URLs**: Extrai conteúdo de até 10 URLs, converte para Markdown e salva com cabeçalho de referência e UUID exclusivo para cada execução.
- **Integração com OpenAI**: Usa a API da OpenAI para processar e consolidar conteúdos com prompts personalizados conforme o idioma, gerando baselines específicos.
- **Exportação de Documentos**: Converte o conteúdo consolidado em uma página HTML multilíngue e organizada para download.
- **Limpeza de Arquivos Temporários por Sessão**: Remove arquivos gerados por sessão após o download, mantendo o ambiente limpo e organizado.

## Estrutura de Arquivos

- `config.toml`: Arquivo de configuração com informações dos vendors, tecnologias e rótulos de tabela para diferentes idiomas.
- `template_html.html`: Template para gerar a página HTML final.
- `prompt_criacao_[idioma].txt` e `prompt_consolidacao_[idioma].txt`: Arquivos de prompt para instruções do assistente, disponíveis em múltiplos idiomas.
- `secrets.toml`: Arquivo com chave da OpenAI.

## Configuração Inicial

1. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```
   
2. **Crie o arquivo `secrets.toml`** com a chave da OpenAI:
   ```toml
   [openai]
   openai_key = "sua_chave_openai"
   ```

## Como Executar

1. **Inicie o Streamlit**:
   ```bash
   streamlit run main.py
   ```

2. **Use a Interface**: 
   - Selecione o idioma, vendor, tecnologia e classificação.
   - Insira as URLs para consulta (até 10 URLs).
   - Clique em "Gerar Baseline" para processar URLs, gerar ID e executar o assistente OpenAI.
   - Baixe o arquivo HTML gerado com o botão "Baixar Página Web".

## Funções Principais

- `gerar_id_unico()`: Gera um ID único com base nas informações fornecidas, incluindo versão e idioma.
- `setup_openai_client()`: Configura o cliente da API OpenAI.
- `fetch_page_content()`: Extrai conteúdo HTML de URLs.
- `html_to_markdown()`: Converte HTML em Markdown.
- `execute_assistant_thread()`: Executa o assistente da OpenAI e armazena as respostas.
- `generate_html_page()`: Gera uma página HTML a partir de um template e conteúdo consolidado com suporte a idiomas.
- `cleanup_generated_files()`: Limpa arquivos temporários específicos ao UUID da sessão após o download.

## Requisitos

- Python 3.12 ou superior
- Chave de API da OpenAI

## Licença

Este projeto é disponibilizado sob a licença MIT. Consulte o arquivo `LICENSE` para mais detalhes.

## TO DO:

- [ ] Unificar lista de categorias e adicionar categorias faltantes