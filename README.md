# 📄 Japanese Receipt AI Recognition System

[![Demo Video](https://img.youtube.com/vi/Ur5AVAt0oT4/0.jpg)](https://youtu.be/Ur5AVAt0oT4)

> 💡 **Click the image above to watch the full demo video** showing the complete workflow of the application.

> 🇹🇼 [繁體中文版本](./README_zh.md) | 🇬🇧 [English Version](./README.md)

An AI-based Japanese receipt recognition and data extraction system that automatically processes receipt images and generates structured CSV data. It uses Azure Computer Vision API for text recognition and Claude AI for structured data extraction.

## 🚀 Quick Start

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Set Environment Variables
Copy `.env.example` to `.env` and fill in your API keys:
```bash
cp .env.example .env
```

### Start Service

#### Method 1: Use Quick Start Script (Recommended)
```bash
./start.sh
```

#### Method 2: Use Python Start Script
```bash
python start.py
```

#### Startup Options
```bash
# Use custom port
./start.sh -p 8080

# Production mode (disable auto-reload)
./start.sh --prod

# View all options
./start.sh --help
```

Visit http://localhost:8000 to start using

## 📋 Main Features

- 🔍 **Smart OCR Recognition**: Uses Azure Computer Vision API for text recognition
- 🤖 **AI Data Extraction**: Uses Claude AI for structured data extraction
- 📊 **CSV Output**: Automatically generates CSV files with Chinese headers
- 🌐 **Web Interface**: User-friendly interface with batch upload support
- ⚡ **Batch Processing**: Efficient processing of large image volumes
- 💾 **Caching Mechanism**: Smart caching to avoid duplicate processing
- 🗑️ **File Management**: Automatic cleanup of processed images, supports manual deletion

## 📚 Documentation

### 🔧 User Guides
- **[Azure Resource Setup Guide](./docs/guides/AZURE_RESOURCE_SETUP.md)** - How to create Computer Vision resource on Azure and obtain URL and Key (**Required for new users**)
- **[API Setup Guide](./docs/guides/API_SETUP_GUIDE.md)** - How to configure Azure and Claude API
- **[Azure Cost Guide](./docs/guides/AZURE_COST_GUIDE.md)** - Cost control and optimization recommendations
- **[Azure Key Management](./docs/guides/AZURE_KEY_MANAGEMENT.md)** - How to view and manage API keys in Azure Portal
- **[Usage Guide](./docs/guides/USAGE.md)** - Detailed usage instructions

### 🎯 Feature Documentation
- **[File Management Features](./docs/features/FILE_MANAGEMENT_SUMMARY.md)** - Automatic file cleanup and management
- **[Performance Optimization](./docs/features/PERFORMANCE_OPTIMIZATION_SUMMARY.md)** - System performance optimization details
- **[Tax Features](./docs/features/TAX_FEATURES_SUMMARY.md)** - Japanese tax recognition and processing

### 🔧 Development Setup
- **[GitHub Setup](./docs/setup/GITHUB_SETUP.md)** - GitHub project setup and upload guide

### 🐛 Fix Records
- **[Fix Documentation Overview](./docs/fixes/README.md)** - Quick overview of all fixes
- **[System Fix Summary](./docs/fixes/INTEGRATED_FIXES.md)** - All issue fix records (with detailed technical explanations)

## 🏗️ System Architecture

```
receipt_record/
├── app/                    # Main application
│   ├── main.py            # FastAPI main program
│   ├── config.py          # Configuration management
│   ├── models/            # Data models
│   ├── services/          # Core services
│   └── utils/             # Utility functions
├── static/                # Frontend files
├── data/                  # Data directory
│   ├── receipts/          # Receipt images
│   ├── output/            # CSV output
│   └── cache/             # Cache files
├── tests/                 # Test files
└── docs/                  # Documentation directory
```

## 🔧 Tech Stack

- **Backend**: FastAPI, Python 3.8+
- **AI Services**: Azure Computer Vision, Claude 3.5 Sonnet
- **Frontend**: HTML, JavaScript
- **Data Processing**: Pandas, CSV
- **Image Processing**: Pillow, OpenCV

## 📊 System Status

- ✅ All known issues fixed
- ✅ System running stably
- ✅ Processing success rate: 100%
- ✅ Supports batch processing
- ✅ Smart caching mechanism

## 🤝 Contributing

Welcome to submit Issues and Pull Requests!

## 📄 License

MIT License

---

**Last Updated**: 2025-12-30  
**Version**: 1.1.0
