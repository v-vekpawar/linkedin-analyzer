"""
LinkedIn Profile Scraper — Playwright version with persistent login.
"""

import time
import random
import logging
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from config import SELENIUM_TIMEOUT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LinkedInScraper:
    """LinkedIn Profile Scraper using Playwright with persistent context."""

    def __init__(self, headless=True):
        self.headless = headless
        self.playwright = sync_playwright().start()
        self.user_data_dir = Path("./playwright_user_data")
        self.cookies_file = self.user_data_dir / "linkedin_cookies.json"
        
        self.user_data_dir.mkdir(exist_ok=True)
        
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
                logger.info(f"✅ Saved {len(linkedin_cookies)} cookies")
                return True
            return False
        except Exception as e:
            logger.error(f"Cookie save error: {e}")
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
                logger.info(f"✅ Loaded {len(cookies)} cookies")
                return True
            return False
        except Exception as e:
            logger.error(f"Cookie load error: {e}")
            return False

    def random_delay(self, min_sec=1, max_sec=3):
        """Add random delays to mimic human behavior."""
        time.sleep(random.uniform(min_sec, max_sec))

    def login_to_linkedin(self, profile_url=None):
        """Log in once, then reuse session cookies forever."""
        try:
            logger.info("Checking if already logged in...")
            self.page.goto("https://www.linkedin.com/feed")
            self.random_delay(3, 5)
            
            if self._is_logged_in():
                logger.info("Already logged in! ✅")
                if profile_url:
                    self.page.goto(profile_url)
                    self.random_delay()
                return True

            if self.headless:
                logger.error("❌ Not logged in! Run with headless=False first to login manually")
                return False
            
            logger.info("Opening login page...")
            self.page.goto("https://www.linkedin.com/login")
            self.random_delay(2, 4)
            
            logger.info("Please log in manually in the browser...")

            # Wait for login completion for 3 minutes
            for i in range(60):
                logger.info(f"Waiting for login... ({i+1}/60)")
                time.sleep(3)
                try:
                    actual_url = self.page.evaluate("window.location.href").lower()
                    playwright_url = self.page.url.lower()
                    logger.info(f"Browser URL: {actual_url}")
                    
                    if any(x in actual_url for x in ['/feed', '/mynetwork', '/in/', '/jobs']):
                        logger.info("Detected successful navigation, checking login status...")
                        self.random_delay(3, 5)
                        
                        if self._is_logged_in():
                            logger.info("✅ Login successful!")
                            self.save_cookies()
                            break
                    
                except Exception as check_error:
                    if "Execution context was destroyed" in str(check_error):
                        logger.debug("Page navigation in progress...")
                    else:
                        logger.warning(f"Error during login check: {check_error}")
                    continue
            else:
                logger.error("⏰ Timeout waiting for login.")
                return False

            if profile_url:
                self.page.goto(profile_url)
                self.random_delay()
            return True

        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            return False

    def _is_logged_in(self):
        """Check if user is logged in to LinkedIn"""
        try:
            try:
                current_url = self.page.evaluate("window.location.href").lower()
            except:
                current_url = self.page.url.lower()
            
            logger.info(f"Checking login status. Current URL: {current_url}")

            # Quick URL checks
            if any(x in current_url for x in ['/login', '/signup', '/checkpoint']):
                logger.info(f"❌ Detected no login via URL: {current_url}")
                return False
            
            if any(x in current_url for x in ['/feed', '/mynetwork', '/in/', '/jobs']):
                logger.info(f"✅ Detected login via URL: {current_url}")
                return True
            
            # Wait for page load
            try:
                self.page.wait_for_load_state('domcontentloaded', timeout=5000)
            except:
                pass
            
            # Check key elements (your robust selectors)
            selectors = [
                "header[id='global-nav']",
                "div[class='global-nav__content']", 
                "div[class='profile-card-member-details']",
                "main[aria-label='Main Feed']",
                "div[id='global-nav-search']"
            ]
            
            return any(self.page.query_selector(s) for s in selectors)
            
        except Exception as e:
            logger.warning(f"Error checking login status: {e}")
            return False

    def scrape_profile(self, profile_url):
        """Scrape LinkedIn profile data."""
        if not self.login_to_linkedin(profile_url):
            logger.error("Login failed, cannot scrape.")
            return None

        try:
            logger.info(f"Scraping profile: {profile_url}")
            self.random_delay()
            
            profile_data = {
                'name': self._extract_name(),
                'headline': self._extract_headline(),
                'about': self._extract_about(),
                'experience': self._extract_experience(),
                'skills': self._extract_skills(),
                'education': self._extract_education(),
                'url': profile_url
            }
            logger.info("✅ Profile scraping completed successfully")
            return profile_data

        except Exception as e:
            logger.error(f"❌ Error scraping profile: {str(e)}")
            return None

    def _extract_name(self):
        try:
            self.page.wait_for_selector("//h1", timeout=SELENIUM_TIMEOUT * 1000)
            element = self.page.query_selector("//h1")
            return element.inner_text().strip() if element else "Name not found"
        except Exception as e:
            logger.warning(f"Name extraction error: {str(e)}")
            return "Name not found"

    def _extract_headline(self):
        try:
            element = self.page.query_selector("//h1/ancestor::div[1]/following-sibling::div[contains(@class,'text-body-medium')]")
            return element.inner_text().strip() if element else "Headline not found"
        except Exception as e:
            logger.warning(f"Headline extraction error: {str(e)}")
            return "Headline not found"

    def _extract_about(self):
        try:
            about_header = self.page.query_selector("//h2[.//span[text()='About']]")
            if about_header:
                try:
                    show_more = self.page.query_selector("//div[contains(@class, 'display-flex ph5 pv3')]//button")
                    if show_more:
                        show_more.click()
                        self.random_delay(1, 2)
                except:
                    pass

                selectors = [
                    "//div[contains(@class, 'display-flex ph5 pv3')]//span[@aria-hidden='true']",
                    "//section[contains(@class, 'pv-about-section')]//span",
                    "//div[contains(@class, 'pv-shared-text')]//span",
                    "//div[contains(@id, 'about')]//span"
                ]

                for selector in selectors:
                    element = self.page.query_selector(selector)
                    if element:
                        text = element.inner_text().strip()
                        if text:
                            return text
            return "About section not found"
        except Exception as e:
            return f"Error: {e}"

    def _extract_experience(self):
        try:
            experience_list = []
            experience_header = self.page.locator("//h2[.//span[text()='Experience']]").first
            if experience_header.count() == 0:
                return ["Experience not found"]

            experience_container = experience_header.locator("xpath=./ancestor::div[4]").first
            experience_section = experience_container.locator("xpath=./following-sibling::div").first
            experience_items = experience_section.locator("xpath=.//li[contains(@class, 'artdeco-list__item')]").all()

            for item in experience_items[:5]:
                title_element = item.locator("xpath=.//div[contains(@class, 't-bold')]//span[@aria-hidden='true']").first
                company_element = item.locator("xpath=.//span[contains(@class,'t-normal')]//span[@aria-hidden='true']").first

                title = title_element.inner_text().strip() if title_element else ""
                company = company_element.inner_text().strip() if company_element else ""

                if title and company:
                    experience_list.append({'title': title, 'company': company})

            return experience_list if experience_list else ["Experience not found"]
        except Exception as e:
            logger.warning(f"Experience extraction error: {str(e)}")
            return ["Experience not found"]

    def _extract_skills(self):
        try:
            skills_list = []
            skills_header = self.page.locator("//h2[.//span[text()='Skills']]")
            if skills_header.count() == 0:
                return ["Skills not found"]

            skills_container = skills_header.locator("xpath=./ancestor::div[4]").first
            skills_section = skills_container.locator("xpath=./following-sibling::div").first
            show_all_link = skills_section.locator("xpath=.//div[contains(@class,'pv-action')]//a[.//span[contains(normalize-space(.), 'Show all') and contains(normalize-space(.), 'skills')]]")

            if show_all_link.count() > 0:
                logger.info("Clicking 'Show all skills'...")
                handle = show_all_link.element_handle()
                if handle:
                    self.page.evaluate("element => element.scrollIntoView({block: 'center'})", handle)
                    self.random_delay(1, 2)
                
                with self.page.expect_navigation(timeout=15000):
                    show_all_link.click()
                
                self.random_delay(2, 4)
                
                try:
                    self.page.wait_for_selector("//section[@class='artdeco-card pb3']//li[contains(@class,'artdeco-list__item')]", timeout=10000)
                    skill_items = self.page.locator("xpath=//section[@class='artdeco-card pb3']//li[contains(@class,'artdeco-list__item')]").all()
                    
                    for item in skill_items[:15]:
                        skill_element = item.locator("xpath=.//div[contains(@class, 't-bold')]//span[@aria-hidden='true']").first
                        if skill_element:
                            skill = skill_element.inner_text().strip()
                            if skill:
                                skills_list.append(skill)
                    
                    skills_list = list(dict.fromkeys(skills_list))  # Remove duplicates while preserving order
                except Exception as wait_error:
                    logger.warning(f"Skills content didn't load: {wait_error}")
                
                # Navigate back
                try:
                    back_arrow = self.page.query_selector("//button[@aria-label='Back to the main profile page']")
                    if back_arrow:
                        back_arrow.click()
                        self.page.wait_for_selector("//h1", timeout=10000)
                    else:
                        original_url = self.page.url.split('/details/')[0] + '/'
                        self.page.goto(original_url)
                        self.random_delay()
                except Exception as back_error:
                    logger.warning(f"Error navigating back: {back_error}")
            else:
                # Extract from main page
                main_page_skills = skills_section.locator("xpath=.//li[contains(@class,'artdeco-list__item')]").all()
                for item in main_page_skills[:10]:
                    skill_element = item.locator("xpath=.//div[contains(@class, 't-bold')]//span[@aria-hidden='true']").first
                    if skill_element:
                        skill = skill_element.inner_text().strip()
                        if skill:
                            skills_list.append(skill)

            return skills_list if skills_list else ["Skills not found"]
        except Exception as e:
            logger.warning(f"Skills extraction error: {str(e)}")
            return ["Skills not found"]

    def _extract_education(self):
        try:
            education_list = []
            education_header = self.page.locator("//h2[.//span[text()='Education']]")
            if education_header.count() == 0:
                return ["Education not found"]

            education_container = education_header.locator("xpath=./ancestor::div[4]").first
            education_section = education_container.locator("xpath=./following-sibling::div").first
            
            # Try main page first
            main_page_education = education_section.locator("xpath=.//li[contains(@class,'artdeco-list__item')]").all()
            if len(main_page_education) > 0:
                for item in main_page_education[:10]:
                    education_element = item.locator("xpath=.//div[contains(@class, 't-bold')]//span[@aria-hidden='true']").first
                    if education_element:
                        education = education_element.inner_text().strip()
                        if education:
                            education_list.append(education)
                if education_list:
                    return education_list

            # Try "Show all" approach if main page failed
            show_all_link = education_section.locator("xpath=.//div[contains(@class,'pv-action')]//a[.//span[contains(normalize-space(.), 'Show all') and contains(normalize-space(.), 'educations')]]")
            if show_all_link.count() > 0:
                handle = show_all_link.element_handle()
                if handle:
                    self.page.evaluate("element => element.scrollIntoView({block: 'center'})", handle)
                    self.random_delay(1, 2)
                
                with self.page.expect_navigation(timeout=15000):
                    show_all_link.click()
                
                self.random_delay(2, 4)
                
                try:
                    self.page.wait_for_selector("//section[contains(@class,'artdeco-card')]//li[contains(@class,'artdeco-list__item')]", timeout=10000)
                    education_items = self.page.locator("xpath=//section[contains(@class,'artdeco-card')]//li[contains(@class,'artdeco-list__item')]").all()
                    
                    for item in education_items[:10]:
                        education_element = item.locator("xpath=.//div[contains(@class, 't-bold')]//span[@aria-hidden='true']").first
                        if education_element:
                            education = education_element.inner_text().strip()
                            if education:
                                education_list.append(education)
                except Exception as wait_error:
                    logger.warning(f"Education content didn't load: {wait_error}")
                
                # Navigate back
                try:
                    back_arrow = self.page.query_selector("//button[@aria-label='Back to the main profile page']")
                    if back_arrow:
                        back_arrow.click()
                        self.page.wait_for_selector("//h1", timeout=10000)
                    else:
                        original_url = self.page.url.split('/details/')[0] + '/'
                        self.page.goto(original_url)
                        self.random_delay()
                except Exception as back_error:
                    logger.warning(f"Error navigating back: {back_error}")

            return education_list if education_list else ["Education not found"]
        except Exception as e:
            logger.warning(f"Education extraction error: {str(e)}")
            return ["Education not found"]

    def close(self):
        """Close browser and save final state"""
        try:
            # Ensure cookies are saved before closing
            self.save_cookies()
            self.browser.close()
            self.playwright.stop()
        except Exception as e:
            logger.error(f"Error during close: {e}")


def scrape_linkedin_profile(profile_url, headless=False):
    scraper = LinkedInScraper(headless=headless)
    try:
        profile_data = scraper.scrape_profile(profile_url)
        return profile_data
    except Exception as e:
        logger.error(f"Scrape error: {str(e)}")
        return None
    finally:
        scraper.close()