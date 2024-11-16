# Security Baselines Generator with AI

This application leverages **Streamlit** and **OpenAI** to generate AI-enhanced security baselines based on user-selected inputs, language preferences, and custom prompts. This project dynamically loads configuration details and categorizes content for users to quickly generate organized security baselines with unique IDs.

## Important Announcement

This project has evolved significantly, surpassing its original purpose as a simple demo. Due to its growth and increased complexity, we have migrated the codebase to a new repository: [BaselineForge](https://github.com/followdrabbit/BaselineForge). 

BaselineForge introduces additional features, enhanced modularity, and a more robust architecture, providing a solid foundation for further development and scaling. Please visit the new repository for the latest updates and improvements.

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
