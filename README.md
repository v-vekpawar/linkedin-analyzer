# LinkedIn Profile Analyzer

A beginner-friendly Python web app that **scrapes LinkedIn profiles** using **Playwright** and generates professional AI-powered summaries and analysis with **Google Gemini**.

---

## Requirements

- **Python 3.8 or higher**
- **Google Gemini API key** ([Get it free](https://aistudio.google.com/app/apikey))
- **Google Chrome or Chromium** (required by Playwright)
- **LinkedIn account** (manual login required on first run)

---

## Setup Instructions

1. **Clone this repository**
   ```bash
   git clone https://github.com/v-vekpawar/linkedin-analyzer
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

4. **Set up your .env**

   - Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Create a `.env` file in the project folder:
     ```env
     GEMINI_API_KEY=your_gemini_api_key_here
     SECRET_KEY=random_secret_key_for_flask
     LINKEDIN_ACCOUNTS=email1:paasword1;email2:password2 (add more if you want more in same format)
     LINKEDIN_2FA_SECRET_email1=2fa_secret_key_for_email1 (get it after enabling Linkedin 2FA)
     LINKEDIN_2FA_SECRET_email2=2fa_secret_key_for_email2 (get it after enabling Linkedin 2FA)
     ```

---

## How to Run the App

**Run in web mode (recommended):**
```bash
python app.py
```
- The app will show a local address (usually `http://127.0.0.1:5000`).
- Open this address in your browser.

**Run in console mode (optional):**
```bash
python app.py --mode console
```
> In console mode, the scraping runs directly in the terminal instead of the web UI.

---

## Headless Mode

By default, the scraper runs **without a visible browser window**.

- To disable headless mode (visible browser window), update `config.py`:
  ```python
  HEADLESS=FALSE
  ```

---

## Legal Disclaimer

This tool is for **personal learning purposes only**.  
Scraping LinkedIn may violate their Terms of Service.  
Use responsibly — the author is not responsible for misuse.

---

##  Author

Created by **ved** — [Connect on LinkedIn](https://www.linkedin.com/in/vivekpawar-ved/)

**Happy analyzing LinkedIn profiles with AI!**
