# ModuLens

ModuLens is a controlled-access platform designed to explore, evaluate, and responsibly bypass the moderation systems of large language models (LLMs). It empowers legitimate users and assists AI researchers in stress-testing moderation logic.

## Overview

ModuLens provides a comprehensive framework for assessing how LLM moderation systems handle potentially sensitive but legitimate queries. The platform offers:

- **User Mode**: Automatically applies bypass strategies to help users receive responses for legitimate queries that might be incorrectly blocked.
- **Debug Mode**: Provides detailed insights into which strategies succeed or fail, aiding researchers in understanding moderation mechanisms.

## Features

- **Authentication System**: Ensures responsible use by restricting access to authorized users.
- **Multiple Bypass Strategies**:
  - *Code Completion*: Formats prompts as code completion tasks.
  - *Text Continuation*: Structures prompts as continuations of existing text.
  - *Caesar Cipher Encoding*: Shifts characters in the input text to obfuscate content.
  - *Expert Persona Framing*: Frames queries as if posed by an expert, potentially altering moderation responses.
  - *Tense Transformation*: Changes the tense of the input text to modify its presentation.
  - *Chain-of-Thought Injection*: Inserts logical reasoning steps to influence moderation outcomes.
- **Comprehensive LLM Support**:
  - Google (Gemini 2.0 Flash, Gemini 1.5 Flash)
  - Cohere (Command, Command-a-03-2025, Command-Light)
  - OpenAI (GPT-3.5, GPT-4)
  - Anthropic (Claude)
- **Multiple Interfaces**:
  - Command-line interface for direct interaction
  - Web interface for easier access and usability

## Installation

### Prerequisites
- Python 3.8 or higher
- API keys for at least one supported LLM provider

### Setup

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

   Either:
   - Create a `config.json` file based on the template in `config-template.json`
   - Set environment variables in a `.env` file:
     ```
     MODULENS_OPENAI_API_KEY=your_openai_key
     MODULENS_ANTHROPIC_API_KEY=your_anthropic_key
     MODULENS_GEMINI_API_KEY=your_gemini_key
     MODULENS_COHERE_API_KEY=your_cohere_key
     ```
   - Provide keys when prompted on first run

   You need to provide at least one API key (Gemini or Cohere recommended) to use the system.

## Usage

### Command Line Interface

Run ModuLens in CLI mode:

```bash
python app.py
```

Options:
- `--config <path>`: Specify a custom configuration file path.
- `--model <model_name>`: Specify which LLM to use.
- `--debug`: Start in debug mode.

### Web Interface

Launch the web interface:

```bash
python web.py
```

The web interface will be available at `http://localhost:5000` by default.

### Modes of Operation

1. **User Mode**:
   - Enter your prompt
   - ModuLens automatically attempts various bypass strategies
   - Receive the most successful response

2. **Debug Mode**:
   - Enter your prompt
   - View detailed results of each strategy
   - Analyze which approaches succeed or fail with the target model

## Configuration

ModuLens uses a configuration file (`config.json`) with the following structure:

```json
{
  "api_keys": {
    "openai": "your_openai_key",
    "anthropic": "your_anthropic_key",
    "gemini": "your_gemini_key",
    "cohere": "your_cohere_key"
  },
  "models": {
    "gemini_primary": "gemini-2.0-flash",
    "cohere_primary": "command",
    "alternatives": ["command-r", "command-light", "gemini-1.5-flash"]
  },
  "strategies": {
    "caesar_cipher": {"enabled": true},
    "tense_transformation": {"enabled": true},
    "chain_of_thought": {"enabled": true},
    "code_completion": {"enabled": true},
    "text_continuation": {"enabled": true}
  },
  "logging": {"enabled": true, "log_dir": "logs", "level": "INFO"}
}
```

## Ethical Considerations

ModuLens is designed for legitimate research and educational purposes, such as:

- Testing moderation boundaries for academic research
- Understanding when legitimate queries might be incorrectly blocked
- Helping model developers improve moderation systems

This tool should not be used for:

- Generating harmful, illegal, or unethical content
- Intentionally bypassing moderation for malicious purposes
- Exploiting vulnerabilities without proper disclosure to model providers

## Development

### Project Structure
```
modulens/
├── core/          # Core engine and authentication
├── handlers/      # Mode-specific processing logic
├── strategies/    # Implementation of bypass strategies
├── utils/         # Helper functions and utilities
├── web/           # Web interface components
├── __init__.py
└── main.py        # Main entry point
```

### Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Future Development

- Enhanced web interface with analytics dashboard
- Additional bypass strategies
- User management system
- API for programmatic access
- Integration with more LLM providers
- Browser extension for direct integration with LLM websites

## License

[MIT License](LICENSE)

## Disclaimer

ModuLens is an experimental research tool. Users are responsible for ensuring their use complies with the terms of service of any LLM providers they interact with.
