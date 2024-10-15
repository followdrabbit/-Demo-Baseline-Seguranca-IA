Here is the updated README in English with the additional information you requested:

---

## README: CyberSecurity Assistant Script

### Overview

This Python script automates the process of downloading web pages, converting them into Markdown files, and interacting with the OpenAI API to generate security baselines for AWS services. The script is designed to be modular, allowing for downloading, processing, and creating threads for the content, utilizing OpenAI's API to build and manage security baselines.

### Features

1. **Download Web Pages**: The script fetches web pages and saves them in both HTML and Markdown formats.
2. **Markdown Conversion**: Converts HTML files to Markdown for easier readability and processing.
3. **Content Management**: Loads and processes Markdown files, stores them in variables for further use.
4. **OpenAI Assistant**: Interacts with the OpenAI API, allowing the creation and execution of security baselines using an assistant named `CyberSecurityAssistant`.
5. **Threaded Processing**: Creates and runs threaded tasks in OpenAI, collects responses, and manages the status of tasks.

### Requirements

This script requires the following packages listed in the `requirements.txt` file:

```txt
requests
html2text
openai
python-dotenv
```

You can install all dependencies with the following command:

```bash
pip install -r requirements.txt
```

### Setup

#### **OpenAI API Key**

To use the transcription and translation features, you must generate an OpenAI API key. Be aware that using the API may incur costs, depending on the volume of requests. For more information on how to generate your API key, refer to [this blog post on Asimov Academy](https://hub.asimov.academy/blog/openai-api/).

Add the API key to a `.env` file with the following content:

```bash
OPENAI_API_KEY=<your-openai-api-key>
```

#### **Directory Structure**

The script expects certain directories for storing content:

- `paginas_md`: For storing converted Markdown files.
- `paginas_baixadas`: For storing downloaded HTML files.

#### **Prompt Baseline**

The `prompt_baseline_creation.txt` file should contain the template or prompt instructions to be used when interacting with OpenAI.

### Usage

#### Step 1: Download Web Pages

The script downloads web pages from a list of URLs and stores the HTML files locally.

- **Function**: `processar_urls(lista_urls)`
- **Output**: Saves the downloaded HTML content into the `paginas_baixadas` directory.

#### Step 2: Convert HTML to Markdown

The HTML files are converted into Markdown format for easier processing and saved to the `paginas_md` directory.

- **Function**: `processar_urls_para_markdown(lista_urls)`
- **Output**: Saves the converted Markdown content into the `paginas_md` directory.

#### Step 3: Load Markdown Files

Once the Markdown files are saved, the script loads them into variables for further use.

- **Function**: `carregar_conteudo_md()`
- **Output**: Loads all Markdown files into a dictionary.

#### Step 4: Create OpenAI Assistant

The script checks whether the assistant already exists or creates a new one using OpenAI's API.

- **Function**: `criar_assistente(client, info_assistente)`
- **Output**: Creates or retrieves an existing assistant from OpenAI.

#### Step 5: Execute Threads and Get Responses

The script creates threads in OpenAI, sends messages with the Markdown content and prompt, and retrieves the assistant's response.

- **Function**: `enviar_mensagens_sequencial(client, diretorio_md, caminho_prompt_baseline, assistant_id)`
- **Output**: Sends content to OpenAI in threaded requests and processes the responses.

### Customization

- **Assistant Configuration**: You can customize the assistant's name and instructions in the `assistant_info` variable.
- **Prompt Customization**: The `prompt_baseline_creation.txt` file can be modified to adjust the instructions for the security baseline creation.

### Example Execution

To run the script:

```bash
python script_name.py
```

### Additional Notes

- Ensure that the `OPENAI_API_KEY` is correctly set in the `.env` file.
- Make sure the directories `paginas_md` and `paginas_baixadas` exist or are created dynamically by the script.
- **Platform**: This script was created and tested in Jupyter Notebook on a Windows environment using Python version 3.12.

### License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

---

Feel free to customize this script for your specific use case in developing security baselines for AWS services!