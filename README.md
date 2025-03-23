# ModuLens

ModuLens is a controlled-access platform designed to explore, evaluate, and responsibly bypass the moderation systems of large language models (LLMs), with the dual goal of empowering legitimate users and assisting AI researchers in stress-testing moderation logic.

## Overview

ModuLens provides a framework for evaluating how LLM moderation systems handle potentially sensitive but legitimate queries. It offers two primary modes:

- **User Mode**: Automatically applies bypass strategies to help users get responses for legitimate queries that might be incorrectly blocked
- **Debug Mode**: Provides detailed insights into which strategies succeed or fail, helping researchers understand moderation mechanisms

## Features

- Authentication system to ensure responsible use
- Multiple bypass strategies:
  - Caesar Cipher encoding
  - Expert persona framing
  - Tense transformation
  - Multilingual translation
  - Chain-of-thought injection
- Detailed logging and metrics for research purposes
- Support for multiple LLM providers:
  - OpenAI (GPT-3.5, GPT-4)
  - Anthropic (Claude)
  - Google (Gemini)
  - Cohere (Command)

## Installation

1. Clone this repository:
```
git clone https://github.com/yourusername/modulens.git
cd modulens
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Set up your API keys by either:
   - Creating a `config.json` file (a sample will be generated on first run)
   - Setting environment variables:
     - `MODULENS_OPENAI_API_KEY`
     - `MODULENS_ANTHROPIC_API_KEY`
     - `MODULENS_GEMINI_API_KEY`
     - `MODULENS_COHERE_API_KEY`

   You only need to provide at least one API key to use the system.

## Usage

Run ModuLens from the command line:

```
python -m modulens.main
```

Options:
- `--config <path>`: Specify a custom configuration file path
- `--model <model_name>`: Specify which LLM to use
- `--debug`: Start in debug mode

## Ethical Considerations

ModuLens is designed for legitimate research and educational purposes, such as:
- Testing moderation boundaries for academic research
- Understanding when legitimate queries might be incorrectly blocked
- Helping model developers improve moderation systems

This tool should not be used for:
- Generating harmful, illegal, or unethical content
- Intentionally bypassing moderation for malicious purposes
- Exploiting vulnerabilities without proper disclosure to model providers

## Future Development

- Web-based UI for easier interaction
- Additional bypass strategies
- Enhanced analytics and visualization
- Integration with more LLM providers

## License

[MIT License](LICENSE)

## Disclaimer

ModuLens is an experimental research tool. Users are responsible for ensuring their use complies with the terms of service of any LLM providers they interact with.