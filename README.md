# 🌍 Gemini Landmark Description App

[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

An AI-powered web app that acts as your personal tour guide! Simply upload an image of any landmark, and get instant details about its history, architecture, and significance - powered by Google's Gemini Pro Vision model.

![App Demo](demo.gif) 

## ✨ Features

- 🏛️ **Instant Landmark Recognition** - Identify famous buildings, monuments, and sites
- 📚 **Rich Descriptions** - Get historical context, architectural details, and cultural significance
- 🖼️ **Image + Text Input** - Combine photos with custom questions (e.g., "What's special about the dome?")
- 🚀 **Streamlit UI** - Simple, intuitive interface for all users

## 🛠️ Tech Stack

| Component          | Technology |
|--------------------|------------|
| **AI Model**       | Google Gemini Pro Vision (`gemini-pro-vision`) |
| **Frontend**       | Streamlit |
| **Backend**        | Python 3.9+ |
| **API Handling**   | `google-generativeai` |
| **Environment**    | `python-dotenv` |

## ⚡ Quick Start

### Prerequisites
- Python 3.9+
- Google API key ([Get one here](https://ai.google.dev/gemini-api/docs/api-key))

### Installation
1. Clone the repo:
   ```bash
   git clone https://github.com/your-username/gemini-landmark-app.git
   cd gemini-landmark-app
   ```
2. Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```
3. Create .env file:
  ```env
  GOOGLE_API_KEY="your_actual_api_key_here"
  ```
4. Run the app:

  ```bash
  streamlit run app.py
  ```
## 📸 How It Works
1. Upload an image of a landmark

2. Click "Describe Landmark"

3. Get AI-generated insights!


## 📂 Project Structure
text
gemini-landmark-app/

├── .env                    # API key configuration

├── app.py                  # Main Streamlit application

├── requirements.txt        # Dependencies

├── README.md               # This file

└── LICENSE                 # MIT License
## 🤝 Contributing
Contributions welcome! Please follow these steps:

#### Fork the project

Create a feature branch (```git checkout -b feature/AmazingFeature```)

Commit changes (```git commit -m 'Add amazing feature```)

Push to branch (```git push origin feature/AmazingFeature```)

Open a Pull Request

## 📜 License
Distributed under the MIT License. See LICENSE for details.
