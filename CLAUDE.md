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

# Set API key (required)
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

## Configuration

API configuration is managed in `config.py`:
- `ZHIPU_API_KEY`: Required API key for Zhipu AI service
- `ZHIPU_API_BASE_URL`: API endpoint URL
- `MODEL_NAME`: AI model to use (glm-4v)
- `DEFAULT_OUTPUT_FORMAT`: Default export format (csv)

## File Processing Flow

1. **Image Input**: Accepts PNG, JPG, BMP, TIFF, WebP formats via file upload or paste
2. **API Call**: Sends image to Zhipu AI GLM-4V model with table extraction prompt
3. **Data Extraction**: Parses JSON response to extract tabular data
4. **Data Processing**: Converts to pandas DataFrame for manipulation
5. **Export**: Saves in requested format (CSV, Excel, JSON)

## Error Handling

The application includes comprehensive error handling for:
- Invalid image formats and file paths
- API request failures with retry logic
- JSON parsing errors from AI responses
- File export failures

## Web UI Features

- Drag-and-drop file upload
- Image paste functionality (Ctrl+V)
- Real-time preview of uploaded images
- Interactive table display of results
- CSV download capability
- Responsive design with error states