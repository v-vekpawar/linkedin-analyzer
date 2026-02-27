import time, random, logging, json, os, shutil
from config import MAX_SCRAPE_PER_ACCOUNT
from pathlib import Path
from playwright.sync_api import sync_playwright
import pyotp

logger = logging.getLogger(__name__)

class LinkedInLogin:
    def __init__(self, headless):
        self.headless = headless
        self.user_data_dir = Path("./playwright_user_data")
        self.cookies_file = self.user_data_dir / "linkedin_cookies.json"
        self.user_data_dir.mkdir(exist_ok=True)
        
        self.playwright = None
        self.browser = None
        self.page = None
        
        self.initialize_browser()

    def initialize_browser(self):
        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch_persistent_context(
        user_data_dir=str(self.user_data_dir),
        headless=self.headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--disable-automation",
                "--disable-plugins-discovery",
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ]
        )

        self.page = self.browser.pages[0] if self.browser.pages else self.browser.new_page()
        
        self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        """)
        
        self.load_cookies()

    def save_cookies(self):
        try:
            cookies = self.page.context.cookies()
            linkedin_cookies = [c for c in cookies if 'linkedin' in c.get('domain', '')]
            
            if linkedin_cookies:
                with open(self.cookies_file, 'w') as f:
                    json.dump(linkedin_cookies, f, indent=2)
                logger.info(f"Saved {len(linkedin_cookies)} cookies")
                return True
            return False
        except Exception as e:
            logger.exception(f"Cookie save error: {e}")
            return False

    def load_cookies(self):
        try:
            if not self.cookies_file.exists():
                return False
            
            with open(self.cookies_file, 'r') as f:
                cookies = json.load(f)
            
            if cookies:
                try:
                    self.page.context.clear_cookies()
                except:
                    pass
                self.page.context.add_cookies(cookies)
                logger.info(f"Loaded {len(cookies)} cookies")
                return True
            return False
        except Exception as e:
            logger.exception(f"Cookie load error: {e}")
            return False
    
    def random_delay(self, min_sec=1, max_sec=3):
        """Add random delays to mimic human behavior."""
        time.sleep(random.uniform(min_sec, max_sec))
        
    def is_logged_in(self):
        try:
            try:
                current_url = self.page.evaluate("window.location.href").lower()
            except:
                current_url = self.page.url.lower()
            
            logger.info(f"Checking login status. Current URL: {current_url}")

            # If page is blank (about:blank), need to navigate somewhere to check login
            if current_url == "about:blank" or not current_url.startswith("http"):
                logger.info("Page is blank, navigating to LinkedIn feed to check login status...")
                try:
                    self.page.goto("https://www.linkedin.com/feed/", timeout=30000, wait_until="domcontentloaded")
                    self.random_delay(2, 3)
                    
                    # Update current URL after navigation
                    try:
                        current_url = self.page.evaluate("window.location.href").lower()
                    except:
                        current_url = self.page.url.lower()
                        
                    logger.info(f"After navigation, current URL: {current_url}")
                except Exception as nav_error:
                    logger.exception(f"Failed to navigate to feed: {nav_error}")
                    return False

            # Quick URL checks - if on login page, definitely not logged in
            if any(x in current_url for x in ['/login', '/signup', '/checkpoint', '/authwall']):
                logger.info(f"Detected not logged in via URL: {current_url}")
                return False
            
            # If on feed, network, profile, or jobs - definitely logged in
            if any(x in current_url for x in ['/feed', '/mynetwork', '/in/', '/jobs']):
                logger.info(f"Detected logged in via URL: {current_url}")
                return True
            
            # Wait for page to load
            try:
                self.page.wait_for_load_state('domcontentloaded', timeout=5000)
            except:
                pass
            
            # Check for logged-in elements
            selectors = [
                "header[id='global-nav']",
                "div.global-nav__content", 
                "div#global-nav-search",
                "button[aria-label*='Me']",  # "Me" dropdown menu
                "nav.global-nav",
            ]
            
            for selector in selectors:
                try:
                    element = self.page.query_selector(selector)
                    if element:
                        logger.info(f"Detected logged in via element: {selector}")
                        return True
                except:
                    continue
            
            logger.info("No logged-in indicators found")
            return False
            
        except Exception as e:
            logger.exception(f"Error checking login status: {e}")
            return False

    def login(self, email, password, profile_url=None):
        if self.is_logged_in():
            if profile_url:
                logger.info(f"Already logged in, navigating to {profile_url}.")
                self.page.goto(profile_url, timeout=60000)
                self.random_delay(3, 5)
            return True
        try:
            logger.info(f"Attempting to Log in with {email}...")
            self.page.goto("https://www.linkedin.com/login", timeout=60000)

            # Fill in email
            logger.info("Entering email...")
            email_input = self.page.wait_for_selector("#username", timeout=10000)
            email_input.fill(email)
            self.random_delay(0.5, 1.5)
            
            # Fill in password
            logger.info("Entering password...")
            password_input = self.page.wait_for_selector("#password", timeout=10000)
            password_input.fill(password)
            self.random_delay(0.5, 1.5)
            
            # Click login button
            logger.info("Clicking login button...")
            login_button = self.page.wait_for_selector("button[type='submit']", timeout=10000)
            login_button.click()

            self.random_delay(3,5)

            current_url = self.page.url.lower()
            logger.info(f"Post-login URL: {current_url}")
            
            # Check for OTP/verification challenge
            if any(indicator in current_url for indicator in ['checkpoint', 'challenge', 'verify']):
                logger.warning(f"Security checkpoint/OTP verification detected for {email}!")
                otp_handled = self.otp_handler(email)

                if otp_handled:
                    # Check if login successful after OTP
                    self.random_delay(3, 5)
                    if self.is_logged_in():
                        logger.info(f"OTP verification successful for {email}!")
                        self.save_cookies()
                        
                        if profile_url:
                            self.page.goto(profile_url)
                            self.random_delay()
                        return True
                return False
            
            if self.is_logged_in():
                logger.info(f"Login successful! for {email}")
                self.save_cookies()
                if profile_url:
                    self.page.goto(profile_url, timeout=60000)
                    self.random_delay(2,4)
                return True
            else:
                logger.error(f"Login failed for {email}. Not properly logged in.")
                return False

        except Exception as e:
            logger.exception(f"Error during automated login: {e}")
            return False
    
    def otp_handler(self, email):
        try:
            logger.info(f"Attempting to handle OTP verification for {email}")
            logger.info("Waiting for OTP verification page to load...")
            
            try:
                self.page.wait_for_selector("div.form__content, input[name='pin'], input[validation='pin']", timeout=10000)
                logger.info("OTP page elements detected")
            except:
                logger.warning("OTP page elements not detected, proceeding anyway...")
            
            time.sleep(2)
            # Try different OTP input selectors based on actual LinkedIn HTML
            otp_selectors = [
                # Most specific selector based on your HTML
                "input#input__phone_verification_pin",
                "input[name='pin'][validation='pin']",
                "input.form__input--text.input_verification_pin",
                
                # Fallback selectors
                "div.form__content input[name='pin']",
                "input[id='input__phone_verification_pin']",
                "input[validation='pin']",
                "input[name='pin']",
                "input[maxlength='6'][type='tel']",
                "input[pattern*='0-9']",
                "input[aria-label*='code']",
                "input[aria-label*='Code']",
                "input[type='tel'][maxlength='6']",
                
                # XPath-style selectors (converted to CSS)
                "div[class*='form__content'] input[name='pin']",
                "div[class*='form__content'] input[type='tel']",
                
                # Generic fallbacks
                "input[placeholder*='code']",
                "input[placeholder*='Code']",
                "input[id*='verification']",
                "input[id*='pin']"
            ]
            
            # First, let's debug what's actually on the page
            logger.info("Debugging: Looking for OTP input field...")
            
            # Check if we're on the right page
            page_content = self.page.content()
            if "verification" in page_content.lower() or "pin" in page_content.lower():
                logger.info("Detected verification/PIN page")
            else:
                logger.warning("May not be on OTP verification page")
            
            # Try to find the form__content div first
            form_content = None
            try:
                form_content = self.page.wait_for_selector("div.form__content", timeout=5000)
                if form_content:
                    logger.info("Found form__content div")
                else:
                    logger.warning("form__content div not found")
            except:
                logger.warning("form__content div not found")
            
            # Now try to find the OTP input
            otp_input = None
            
            for i, selector in enumerate(otp_selectors):
                try:
                    logger.info(f"Trying selector {i+1}/{len(otp_selectors)}: {selector}")
                    otp_input = self.page.wait_for_selector(selector, timeout=2000)
                    if otp_input:
                        logger.info(f"Found OTP input field")
                        break
                except Exception as e:
                    logger.debug(f"Selector failed: {selector} - {str(e)}")
                    continue
            
            if not otp_input:
                logger.error("Could not find OTP input field with any selector")
                return False
            
            # Get OTP code
            otp_code = self.get_otp(email)
            
            if not otp_code:
                logger.error("No OTP code available")
                return False
            
            # Enter OTP code
            logger.info(f"Entering OTP code: {'*' * len(otp_code)}")
            otp_input.fill(otp_code)
            time.sleep(1)
            
            # Try to find and click submit button
            submit_selectors = [
                "button[type='submit']",
                "button[data-test-id='submit-btn']",
                "button[aria-label='Submit']",
                "button:has-text('Submit')",
                "button:has-text('Verify')",
                "button:has-text('Continue')"
            ]
            
            submit_button = None
            for selector in submit_selectors:
                try:
                    submit_button = self.page.query_selector(selector)
                    if submit_button:
                        logger.info(f"Found submit button: {selector}")
                        break
                except:
                    continue
            
            if submit_button:
                logger.info("Clicking submit button")
                submit_button.click()
                time.sleep(3)
                return True
            else:
                logger.warning("Could not find submit button, trying Enter key")
                otp_input.press("Enter")
                time.sleep(3)
                return True
            
        except Exception as e:
            logger.exception(f"Error handling OTP verification: {e}")
            return False

    def get_otp(self, email):
        secret = os.getenv(f"LINKEDIN_2FA_SECRET_{email.split('@')[0]}")
        if not secret:
            logger.exception(f"Secret not found for: {email}")
            return None
        totp = pyotp.TOTP(secret)
        otp_code = totp.now()
        return otp_code

    def rotate_account(self, state_file="account_state.json", increment=True):
        """Rotate to next available account with proper state management"""
        accounts_string = str(os.getenv("LINKEDIN_ACCOUNTS"))
        max_usage = MAX_SCRAPE_PER_ACCOUNT
        accounts = [{"email": e.strip(), "password": p.strip()} 
                    for e, p in (pair.split(":") for pair in accounts_string.split(";"))]

        # Load or initialize state
        if os.path.exists(state_file):
            with open(state_file, "r") as f:
                state = json.load(f)
            
            # Clean up old format if exists (migrate to new format)
            if "usage" not in state:
                # Old format detected - migrate to new format
                logger.info("Migrating state file to new format...")
                old_state = {k: v for k, v in state.items() 
                            if k not in ["last_account_index", "current_account"]}
                state = {
                    "usage": old_state,
                    "last_account_index": state.get("last_account_index", -1),
                    "current_account": state.get("current_account")
                }
            else:
                # Remove any duplicate keys from old format
                keys_to_keep = ["usage", "last_account_index", "current_account"]
                state = {k: v for k, v in state.items() if k in keys_to_keep}
        else:
            state = {
                "usage": {acc["email"]: 0 for acc in accounts},
                "last_account_index": -1,
                "current_account": None
            }
        
        usage_dict = state["usage"]
        last_index = state.get("last_account_index", -1)
        current_account = state.get("current_account")
        
        # Check if all accounts reached max_usage
        if all(usage_dict.get(acc["email"], 0) >= max_usage for acc in accounts):
            logger.info("All accounts reached max usage. Resetting all counters.")
            usage_dict = {acc["email"]: 0 for acc in accounts}
            last_index = -1
            current_account = None
        
        # Start from the next account after the last used one
        start_index = (last_index + 1) % len(accounts)
        
        # Try each account starting from start_index
        for i in range(len(accounts)):
            current_index = (start_index + i) % len(accounts)
            acc = accounts[current_index]
            email = acc["email"]
            usage = usage_dict.get(email, 0)

            if usage >= max_usage:
                logger.info(f"Account {email} reached max usage ({usage}/{max_usage}). Trying next account.")
                continue
            
            # Found available account
            if increment:
                usage_dict[email] = usage + 1
                logger.info(f"Using account: {email} (Usage: {usage_dict[email]}/{max_usage})")
            else:
                logger.info(f"Selected account: {email} (Current usage: {usage}/{max_usage})")
            
            # Update state with ONLY the new format keys
            state = {
                "usage": usage_dict,
                "last_account_index": current_index,
                "current_account": email
            }
            
            # Save updated state
            with open(state_file, "w") as f:
                json.dump(state, f, indent=2)

            return acc["email"], acc["password"], usage
    
        # If we reach here, no accounts available
        raise Exception("All accounts exhausted.")

    def increment_account_usage(self, email, state_file="account_state.json"):
        """Increment usage counter for an account"""
        try:
            if os.path.exists(state_file):
                with open(state_file, "r") as f:
                    state = json.load(f)
            else:
                state = {
                    "usage": {},
                    "last_account_index": -1,
                    "current_account": None
                }
            
            # Handle both old and new format
            if "usage" in state:
                # New format
                usage_dict = state["usage"]
                usage_dict[email] = usage_dict.get(email, 0) + 1
                state["usage"] = usage_dict
            else:
                # Old format - migrate
                state["usage"] = {email: state.get(email, 0) + 1}
                # Remove old keys
                if email in state:
                    del state[email]
            
            # Save with clean format (only these 3 keys)
            clean_state = {
                "usage": state["usage"],
                "last_account_index": state.get("last_account_index", -1),
                "current_account": state.get("current_account", email)
            }
            
            with open(state_file, "w") as f:
                json.dump(clean_state, f, indent=2)
            
            logger.info(f"Incremented usage for {email}: {clean_state['usage'][email]}")
            
        except Exception as e:
            logger.exception(f"Failed to increment account usage: {e}")
        
    def clear_browser_data(self):
        try:
            logger.info("Clearing browser data...")
            if hasattr(self, 'browser') and self.browser:
                try:
                    self.browser.close()
                    logger.info("Browser closed.")
                except Exception as e:
                    logger.exception(f"Error closing browser: {e}")
            
            if hasattr(self, 'playwright') and self.playwright:
                try:
                    self.playwright.stop()
                    logger.info("Playwright stopped.")
                except Exception as e:
                    logger.exception(f"Error stopping playwright: {e}")
            
            time.sleep(2)
            
            if self.user_data_dir.exists():
                try:
                    shutil.rmtree(self.user_data_dir, ignore_errors=True)
                    logger.info("Deleted user data directory.")
                except Exception as e:
                    logger.exception(f"Error deleting user data directory: {e}")
            
            self.user_data_dir.mkdir(exist_ok=True)
            
            time.sleep(3)

            logger.info("Browser data cleared successfully.")
            return True
        
        except Exception as e: 
            logger.exception(f"Error clearing browser data: {e}")
            return False

    def ensure_logged_in(self, profile_url, max_login_retries=3):
        # Check if we have a current valid account
        state_file = "account_state.json"
        current_account_email = None
        current_account_password = None
        
        try:
            if os.path.exists(state_file):
                with open(state_file, 'r') as f:
                    state = json.load(f)
                
                current_account = state.get("current_account")
                
                if current_account:
                    # Check if current account hasn't reached max usage
                    usage = state.get("usage", {}).get(current_account, 0)
                    
                    if usage < MAX_SCRAPE_PER_ACCOUNT:
                        # Current account is still valid
                        logger.info(f"Using existing account: {current_account} (Usage: {usage}/{MAX_SCRAPE_PER_ACCOUNT})")
                        
                        # Get password for current account
                        accounts_string = str(os.getenv("LINKEDIN_ACCOUNTS"))
                        accounts = [{"email": e.strip(), "password": p.strip()} 
                                for e, p in (pair.split(":") for pair in accounts_string.split(";"))]
                        
                        for acc in accounts:
                            if acc["email"] == current_account:
                                current_account_email = current_account
                                current_account_password = acc["password"]
                                break
                    else:
                        logger.info(f"Current account {current_account} reached max usage ({usage}/{MAX_SCRAPE_PER_ACCOUNT})")
        except Exception as e:
            logger.exception(f"Could not load current account state: {e}")
        
        # Try logging in with account rotation on failure
        login_successful = False
        attempts_made = 0
        
        # First, try with current account if available
        if current_account_email and current_account_password:
            logger.info(f"Attempting login with current account: {current_account_email}")
            
            if self.login(current_account_email, current_account_password, profile_url):
                login_successful = True
                self.increment_account_usage(current_account_email)
                logger.info(f"Logged in successfully with {current_account_email}")
            else:
                logger.exception(f"Login failed with current account: {current_account_email}")
                attempts_made += 1
        
        # If current account failed or doesn't exist, try rotating accounts
        if not login_successful:
            remaining_retries = max_login_retries - attempts_made
            
            for attempt in range(remaining_retries):
                try:
                    logger.info(f"Rotation attempt {attempt + 1}/{remaining_retries}")
                    
                    # Clear browser for fresh start with new account
                    if attempt > 0 or current_account_email:  # Clear if we already tried an account
                        logger.info("Clearing browser data for account switch...")
                        self.clear_browser_data()
                        self.random_delay(3, 5)
                        self.initialize_browser()
                    
                    # Get next account credentials
                    email, password, current_usage = self.rotate_account(increment=False)
                    
                    # Skip if it's the same account we just tried
                    if email == current_account_email:
                        logger.info(f"Skipping {email} - already tried")
                        continue
                    
                    logger.info(f"Trying account: {email}")
                    
                    # Try to login
                    if self.login(email, password, profile_url):
                        login_successful = True
                        self.increment_account_usage(email)
                        logger.info(f"Logged in successfully with {email}")
                        break
                    else:
                        logger.exception(f"Login failed with: {email}")
                        
                except Exception as e:
                    logger.exception(f"Error in rotation attempt {attempt + 1}: {e}")
        
        if not login_successful:
            logger.error(f"Failed to login after trying {attempts_made + remaining_retries} accounts")
            return False
            
        return True

    def close(self):
        try:
            self.save_cookies()

            if self.browser:
                self.browser.close()
            if self.playwright: 
                self.playwright.stop()
            
            logger.info("Browser closed successfully.") 

        except Exception as e: 
            logger.exception(f"Error closing browser: {e}")
