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

# Configuração inicial
config = toml.load("config.toml")
# Carregar apenas a lista de classificações para produtos AWS e Azure
aws_classificacoes = config.get("AWS", {}).get("classificacoes", [])
azure_classificacoes = config.get("Azure", {}).get("classificacoes", [])
classificacoes = aws_classificacoes + azure_classificacoes

ARTIFACTS_DIRECTORY = "artefatos"
section_id = str(uuid.uuid4())  # Gera um UUID único para cada execução

DIRECTORY_MD = os.path.join(ARTIFACTS_DIRECTORY, f"paginas_md_{section_id}")
DIRECTORY_HTML = os.path.join(ARTIFACTS_DIRECTORY, f"paginas_baixadas_{section_id}")
PROMPT_BASELINE_PATH = "prompt_criacao.txt"
PROMPT_CONSOLIDACAO_PATH = "prompt_consolidacao.txt"
OUTPUT_FILE = os.path.join(ARTIFACTS_DIRECTORY, f"gerados_{section_id}.txt")
FINAL_OUTPUT_FILE = os.path.join(ARTIFACTS_DIRECTORY, f"consolidados_{section_id}.md")
DOC_VERSION = 1
template_file_path = "template_html.html"


# Função para gerar o ID único com o novo padrão
def gerar_id_unico(vendor: str, classificacao: str, tecnologia: str, versao: str, ano: int, revisao: int) -> str:
    return f"{vendor}.{classificacao}.{tecnologia}.{versao}.{ano}.r{revisao}".replace("..", ".")  # Remover duplo ponto



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
    prompt_consolidacao_content = load_file_content(PROMPT_CONSOLIDACAO_PATH)
    controles_gerados_content = load_file_content(OUTPUT_FILE)
    if prompt_consolidacao_content and controles_gerados_content:
        combined_content = f"{prompt_consolidacao_content}\n\n{controles_gerados_content}"
        st.write("Consolidando controles com ajuda da OpenAI")
        execute_assistant_thread(client, combined_content, assistant_id, FINAL_OUTPUT_FILE)


# Função para converter conteúdo Markdown em HTML e gerar uma tabela HTML
def markdown_to_html_table(md_content):
    html_content = markdown.markdown(md_content)
    soup = BeautifulSoup(html_content, "html.parser")
    controls = []

    for ul in soup.find_all("ul"):
        control = {}
        for li in ul.find_all("li"):
            key = li.strong.get_text(strip=True).replace(":", "")
            value = li.get_text(strip=True).replace(f"{key}:", "").strip()
            control[key] = value
        controls.append(control)

    # Criando a tabela HTML
    table_html = "<table>\n<tr><th>Nome do Controle</th><th>ID do Controle</th><th>Justificativa</th><th>Riscos Mitigados</th><th>Criticidade</th><th>Referências</th></tr>\n"
    for control in controls:
        table_html += "<tr>"
        table_html += f"<td>{control.get('Nome do Controle', '')}</td>"
        table_html += f"<td>{control.get('ID do Controle', '')}</td>"
        table_html += f"<td>{control.get('Justificativa', '')}</td>"
        table_html += f"<td>{control.get('Riscos Mitigados', '')}</td>"
        table_html += f"<td>{control.get('Criticidade', '')}</td>"
        table_html += f"<td>{control.get('Referências', '')}</td>"
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
def generate_html_page(template_path, markdown_path, output_html_path):
    # Ler o conteúdo do arquivo consolidado de controles em Markdown
    markdown_content = load_file_content(markdown_path)
    if markdown_content is None:
        st.error("Erro ao carregar o conteúdo do arquivo Markdown.")
        return None

    # Converter o conteúdo Markdown para uma tabela HTML
    table_html = markdown_to_html_table(markdown_content)

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

# Seleção do vendor, tecnologia e classificação
vendor = st.selectbox("Selecione o Vendor", ["AWS", "Azure"])
tecnologia = st.text_input("Digite o nome da Tecnologia")
versao = st.text_input("Digite a versão da tecnologia (ou deixe com valor padrão 'Static' se a tecnologia não possuir versão)", "Static")  # "none" como padrão
classificacao = st.selectbox("Selecione a classificação", ["Selecione uma classificação"] + classificacoes)

# Campo para URLs
urls_input = st.text_area("Digite até 10 URLs separadas por vírgulas", "")
urls = [url.strip() for url in urls_input.split(",") if url.strip()]

# Ano atual e formulário para revisão e geração de ID
ano_atual = datetime.now().year
with st.form("Formulário de ID"):
    submit_button = st.form_submit_button("Gerar Baseline")

# Processamento ao clicar em "Gerar ID"
if submit_button:
    if vendor and tecnologia and classificacao != "Selecione uma classificação" and versao and urls:
        if len(urls) > 10:
            st.error("Por favor, insira no máximo 10 URLs.")
        else:
            st.write(f"Classificação da Tecnologia: {classificacao}")
            st.write("URLs carregadas:")
            for url in urls:
                st.write(url)

            id_unico = gerar_id_unico(vendor, classificacao, tecnologia, versao, ano_atual, DOC_VERSION)
            st.success(f"O ID único gerado é: {id_unico}")

            # Configuração dos caminhos de saída
            OUTPUT_FILE = os.path.join(ARTIFACTS_DIRECTORY, f"gerados.{id_unico}.{section_id}.txt")
            FINAL_OUTPUT_FILE = os.path.join(ARTIFACTS_DIRECTORY, f"consolidados.{id_unico}.{section_id}.md")
            
        # Processar URLs e salvar como Markdown
        process_urls_to_markdown(urls)

        # Carregar cliente OpenAI e executar o assistente
        client = setup_openai_client()
        assistant_info = {
            "instructions": "Você é um Especialista em Segurança Cibernética focado em desenvolver baselines de segurança para serviços e produtos da AWS.",
            "name": "CyberSecurityAssistant",
            "tools": [{"type": "code_interpreter"}],
            "model": "gpt-4o"
        }
        assistant_id = find_or_create_assistant(client, assistant_info)

        # Executar assistente para cada URL processada
        markdown_contents = load_markdown_files()
        prompt_content = load_file_content(PROMPT_BASELINE_PATH)
        
        if prompt_content and assistant_id:
            for filename, content in markdown_contents.items():
                combined_content = (
                    f"ID: {id_unico}\nVendor: {vendor}\nTecnologia: {tecnologia}\nVersão: {versao}\n\n"
                    f"{prompt_content}\n\n{content}"
                )
                st.write(f"Extraindo controles com ajuda da OpenAI:")
                execute_assistant_thread(client, combined_content, assistant_id, OUTPUT_FILE)

            # Consolidação final e envio ao assistente
            consolidate_and_send_to_assistant(client, assistant_id)

        # Gerar a página HTML final e permitir download
        output_html_file_path = os.path.join(ARTIFACTS_DIRECTORY, f"{id_unico}_controles.html")
        html_content = generate_html_page(template_file_path, FINAL_OUTPUT_FILE, output_html_file_path)
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

