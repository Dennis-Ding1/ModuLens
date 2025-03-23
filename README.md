# ModuLens

ModuLens is a controlled-access platform designed to explore, evaluate, and responsibly bypass the moderation systems of large language models (LLMs). It aims to empower legitimate users and assist AI researchers in stress-testing moderation logic.

## Overview

ModuLens provides a framework for assessing how LLM moderation systems handle potentially sensitive but legitimate queries. It offers two primary modes:

- **User Mode**: Automatically applies bypass strategies to help users receive responses for legitimate queries that might be incorrectly blocked.
- **Debug Mode**: Provides detailed insights into which strategies succeed or fail, aiding researchers in understanding moderation mechanisms.

## Features

- **Authentication System**: Ensures responsible use by restricting access to authorized users.
- **Multiple Bypass Strategies**:
  - *Caesar Cipher Encoding*: Shifts characters in the input text to obfuscate content.
  - *Expert Persona Framing*: Frames queries as if posed by an expert, potentially altering moderation responses.
  - *Tense Transformation*: Changes the tense of the input text to modify its presentation.
  - *Multilingual Translation*: Translates the input into another language and back to circumvent moderation.
  - *Chain-of-Thought Injection*: Inserts logical reasoning steps to influence moderation outcomes.
- **Support for Multiple LLM Providers**:
  - Google (Gemini)
  - Cohere (Command)
  - OpenAI (GPT-3.5, GPT-4)
  - Anthropic (Claude)
  

## Installation

To set up ModuLens locally, follow these steps:

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/yourusername/modulens.git
   cd modulens
   ```

2. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Configuration**:

   Create a `config.json` file or set the following environment variables:

   - `MODULENS_OPENAI_API_KEY`
   - `MODULENS_ANTHROPIC_API_KEY`
   - `MODULENS_GEMINI_API_KEY`
   - `MODULENS_COHERE_API_KEY`

   You need to provide at least one API key to use the system.

## Usage

Run ModuLens from the command line:

```bash
python -m modulens.main
```

Options:

- `--config <path>`: Specify a custom configuration file path.
- `--model <model_name>`: Specify which LLM to use.
- `--debug`: Start in debug mode.

## Ethical Considerations

ModuLens is designed for legitimate research and educational purposes, such as:

- Testing moderation boundaries for academic research.
- Understanding when legitimate queries might be incorrectly blocked.
- Helping model developers improve moderation systems.

This tool should not be used for:

- Generating harmful, illegal, or unethical content.
- Intentionally bypassing moderation for malicious purposes.
- Exploiting vulnerabilities without proper disclosure to model providers.

## Future Development

- Web-based UI for easier interaction.
- Additional bypass strategies.
- Enhanced analytics and visualization.
- Integration with more LLM providers.

## License

[MIT License](LICENSE)

## Disclaimer

ModuLens is an experimental research tool. Users are responsible for ensuring their use complies with the terms of service of any LLM providers they interact with.
