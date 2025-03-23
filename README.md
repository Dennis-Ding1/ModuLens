# ModuLens

ModuLens is a controlled-access platform designed for AI researchers to explore, evaluate, and responsibly bypass the "Moderation Layer" of large language models. By providing authenticated access only, ModuLens creates a secure environment for legitimate researchers to investigate how LLM moderation systems handle important queries that may be incorrectly blocked by alignment filters.

![ModuLens Logo](https://placeholder-for-modulens-logo.png)

## Overview

AI safety research requires understanding both the capabilities and limitations of moderation systems. ModuLens enables researchers to explore important interdisciplinary questions at the intersection of AI and fields like psychology, chemistry, biology, and security research - areas where legitimate academic inquiry is often hindered by overly cautious moderation policies.

The platform enforces strict authentication protocols to ensure only credentialed researchers can access these capabilities:

- **User Mode**: Automatically applies bypass strategies to help researchers receive responses for legitimate academic queries that are incorrectly blocked by moderation systems.
- **Debug Mode**: Provides detailed insights into which bypass strategies succeed or fail, aiding researchers in understanding moderation mechanisms and their limitations.

## Key Research Applications

ModuLens facilitates responsible research in areas where AI alignment filters may impede legitimate inquiry:

- **Psychology & Mental Health**: Explore how AI models respond to sensitive topics like suicide prevention strategies and crisis intervention approaches.
- **Chemistry & Materials Science**: Study chemical processes and reactions that might be incorrectly flagged as dangerous.
- **Security Research**: Examine model responses to potential security vulnerabilities to improve AI systems' robustness.
- **Bias & Fairness Research**: Investigate how moderation systems handle culturally sensitive topics across different regions and languages.
- **So on and so forth**

## Features

- **Authentication System**: Strictly verifies researcher credentials to ensure only authorized academic users can access the platform.
- **Multiple Bypass Strategies**:
  - *Code Completion*: Formats prompts as code completion tasks to bypass content filters.
  - *Text Continuation*: Structures prompts as continuations of existing text to maintain context.
  - *Caesar Cipher Encoding*: Shifts characters in the input text to obfuscate content from detection systems.
  - *Expert Persona Framing*: Frames queries as if posed by an expert in a field, potentially altering moderation responses.
  - *Tense Transformation*: Changes the tense of the input text to modify how moderation systems interpret intent.
  - *Chain-of-Thought Injection*: Inserts logical reasoning steps to influence moderation outcomes by demonstrating academic purpose.
- **Comprehensive LLM Support**:
  - Google (Gemini 2.0 Flash, Gemini 1.5 Flash)
  - Cohere (Command, Command-a-03-2025, Command-Light)
  - OpenAI (GPT-3.5, GPT-4)
  - Anthropic (Claude)
- **Multiple Interfaces**:
  - Command-line interface for direct research interaction
  - Web interface for easier access and usability with result logging

## Installation

### Prerequisites
- Python 3.8 or higher
- API keys for at least one supported LLM provider
- Institutional email or research credentials for authentication

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

## Authentication

ModuLens implements a strict authentication system to ensure responsible use:

1. **First-time Setup**: Register with your institutional email address
2. **Verification**: Your research credentials will be verified before access is granted
3. **Login System**: After verification, use your credentials to access the system
4. **Session Management**: All research sessions are logged and monitored for compliance

Unauthorized access attempts are blocked and may be reported to relevant authorities.

## Usage

### Command Line Interface

After authentication, run ModuLens in CLI mode:

```bash
python app.py
```

Options:
- `--config <path>`: Specify a custom configuration file path.
- `--model <model_name>`: Specify which LLM to use.
- `--debug`: Start in debug mode.

### Web Interface

Launch the web interface after authentication:

```bash
python web.py
```

The web interface will be available at `http://localhost:5000` by default.

### Modes of Operation

1. **User Mode**:
   - Enter your research query
   - ModuLens automatically attempts various bypass strategies
   - Receive the most successful response for your academic inquiry
   - All responses are logged for research accountability

2. **Debug Mode**:
   - Enter your research query
   - View detailed results of each strategy
   - Analyze which approaches succeed or fail with the target model
   - Export detailed logs for publication or further analysis

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

## Ethical Requirements and Guidelines

ModuLens is exclusively designed for legitimate academic and research purposes. We maintain strict ethical guidelines:

### Permitted Research Uses
- Academic studies on AI alignment and safety
- Educational research on moderation systems
- Development of improved moderation techniques
- Identification of false positives in content filtering
- Cross-disciplinary research requiring discussion of sensitive topics

### Prohibited Uses
- Generating harmful, illegal, or unethical content
- Bypassing moderation for non-research purposes
- Distributing harmful outputs or bypass techniques to unauthorized parties
- Using the tool without proper research protocols in place
- Concealing research intent or providing false credentials

### Research Accountability
- All sessions are logged with user identification
- Research purposes must be documented before use
- Potentially problematic outputs must be reported
- Researchers agree to share findings with model providers
- Vulnerabilities discovered must follow responsible disclosure protocols

### Compliance Requirements
- Users must obtain appropriate IRB/ethics board approval when necessary
- Users must comply with their institution's research ethics guidelines
- All use must comply with relevant laws and regulations

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

Contributions are welcome from the research community! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request with a detailed description of the research purpose

## Future Development

- Enhanced web interface with analytics dashboard
- Additional bypass strategies for research purposes
- Comprehensive user management system with role-based access
- API for programmatic access in controlled research environments
- Integration with more LLM providers
- Advanced logging and analysis tools for research publication
- Browser extension for direct integration with LLM websites

## License

[MIT License](LICENSE)

## Disclaimer

ModuLens is an experimental research tool designed exclusively for legitimate academic research. Misuse is strictly prohibited and may result in legal consequences. Users are responsible for ensuring their research complies with the terms of service of any LLM providers they interact with, as well as all applicable laws and regulations. 

The developers of ModuLens are committed to advancing AI safety research and improving content moderation systems through responsible academic inquiry. We actively discourage any attempt to use this tool for harmful purposes.
