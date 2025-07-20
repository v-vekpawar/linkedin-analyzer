# LinkedIn Profile Analyzer

A beginner-friendly Python web app that **scrapes LinkedIn profiles** using **Playwright** and generates professional AI-powered summaries and analysis with **Google Gemini**.

---

## ✨ Features

- **LinkedIn Profile Scraping** — Extracts name, headline, about, experience, skills, and education.
- **AI Summaries** — Uses the Google Gemini API to generate clear, professional summaries.
- **Modern Web Interface** — Simple, responsive web UI.
- **Copy & Download** — Easily copy or download the generated summary.
- **Persistent Login** — Log in once; your session is saved.
- **Beginner-Friendly** — No advanced setup or coding skills required.

---

## 📝 Requirements

- **Python 3.8 or higher**
- **Google Gemini API key** ([Get it free](https://aistudio.google.com/app/apikey))
- **Google Chrome or Chromium** (required by Playwright)
- **LinkedIn account** (manual login required on first run)

---

## 🚀 Setup Instructions

1. **Clone this repository**
   ```bash
   git clone <your-repository-url>
   cd linkedin-analyzer
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers**
   ```bash
   playwright install
   ```

4. **Set up your Gemini API key**

   - Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Create a `.env` file in the project folder:
     ```env
     GEMINI_API_KEY=your_gemini_api_key_here
     ```

---

## ▶️ How to Run the App

**Run in web mode (recommended):**
```bash
python main.py
```
- The app will show a local address (usually `http://127.0.0.1:5000`).
- Open this address in your browser.

**Run in console mode (optional):**
```bash
python main.py --mode console
```
> In console mode, the scraping runs directly in the terminal instead of the web UI.

---

## ⚙️ Headless Mode

By default, the scraper runs **with a visible browser window** so you can log in manually.

- To enable headless mode (no visible browser window), update `main.py`:
  ```python
  profile_data = scrape_linkedin_profile(profile_url, headless=True)
  ```
  in both `analyze()` and `api_analyze()` functions.

**Important:**  
You **must log in once** with `headless=False` so your session is saved. After that, you can run headless.

---

## 🖥️ How It Works

1. Open the web page shown in your terminal.
2. Enter a LinkedIn profile URL (e.g., `https://www.linkedin.com/in/example`).
3. The app opens a **Chromium browser** — log in to LinkedIn if asked.
4. Once logged in, your session is saved in `playwright_user_data`.
5. The scraper fetches data, sends it to Gemini, and shows the AI summary.
6. Copy or download your result.

---

## 🐞 Troubleshooting

- **Browser not found:**  
  ```bash
  playwright install
  ```
- **Manual login:**  
  Your login is saved after the first run.
- **Invalid API key:**  
  Make sure `.env` is set up correctly with no extra spaces or quotes.
- **LinkedIn blocks scraping:**  
  - Be patient — scraping takes time.
  - Avoid sending too many requests.
- **Port already in use:**  
  - Make sure port `5000` is free or change it in `config.py`.

---

## 🔒 Security Notes

- Keep your Gemini API key secret.
- Only scrape profiles you’re allowed to view.
- Do not use this tool for bulk scraping.
- Respect LinkedIn’s Terms of Service — this is for **personal, educational use** only.

---

## ⚠️ Legal Disclaimer

This tool is for **personal learning purposes only**.  
Scraping LinkedIn may violate their Terms of Service.  
Use responsibly — the author is not responsible for misuse.

---

## 📁 Project Structure

```
linkedin-analyzer/
├── main.py           # Main app (web server)
├── scraper.py        # Playwright scraping logic
├── summarizer.py     # Gemini API integration
├── config.py         # App settings
├── requirements.txt  # Python dependencies
├── templates/        # HTML templates
│   ├── index.html
│   └── result.html
└── README.md         # This file
```

---

## 📚 Learn More

- [Python Basics](https://www.learnpython.org/)
- [Flask Web Framework](https://flask.palletsprojects.com/)
- [Playwright for Python](https://playwright.dev/python/)
- [Google Gemini API](https://aistudio.google.com/app/apikey)

---

## 👤 Author

Created by **Vivek Pawar** — [Connect on LinkedIn](https://www.linkedin.com/in/vivekpawar-ved/)

**🚀 Happy analyzing LinkedIn profiles with AI!**
