# Security Baselines Generator with AI

This application leverages **Streamlit** and **OpenAI** to generate AI-enhanced security baselines based on user-selected inputs, language preferences, and custom prompts. This project dynamically loads configuration details and categorizes content for users to quickly generate organized security baselines with unique IDs.

## Key Features

- **Multi-language Support**: Supports **EN-US**, **PT-BR**, and **ES-ES**, dynamically loading configuration settings from `config.toml`, which includes:
  - Language-specific prompts for vendor, technology, version, category, URLs, and baseline generation.
  - Labels in each language for table headers in the HTML output.
  - Categories covering various technology fields, enabling organized selection.
  - Dynamic table headers in the HTML output, based on user-selected language.

- **Unique ID Generation**: A structured ID format is created using parameters like vendor, category, technology, and version for consistency across generated baselines.

- **OpenAI Assistant**: The application checks for an existing assistant with pre-set instructions. If not found, a new assistant is created to assist in generating security controls based on prompts and URLs.

- **Conversion to HTML**: Processes Markdown files into dynamic HTML tables, incorporating labels specific to each selected language for a customized final report.

- **Automated Cleanup**: Temporary files and folders generated during each session are cleaned up after use, optimizing server storage.

## Project Structure

- **main.py**: The primary script handling Streamlit’s UI elements, OpenAI assistant operations, and file management.
- **config.toml**: Configuration file defining language settings, available categories, table labels, and template text.
- **artefatos/**: Directory for temporary files generated during processing.
- **template_html.html**: HTML template used to generate the final downloadable HTML report based on consolidated content.

## Configuration Overview

The `config.toml` file organizes settings as follows:

- `[MENU]`: Language-specific prompts for UI elements.
- `[Categories]`: List of categories to choose from for security control contexts.
- `[tabela_labels]`: Language-specific table labels for displaying security controls.
- `[html_template_control_list]`: Title of the control list section for each language in the HTML output.

## Getting Started

### Installation

1. **Install Required Libraries**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Application**:
   ```bash
   streamlit run main.py
   ```

### Usage

1. **Choose Language**: Select from **EN-US**, **PT-BR**, or **ES-ES** for UI and prompt language.
2. **Input Details**:
   - Select **Vendor** and **Category**.
   - Enter **Technology Name** and **Version** (leave as "Static" if there’s no specific version).
   - Add up to **10 URLs** for processing, separated by commas.
3. **Generate Baseline**: The application generates a unique ID and processes the URLs, saving the results in Markdown and converting them to HTML.
4. **Download**: After processing, download the generated HTML report containing the organized security controls list.
5. **File Management**: Temporary files are removed post-download for optimal storage management.

## Acknowledgments

Special thanks to OpenAI and Streamlit communities for tools and resources that made this project possible.