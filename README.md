LinkedIn Profile Analyzer — a beginner-friendly Python web app that scrapes LinkedIn profiles and generates professional AI-powered summaries and analysis using Google Gemini.

---

## ✨ Features
- **LinkedIn Profile Scraping**: Extracts name, headline, about, experience, and skills (manual login required for privacy and security).
- **AI Summaries**: Uses Google Gemini API to generate clear, professional summaries.
- **Modern Web Interface**: Simple, responsive web UI for easy use.
- **Copy & Download**: Easily copy or download the generated summary.
- **Beginner-Friendly**: No advanced setup or coding required.

---

## 📝 Requirements
- **Python 3.8 or higher**
- **Google Gemini API key** ([get it free](https://aistudio.google.com/app/apikey))
- **Google Chrome browser** (for scraping)
- **LinkedIn account** (for manual login during scraping)

---

## 🚀 Setup Instructions

1. **Clone this repository**
   ```sh
   git clone <your-repository-url>
   cd linkedin-analyzer
   ```

2. **Install Python dependencies**
   ```sh
   pip install -r requirements.txt
   ```

3. **Set up your Gemini API key**
   - Get your key from [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Create a file named `.env` in the project folder:
     ```
     GEMINI_API_KEY=your_gemini_api_key_here
     ```
4. **Install Chrome and Chromedriver if not already installed**
   - Go to (https://googlechromelabs.github.io/chrome-for-testing/)
   - Install the stable ChromeDriver .zip file according to your PC
   - Unzip the downloaded folder in linkedin-analyzer/drivers

5. **(Linux only) Install Chrome and Chromedriver if not already installed**
   ```sh
   sudo apt update
   sudo apt install chromium-browser chromium-chromedriver xvfb -y
   ```
   - On Windows or Mac, make sure Chrome is installed and Chromedriver matches your Chrome version.

---

## ▶️ How to Run the App

1. **Start the web app**
   ```sh
   python main.py
   ```
   - The app will show a local address (usually http://127.0.0.1:5000)
   - Open this address in your web browser.

---

## 🖥️ How to Use

1. Open the web page shown in your terminal.
2. Enter a LinkedIn profile URL (e.g., https://www.linkedin.com/in/example).
3. The app will open a browser window for you to log in to LinkedIn (this is needed for scraping).
4. Wait a few seconds while the app scrapes the profile.
5. The AI summary will appear on the results page for you to copy or download!

---

## 🐞 Troubleshooting
- **Chrome/Chromedriver errors:**
  - Make sure both are installed and versions match.
  - On Linux, update with:
    ```sh
    sudo apt install --only-upgrade chromium-browser chromium-chromedriver
    ```
- **Gemini API key not found:**
  - Make sure `.env` exists and contains your key (no spaces or quotes).
- **LinkedIn scraping fails:**
  - Log in when the browser opens.
  - Only public info can be scraped.
  - Avoid too many requests to prevent being blocked.
- **App not opening:**
  - Check the terminal for the correct address.
  - Make sure nothing else is using port 5000.

---

## 🔒 Security Notes
- Never share your Gemini API key.
- Only scrape profiles you have permission to view.
- Do not use this for commercial scraping or spam.

---

## ⚠️ Legal Disclaimer
This tool is for educational and personal use only. Scraping LinkedIn may violate their Terms of Service. The author takes no responsibility for misuse.

---
## 📁 Project Structure
```
linkedin-analyzer/
├── main.py           # The main app (runs the web server)
├── scraper.py        # Scrapes LinkedIn profiles
├── summarizer.py     # Talks to Gemini AI
├── config.py         # Settings
├── requirements.txt  # Python packages needed
├── templates/        # Web page HTML files
│   ├── index.html
│   └── result.html
└── README.md         # This file
```

---

## 📚 Learn More
- [Python basics](https://www.learnpython.org/)
- [Flask web framework](https://flask.palletsprojects.com/)
- [Selenium for web scraping](https://selenium-python.readthedocs.io/)
- [Google Gemini API](https://aistudio.google.com/app/apikey)

---

---
## 👤 Author
Created by [Vivek] — feel free to check my [LinkedIn](https://www.linkedin.com/in/vivekpawar-ved/).

**Enjoy analyzing LinkedIn profiles with AI!**