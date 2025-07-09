# LinkedIn Profile Summarizer

A Python application that scrapes LinkedIn profiles and generates professional summaries using **Google Gemini API** (free tier available).

## 🚀 Features

- **Smart Scraping**: Automatically extracts profile information using Selenium WebDriver
- **AI-Powered Summaries**: Uses Google Gemini API to generate professional, engaging summaries
- **Multiple Summary Styles**: Choose from professional, executive, or casual tones
- **Dual Interface**: Console mode for quick use and Flask web interface for better UX
- **Error Handling**: Robust error handling and logging throughout the application
- **Modern UI**: Beautiful, responsive web interface with Bootstrap 5

## 📋 Requirements

- Python 3.8 or higher
- Chrome browser (for Selenium WebDriver)
- **Gemini API key** (get it free at https://aistudio.google.com/app/apikey)
- LinkedIn account (for manual login during scraping)

## 🛠️ Installation

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd linkedin-profile-scraper
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your Gemini API key**
   
   Create a `.env` file in the project root:
   ```bash
   # Example .env file
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
   
   **Get your Gemini API key from:** https://aistudio.google.com/app/apikey

## 🚀 Usage

### Console Mode (Recommended for first-time users)

Run the application and choose console mode:

```bash
python main.py
```

Then select option `1` for console mode.

**Console Mode Features:**
- Interactive prompts for profile URL
- Manual LinkedIn login (browser opens automatically)
- Option to generate multiple summary types
- Save summaries to files
- Real-time feedback and progress updates

### Web Mode (Flask Interface)

Run the application and choose web mode:

```bash
python main.py
```

Then select option `2` for web mode.

**Web Mode Features:**
- Beautiful, modern web interface
- Sample data option for testing without scraping
- Multiple summary type selection
- Copy and download functionality
- Responsive design for all devices

The web interface will be available at: `http://127.0.0.1:5000`

## 📁 Project Structure

```
linkedin-profile-scraper/
├── main.py              # Main application entry point
├── scraper.py           # LinkedIn profile scraping logic
├── summarizer.py        # Gemini API integration
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── templates/          # Flask HTML templates
    ├── index.html      # Main web interface
    └── result.html     # Results display page
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here
```

### Configuration Options

Edit `config.py` to customize:

- **Selenium settings**: Timeouts, wait times
- **Flask settings**: Host, port, debug mode
- **LinkedIn URLs**: Login and base URLs

## 📖 How It Works

### 1. Profile Scraping (`scraper.py`)
- Uses Selenium WebDriver to open LinkedIn profile pages
- Handles manual login process (user logs in via browser)
- Extracts profile data using CSS selectors:
  - Name and headline
  - About section
  - Work experience
  - Skills
- Implements explicit waits and error handling

### 2. Summary Generation (`summarizer.py`)
- Formats scraped data for Gemini API
- Creates prompts based on summary type (professional/executive/casual)
- Calls Gemini API to generate summaries
- Handles API errors and rate limiting
- Saves summaries to JSON files

### 3. Application Interface (`main.py`)
- Provides console and web interfaces
- Orchestrates scraping and summarization
- Handles user input and validation
- Manages application flow and error handling

## 🎯 Example Usage

### Console Mode Example

```bash
$ python main.py
LinkedIn Profile Summarizer
Choose your mode:
1. Console Mode (Interactive)
2. Web Mode (Flask)
Enter your choice (1 or 2): 1

============================================================
LinkedIn Profile Summarizer - Console Mode
============================================================
✅ Gemini API key found

Enter LinkedIn profile URL: https://www.linkedin.com/in/johndoe

🔍 Scraping profile: https://www.linkedin.com/in/johndoe
Note: You will need to log in to LinkedIn manually when the browser opens.

✅ Profile data scraped successfully!
Name: John Doe
Headline: Senior Software Engineer at Tech Company

🤖 Generating professional summary...

============================================================
PROFESSIONAL SUMMARY
============================================================
John Doe is a seasoned software engineer with extensive experience in full-stack development and cloud technologies. With over 5 years of experience at leading tech companies, he has demonstrated expertise in Python, JavaScript, and modern web frameworks. His background includes successful project delivery at Tech Corp and Startup Inc, where he has consistently delivered scalable solutions and mentored junior developers.
============================================================
```

### Web Mode Example

1. Open `http://127.0.0.1:5000` in your browser
2. Enter a LinkedIn profile URL
3. Choose summary type (Professional/Executive/Casual)
4. Optionally check "Use Sample Data" for testing
5. Click "Generate Summary"
6. View results with copy and download options

## ⚠️ Important Notes

### LinkedIn Scraping Limitations
- **Manual Login Required**: You must log in to LinkedIn manually when the browser opens
- **Rate Limiting**: LinkedIn may block automated access if too many requests are made
- **Profile Privacy**: Only public profile information can be scraped
- **Terms of Service**: Ensure compliance with LinkedIn's terms of service

### Gemini API Usage
- **API Limits**: Free tier has usage limits, see Google AI Studio for details
- **API Key Security**: Never commit your API key to version control

### Browser Requirements
- **Chrome**: The application uses Chrome WebDriver
- **Automatic Download**: ChromeDriver is automatically downloaded by webdriver-manager
- **Headless Mode**: Available for web mode (no visible browser window)

## 🐛 Troubleshooting

### Common Issues

1. **"Chrome WebDriver failed to initialize"**
   - Ensure Chrome browser is installed
   - Try updating Chrome to the latest version
   - Check internet connection for driver download

2. **"Gemini API key not found"**
   - Verify `.env` file exists in project root
   - Check that `GEMINI_API_KEY` is set correctly
   - Ensure no extra spaces or quotes around the API key

3. **"Failed to scrape profile data"**
   - Verify the LinkedIn URL is correct and public
   - Ensure you're logged into LinkedIn in the browser
   - Check if the profile has privacy restrictions

4. **"LinkedIn login page not loading"**
   - Check internet connection
   - Verify LinkedIn is accessible in your region
   - Try refreshing the browser page

### Debug Mode

Enable debug logging by modifying `config.py`:

```python
FLASK_DEBUG = True
```

Or set logging level in individual files:

```python
logging.basicConfig(level=logging.DEBUG)
```

## 🔒 Security Considerations

- **API Key Protection**: Never expose your Gemini API key in code or logs
- **Profile Privacy**: Only scrape public profiles with permission
- **Rate Limiting**: Implement delays between requests to avoid being blocked
- **Data Handling**: Don't store sensitive profile data unnecessarily

## 📝 License

This project is for educational purposes. Please ensure compliance with:
- LinkedIn's Terms of Service
- Google AI Studio Usage Policies
- Applicable data protection laws

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the code comments for implementation details
3. Ensure all dependencies are properly installed
4. Verify your API keys and configuration

## 🎉 Acknowledgments

- **Selenium**: For web automation capabilities
- **Google Gemini**: For free text generation API
- **Flask**: For web framework
- **Bootstrap**: For responsive UI components

---

**Happy Summarizing! 🚀**