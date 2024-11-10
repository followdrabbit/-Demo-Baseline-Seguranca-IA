# Imports necessários
import streamlit as st
from datetime import datetime
import toml
import requests
import os
import html2text
from openai import OpenAI
import time
import markdown
from bs4 import BeautifulSoup
from jinja2 import Template
import uuid

# Função para carregar o arquivo config.toml
def carregar_config():
    try:
        return toml.load("config.toml")
    except toml.TomlDecodeError as e:
        st.error(f"Erro ao carregar config.toml: {e}")
        return None

# Configuração inicial
config = carregar_config()
if not config:
    st.stop()  # Interrompe a execução se o config.toml não carregar corretamente

# Carregar a lista de categorias
categorias = config.get("Categories", {}).get("items", [])
if not categorias:
    st.warning("Nenhuma categoria encontrada no arquivo config.toml.")

ARTIFACTS_DIRECTORY = "artefatos"
section_id = str(uuid.uuid4())  # Gera um UUID único para cada execução

DIRECTORY_MD = os.path.join(ARTIFACTS_DIRECTORY, f"paginas_md_{section_id}")
DIRECTORY_HTML = os.path.join(ARTIFACTS_DIRECTORY, f"paginas_baixadas_{section_id}")
OUTPUT_FILE = os.path.join(ARTIFACTS_DIRECTORY, f"gerados_{section_id}.txt")
FINAL_OUTPUT_FILE = os.path.join(ARTIFACTS_DIRECTORY, f"consolidados_{section_id}.md")
DOC_VERSION = 1
template_file_path = "template_html.html"


# Função para carregar textos com base no idioma selecionado
def carregar_textos(idioma):
    try:
        return config["MENU"][idioma]
    except KeyError:
        st.error(f"Erro: idioma '{idioma}' não encontrado no config.toml.")
        return None

# Função para gerar o ID único com o novo padrão
def gerar_id_unico(vendor: str, categoria: str, tecnologia: str, versao: str, ano: int, revisao: int) -> str:
    return f"{vendor}.{categoria}.{tecnologia}.{versao}.{ano}.r{revisao}".replace("..", ".")  # Remover duplo ponto

# Função para carregar os prompts com base no idioma
def carregar_prompts(idioma):
    arquivos_prompts = {
        'PT-BR': ("prompt_criacao_pt.txt", "prompt_consolidacao_pt.txt"),
        'EN-US': ("prompt_criacao_en.txt", "prompt_consolidacao_en.txt"),
        'ES-ES': ("prompt_criacao_es.txt", "prompt_consolidacao_es.txt"),
    }
    if idioma not in arquivos_prompts:
        st.error("Idioma não suportado.")
        return None, None

    arquivo_criacao, arquivo_consolidacao = arquivos_prompts[idioma]
    try:
        with open(arquivo_criacao, "r") as f:
            prompt_criacao = f.read()
        with open(arquivo_consolidacao, "r") as f:
            prompt_consolidacao = f.read()
    except FileNotFoundError as e:
        st.error(f"Erro: {e}")
        return None, None

    return prompt_criacao, prompt_consolidacao

def setup_openai_client():
    openai_key = st.secrets["OpenAI_key"]  # Busca a chave de API do OpenAI em st.secrets
    if not openai_key:
        st.error("Chave da API OpenAI não encontrada em secrets.toml.")
        return None
    return OpenAI(api_key=openai_key)

# Função para garantir a criação de diretórios
def ensure_directory_exists(directory):
    os.makedirs(directory, exist_ok=True)

# Função para salvar conteúdo em arquivo
def save_file(content, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)

# Função para anexar conteúdo a um arquivo
def append_to_file(content, file_path):
    with open(file_path, "a", encoding="utf-8") as file:
        file.write(content + "\n")

# Função para carregar conteúdo de um arquivo
def load_file_content(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        st.write(f"Erro ao carregar arquivo {file_path}: {e}")
        return None

# Função para baixar conteúdo de URL
def fetch_page_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        st.write(f"Erro ao acessar {url}: {e}")
        return None

# Função para limpar arquivos temporários específicos ao `section_id`
def cleanup_generated_files():
    st.write("Removendo arquivos temporários:")
    try:
        # Primeiro remove todos os arquivos dentro dos diretórios
        for root, dirs, files in os.walk(ARTIFACTS_DIRECTORY, topdown=False):
            for file in files:
                if section_id in file:
                    file_path = os.path.join(root, file)
                    os.remove(file_path)
                    st.write(f"Arquivo removido: {file_path}")

            # Em seguida, remove os diretórios se estiverem vazios
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                if section_id in dir:
                    try:
                        os.rmdir(dir_path)
                        st.write(f"Diretório removido: {dir_path}")
                    except OSError as e:
                        st.write(f"Erro ao remover diretório {dir_path}: {e}")

        st.write("------> Todos os arquivos e diretórios temporários foram removidos.")
    except Exception as e:
        st.error(f"Erro ao limpar arquivos: {e}")

# Função para converter HTML para Markdown
def html_to_markdown(html_content):
    converter = html2text.HTML2Text()
    converter.ignore_links = False
    return converter.handle(html_content)

# Função para processar URLs e salvar como Markdown com cabeçalho de referência e `section_id`
def process_urls_to_markdown(urls):
    st.write("Baixando conteúdo das URLs fornecidas")
    for url in urls:
        html_content = fetch_page_content(url)
        if html_content:
            markdown_content = html2text.HTML2Text().handle(html_content)
            header = f"Reference: {url}\n\n\n{markdown_content}"
            ensure_directory_exists(DIRECTORY_MD)
            unique_filename = f"{url.replace('https://', '').replace('http://', '').replace('/', '_')}_{section_id}.md"
            file_path = os.path.join(DIRECTORY_MD, unique_filename)
            save_file(header, file_path)
            st.write(f"Conteúdo Markdown salvo em {file_path}")

# Função para carregar todos os arquivos Markdown gerados
def load_markdown_files():
    st.write(f"Carregando páginas baixadas:")
    content_dict = {}
    if os.path.exists(DIRECTORY_MD):
        for file_name in os.listdir(DIRECTORY_MD):
            if file_name.endswith(".md"):
                file_path = os.path.join(DIRECTORY_MD, file_name)
                content = load_file_content(file_path)
                if content:
                    content_dict[file_name] = content
                    st.write(f"------> Conteúdo carregado de {file_name}")
    else:
        st.write(f"Diretório {DIRECTORY_MD} não encontrado.")
    return content_dict

# Função para encontrar ou criar assistente no OpenAI
def find_or_create_assistant(client, assistant_info):
    try:
        st.write(f"Verificando se o assistente '{assistant_info['name']}' existe:")
        assistants = client.beta.assistants.list(order="desc", limit=20)
        for assistant in assistants.data:
            if assistant.name == assistant_info["name"]:
                st.write(f"------> Assistente '{assistant_info['name']}': OK.")
                return assistant.id
        st.write(f"------> Assistente'{assistant_info['name']}': NOK.")
        st.write(f"Criando assistente'{assistant_info['name']}':")
        new_assistant = client.beta.assistants.create(
            instructions=assistant_info["instructions"],
            name=assistant_info["name"],
            tools=assistant_info["tools"],
            model=assistant_info["model"]
        )
        st.write(f"------> Assistente '{assistant_info['name']}': Criado.")
        return new_assistant.id
    except Exception as e:
        st.write(f"Erro ao criar ou recuperar assistente: {e}")
        return None

# Função para executar assistente da OpenAI
def execute_assistant_thread(client, content, assistant_id, output_file):
    try:
        thread = client.beta.threads.create()
        client.beta.threads.messages.create(thread.id, role="user", content=content)
        run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant_id)
        
        while True:
            run_status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id).status
            if run_status == "completed":
                messages = client.beta.threads.messages.list(thread_id=thread.id)
                responses = [msg.content[0].text.value for msg in messages if msg.role == "assistant"]
                for response in responses:
                    append_to_file(response, output_file)
                st.write(f"------------> Respostas salvas em {output_file}")
                return responses
            elif run_status in ["queued", "in_progress"]:
                st.write(f"------> Aguardando processamento, status de execução: {run_status}")
                time.sleep(3)
            else:
                break
    except Exception as e:
        st.write(f"Erro ao executar thread do assistente: {e}")
        return None

# Função para consolidar e enviar ao assistente
def consolidate_and_send_to_assistant(client, assistant_id):
    prompt_consolidacao_content = load_file_content(prompt_consolidacao)
    controles_gerados_content = load_file_content(OUTPUT_FILE)
    if prompt_consolidacao_content and controles_gerados_content:
        combined_content = f"{prompt_consolidacao_content}\n\n{controles_gerados_content}"
        st.write("Consolidando controles com ajuda da OpenAI")
        execute_assistant_thread(client, combined_content, assistant_id, FINAL_OUTPUT_FILE)


# Função para converter Markdown em HTML e gerar uma tabela HTML
def markdown_to_html_table(md_content, idioma):
    # Carrega os rótulos do config.toml de acordo com o idioma selecionado
    config = toml.load("config.toml")
    labels = config["tabela_labels"].get(idioma, {})
    
    # Verifica se o idioma possui rótulos definidos
    if not labels:
        st.error("Erro: Idioma não suportado ou rótulos ausentes no config.toml.")
        return "<p>Erro na conversão de Markdown para tabela HTML.</p>"

    # Converte o conteúdo Markdown em HTML
    html_content = markdown.markdown(md_content)
    soup = BeautifulSoup(html_content, "html.parser")
    controls = []

    # Extrai os campos de cada controle no Markdown
    for ul in soup.find_all("ul"):
        control = {}
        for li in ul.find_all("li"):
            strong_tag = li.find("strong")
            if strong_tag:
                key = strong_tag.get_text(strip=True).replace(":", "")
                value = li.get_text(strip=True).replace(f"{key}:", "").strip()
                control[key] = value
        if control:
            controls.append(control)

    if not controls:
        st.error("Erro: Não foi possível extrair dados dos controles do conteúdo Markdown.")
        return "<p>Erro na conversão de Markdown para tabela HTML.</p>"

    # Gera a tabela HTML com os rótulos carregados
    table_html = (
        f"<table>\n<tr><th>{labels['nome_controle']}</th>"
        f"<th>{labels['id_controle']}</th>"
        f"<th>{labels['justificativa']}</th>"
        f"<th>{labels['riscos_mitigados']}</th>"
        f"<th>{labels['criticidade']}</th>"
        f"<th>{labels['referencias']}</th></tr>\n"
    )
    for control in controls:
        table_html += "<tr>"
        table_html += f"<td>{control.get(labels['nome_controle'], '')}</td>"
        table_html += f"<td>{control.get(labels['id_controle'], '')}</td>"
        table_html += f"<td>{control.get(labels['justificativa'], '')}</td>"
        table_html += f"<td>{control.get(labels['riscos_mitigados'], '')}</td>"
        table_html += f"<td>{control.get(labels['criticidade'], '')}</td>"
        table_html += f"<td>{control.get(labels['referencias'], '')}</td>"
        table_html += "</tr>\n"
    table_html += "</table>"

    return table_html

# Função para carregar o conteúdo de um arquivo
def load_file_content(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {e}")
        return None

# Função para gerar uma página HTML a partir de um template e conteúdo consolidado
def generate_html_page(template_path, markdown_path, output_html_path, idioma):
    # Ler o conteúdo do arquivo consolidado de controles em Markdown
    markdown_content = load_file_content(markdown_path)
    if markdown_content is None:
        st.error("Erro ao carregar o conteúdo do arquivo Markdown.")
        return None

    # Converter o conteúdo Markdown para uma tabela HTML, passando o idioma
    table_html = markdown_to_html_table(markdown_content, idioma)

    # Ler o template HTML
    html_template = load_file_content(template_path)
    if html_template is None:
        st.error("Erro ao carregar o template HTML.")
        return None

    # Usar o template com Jinja2 para renderizar a tabela
    template = Template(html_template)
    final_html = template.render(table_content=table_html)

    # Salvar o HTML final no arquivo de saída
    try:
        with open(output_html_path, "w", encoding="utf-8") as file:
            file.write(final_html)
        return final_html  # Retorna o conteúdo HTML para download
    except Exception as e:
        st.error(f"Erro ao salvar o arquivo HTML: {e}")
        return None
    
# Interface do Streamlit
st.title("Gerador de Baselines de Segurança com I.A.")

# Verificar e exibir a lista de categorias

# Opção de seleção do idioma
idioma_selecionado = st.selectbox(
    config["MENU"]["EN-US"]["language_selection"],  # Título multilíngue para seleção de idioma
    ("EN-US", "PT-BR", "ES-ES")
)

# Carregar os textos do idioma selecionado
textos = carregar_textos(idioma_selecionado)
if not textos:
    st.stop()  # Interrompe a execução se os textos do idioma não forem carregados

# Carregar os prompts com base na seleção do idioma
prompt_criacao, prompt_consolidacao = carregar_prompts(idioma_selecionado)

# Campos da interface com os textos obtidos do arquivo config.toml
vendor = st.selectbox(textos["select_vendor"], ["AWS", "Azure"])
tecnologia = st.text_input(textos["enter_technology_name"])
versao = st.text_input(textos["enter_technology_version"], "Static")
categoria = st.selectbox(textos["select_category"], ["Selecione uma categoria"] + categorias) # Carregar e exibir categorias

# Verificação adicional para depuração
if not categorias:
    st.warning("A lista de categorias está vazia. Verifique se a chave 'Categories' está correta no arquivo config.toml.")

# Campo para URLs
urls_input = st.text_area(textos["enter_urls"], "")
urls = [url.strip() for url in urls_input.split(",") if url.strip()]

# Ano atual e formulário para revisão e geração de ID
ano_atual = datetime.now().year
with st.form("Formulário de ID"):
    submit_button = st.form_submit_button(textos["generate_baseline"])

# Processamento ao clicar em "Gerar ID"
if submit_button:
    if vendor and tecnologia and categoria != "Selecione uma categoria" and versao and urls:
        if len(urls) > 10:
            st.error("Por favor, insira no máximo 10 URLs.")
        else:
            st.write(f"Categoria da Tecnologia: {categoria}")
            st.write("URLs carregadas:")
            for url in urls:
                st.write(url)

            id_unico = gerar_id_unico(vendor, categoria, tecnologia, versao, ano_atual, DOC_VERSION)
            st.success(f"O ID único gerado é: {id_unico}")

            # Processar URLs e salvar como Markdown
            process_urls_to_markdown(urls)

            # Carregar cliente OpenAI e executar o assistente
            client = setup_openai_client()
            if client:
                assistant_info = {
                    "instructions": "Você é um Especialista em Segurança Cibernética focado em desenvolver baselines de segurança para serviços e produtos da AWS.",
                    "name": "CyberSecurityAssistant",
                    "tools": [{"type": "code_interpreter"}],
                    "model": "gpt-4o"
                }
                assistant_id = find_or_create_assistant(client, assistant_info)

                # Executar assistente para cada URL processada com prompt específico ao idioma
                markdown_contents = load_markdown_files()
                if prompt_criacao and assistant_id:
                    for filename, content in markdown_contents.items():
                        combined_content = (
                            f"ID: {id_unico}\nVendor: {vendor}\nTecnologia: {tecnologia}\nVersão: {versao}\n\n"
                            f"{prompt_criacao}\n\n{content}"
                        )
                        st.write(f"Extraindo controles com ajuda da OpenAI:")
                        execute_assistant_thread(client, combined_content, assistant_id, OUTPUT_FILE)

                    # Consolidação final e envio ao assistente usando o prompt de consolidação específico ao idioma
                    if prompt_consolidacao:
                        combined_content = f"{prompt_consolidacao}\n\n{load_file_content(OUTPUT_FILE)}"
                        execute_assistant_thread(client, combined_content, assistant_id, FINAL_OUTPUT_FILE)

                    # Gerar a página HTML final e permitir download
                    output_html_file_path = os.path.join(ARTIFACTS_DIRECTORY, f"{id_unico}_controles.html")
                    html_content = generate_html_page(template_file_path, FINAL_OUTPUT_FILE, output_html_file_path, idioma_selecionado)

                    if html_content:
                        download_button_clicked = st.download_button(
                            label="Baixar Página Web",
                            data=html_content,
                            file_name=f"{id_unico}_controles.html",
                            mime="text/html"
                        )

                    # Executar cleanup
                    cleanup_generated_files()

    else:
        st.error("Por favor, preencha todos os campos para gerar o ID.")