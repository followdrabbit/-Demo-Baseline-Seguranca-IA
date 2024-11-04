```markdown
# Gerador de Baselines de Segurança com I.A.

Este projeto utiliza o [Streamlit](https://streamlit.io/) e a API da [OpenAI](https://openai.com/) para gerar baselines de segurança automatizados para serviços de tecnologia. A aplicação permite selecionar vendors e tecnologias específicas para consultar conteúdos da web, consolidá-los em Markdown, e gerar um documento HTML final.

## Funcionalidades

- **Seleção de Vendors e Tecnologias**: Carrega configurações para os vendors AWS e Azure, permitindo selecionar tecnologias específicas.
- **Geração de ID Único**: Gera um ID baseado no vendor, tecnologia, classificação, ano e revisão.
- **Processamento de URLs**: Extrai conteúdo de URLs, converte para Markdown e salva com cabeçalho de referência.
- **Integração com OpenAI**: Usa a API da OpenAI para processar e consolidar conteúdos, gerando baselines personalizados.
- **Exportação de Documentos**: Converte o conteúdo consolidado em uma página HTML para download.
- **Limpeza de Arquivos Temporários**: Remove arquivos gerados após o download, mantendo o ambiente limpo.

## Estrutura de Arquivos

- `config.toml`: Arquivo de configuração com informações dos vendors e tecnologias.
- `template_html.html`: Template para gerar a página HTML final.
- `prompt_criacao.txt` e `prompt_consolidacao.txt`: Arquivos de prompt para instruções do assistente.

## Configuração Inicial

1. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```
   
2. **Configure o arquivo `config.toml`** com a chave da OpenAI e URLs para as tecnologias desejadas:
   ```toml
   [openai]
   openai_key = "sua_chave_openai"

   [AWS]
   classificacao = "cloud"
   urls = ["https://url_da_aws"]

   [Azure]
   classificacao = "cloud"
   urls = ["https://url_da_azure"]
   ```

## Como Executar

1. **Inicie o Streamlit**:
   ```bash
   streamlit run main.py
   ```

2. **Use a Interface**: 
   - Selecione o vendor e tecnologia.
   - Clique em "Gerar Baseline" para processar URLs, gerar IDs e executar o assistente OpenAI.
   - Baixe o arquivo HTML gerado com o botão "Baixar Página Web".

## Funções Principais

- `gerar_id_unico()`: Gera um ID único com base nas informações fornecidas.
- `setup_openai_client()`: Configura o cliente da API OpenAI.
- `fetch_page_content()`: Extrai conteúdo HTML de URLs.
- `html_to_markdown()`: Converte HTML em Markdown.
- `execute_assistant_thread()`: Executa o assistente da OpenAI e armazena as respostas.
- `generate_html_page()`: Gera uma página HTML a partir de um template e conteúdo consolidado.
- `cleanup_generated_files()`: Limpa arquivos temporários após o download.

## Observações

- **Arquivo `config.toml`**: Certifique-se de incluir suas chaves de API e URLs corretamente.
- **Cleanup Automático**: Todos os arquivos gerados são removidos após o download do HTML para otimizar o uso do armazenamento.
  
## Requisitos

- Python 3.12 ou superior
- Chave de API da OpenAI

## Licença

Este projeto é disponibilizado sob a licença MIT. Consulte o arquivo `LICENSE` para mais detalhes.