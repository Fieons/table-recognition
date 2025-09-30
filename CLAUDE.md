# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a table recognition tool that uses Zhipu AI's GLM-4V model to extract tabular data from images and convert it to structured formats (CSV, Excel, JSON). The project provides both a web interface and command-line interface.

## Architecture

### Core Components
- **app.py**: Flask web application with file upload and image paste functionality
- **main.py**: Command-line interface with argument parsing and file processing
- **api_client.py**: Zhipu AI API client for table recognition requests
- **table_parser.py**: Data processing and export functionality using pandas
- **config.py**: Configuration management for API keys and settings
- **templates/index.html**: Web UI with drag-drop, file selection, and image paste support

### Key Dependencies
- Flask: Web framework for the UI
- pandas: Data manipulation and export
- requests: HTTP client for API calls
- Pillow: Image processing (implicit dependency)
- openpyxl: Excel file export support

## Development Commands

### Environment Setup
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set API key (required) - IMPORTANT: Never commit API keys to version control
export ZHIPU_API_KEY=your_api_key_here
```

### Running the Application
```bash
# Web UI (recommended for development)
python app.py
# Access at http://localhost:5000

# Command-line interface
python main.py image_path [options]
```

### CLI Usage Examples
```bash
# Basic usage with default CSV output
python main.py screenshot.png

# Specify output format
python main.py screenshot.png -f excel
python main.py screenshot.png -f json

# Preview without saving
python main.py screenshot.png --preview

# Custom output path
python main.py screenshot.png -o result.xlsx
```

### Development and Testing
```bash
# Check for syntax errors (no specific linter configured)
python -m py_compile *.py

# Type checking (if mypy was installed)
python -m mypy *.py
```

## Configuration

API configuration is managed in `config.py`:
- `ZHIPU_API_KEY`: Required API key for Zhipu AI service (should use environment variables)
- `ZHIPU_API_BASE_URL`: API endpoint URL
- `MODEL_NAME`: AI model to use (glm-4v)
- `DEFAULT_OUTPUT_FORMAT`: Default export format (csv)

**SECURITY NOTE**: The current config.py contains a hardcoded API key which is a security risk. Always use environment variables for sensitive configuration.

## File Processing Flow

1. **Image Input**: Accepts PNG, JPG, BMP, TIFF, WebP formats via file upload or paste
2. **API Call**: Sends image to Zhipu AI GLM-4V model with table extraction prompt
3. **Data Extraction**: Parses JSON response to extract tabular data with fallback text parsing
4. **Data Processing**: Converts to pandas DataFrame for manipulation
5. **Export**: Saves in requested format (CSV, Excel, JSON)

## Error Handling

The application includes comprehensive error handling for:
- Invalid image formats and file paths
- API request failures with retry logic (3 attempts)
- JSON parsing errors from AI responses with fallback text parsing
- File export failures
- Network connectivity issues with detailed error messages

## API Integration Details

- Uses Zhipu AI's GLM-4V model via REST API
- Image data is base64 encoded and sent in multipart format
- Response parsing handles both JSON and text formats
- Automatic retry mechanism for failed requests
- Detailed error reporting with suggested solutions

## Web UI Features

- Drag-and-drop file upload
- Image paste functionality (Ctrl+V)
- Real-time preview of uploaded images
- Interactive table display of results
- CSV download capability
- Responsive design with error states
- CORS support for cross-origin requests

## Data Flow Architecture

1. **Input Layer**: File upload (web) or file path (CLI)
2. **API Layer**: ZhipuAIClient handles authentication and requests
3. **Processing Layer**: TableParser converts raw data to structured format
4. **Output Layer**: Export to CSV/Excel/JSON formats

## Security Considerations

- API keys should be managed via environment variables
- Temporary files are automatically cleaned up
- File uploads are validated for allowed formats
- No authentication mechanism for web interface (development only)
- Input validation for file paths and formats