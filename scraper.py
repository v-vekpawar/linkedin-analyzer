"""
LinkedIn Profile Scraper
Handles scraping LinkedIn profile data using Selenium WebDriver
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from config import SELENIUM_TIMEOUT, SELENIUM_IMPLICIT_WAIT

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LinkedInScraper:
    """LinkedIn Profile Scraper using Selenium WebDriver"""
    
    def __init__(self, headless=False):
        """
        Initialize the LinkedIn scraper
        
        Args:
            headless (bool): Run browser in headless mode
        """
        self.driver = None
        self.headless = headless
        self.wait = None
        
    def setup_driver(self):
        """Set up Chrome WebDriver with local driver"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")

            # ✅ Use your downloaded driver directly
            service = Service("drivers/chromedriver-win64/chromedriver.exe")
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            self.driver.implicitly_wait(SELENIUM_IMPLICIT_WAIT)
            self.wait = WebDriverWait(self.driver, SELENIUM_TIMEOUT)

            logger.info("✅ Chrome WebDriver initialized successfully (manual driver)")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize WebDriver: {str(e)}")
            return False

    
    def login_to_linkedin(self, profile_url=None):
        """
        Open LinkedIn login page and wait for manual login
        If profile_url is provided, navigate to it after login.
        Returns:
            bool: True if login page loaded successfully
        """
        try:
            logger.info("\n\n\t\tOpening LinkedIn login page...\n\n")
            self.driver.get("https://www.linkedin.com/login")
            self.wait.until(EC.presence_of_element_located((By.ID, "username")))
            logger.info("\n\t\tLinkedIn login page loaded. Please log in manually.")
            logger.info("\t\tWaiting for manual login completion (auto-detect)...")
            max_wait = 300  # seconds
            poll_interval = 2  # seconds
            waited = 0
            while waited < max_wait:
                current_url = self.driver.current_url
                if "linkedin.com" in current_url and "login" not in current_url:
                    logger.info("\n\n\t\tLogin detected! Proceeding...\n\n")
                    break
                try:
                    if self.driver.find_elements(By.ID, "global-nav"):
                        logger.info("\n\n\t\tLogin detected by nav bar! Proceeding...\n\n")
                        break
                except Exception:
                    pass
                time.sleep(poll_interval)
                waited += poll_interval
            else:
                logger.error("\n\n\t\tTimeout waiting for LinkedIn login to complete.\n\n")
                return False
            # After login, navigate to the profile page if provided
            if profile_url:
                logger.info(f"\n\n\t\tNavigating to profile page after login: {profile_url}\n\n")
                self.driver.get(profile_url)
                time.sleep(3)  # Wait for profile page to load
            return True
        except TimeoutException:
            logger.error("\n\n\t\tTimeout waiting for login page to load\n\n")
            return False
        except Exception as e:
            logger.error(f"\n\n\t\tError during login process: {str(e)}\n\n")
            return False
    
    def scrape_profile(self, profile_url):
        """
        Scrape LinkedIn profile data
        Args:
            profile_url (str): LinkedIn profile URL to scrape
        Returns:
            dict: Scraped profile data
        """
        try:
            # No need to navigate again, already on profile page after login
            logger.info(f"Scraping profile: {profile_url}")
            time.sleep(2)  # Ensure page is loaded
            profile_data = {
                'name': self._extract_name(),
                'headline': self._extract_headline(),
                'about': self._extract_about(),
                'experience': self._extract_experience(),
                'skills': self._extract_skills(),
                'url': profile_url
            }
            logger.info("\n\n\t\tProfile scraping completed successfully\n\n")
            return profile_data
        except Exception as e:
            logger.error(f"\n\n\t\tError scraping profile: {str(e)}\n\n")
            return None
    
    def _extract_name(self):
        """Extract profile name"""
        try:
            # Try multiple selectors for name
            selectors = [
                ".v-align-middle.break-words",
                "h1.text-heading-xlarge",
                ".text-heading-xlarge",
                "h1[aria-label*='name']",
                ".pv-text-details__left-panel h1"
            ]
            
            for selector in selectors:
                try:
                    element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    return element.text.strip()
                except TimeoutException:
                    continue
            
            return "Name not found"
            
        except Exception as e:
            logger.warning(f"Error extracting name: {str(e)}")
            return "Name not found"
    
    def _extract_headline(self):
        """Extract profile headline"""
        try:
            selectors = [
                ".text-body-medium.break-words",
                ".pv-text-details__left-panel .text-body-medium",
                "[data-section='headline'] .text-body-medium"
            ]
            
            for selector in selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    return element.text.strip()
                except NoSuchElementException:
                    continue
            
            return "Headline not found"
            
        except Exception as e:
            logger.warning(f"Error extracting headline: {str(e)}")
            return "Headline not found"
    
    def _extract_about(self):
        """Extract about section"""
        try:
            # Click "Show more" if available
            try:
                show_more = self.driver.find_element(By.CSS_SELECTOR, "[aria-label='Show more']")
                show_more.click()
                time.sleep(1)
            except NoSuchElementException:
                pass
            
            selectors = [
                ".pv-shared-text-with-see-more span",
                ".pv-about__summary-text",
                "[data-section='summary'] .pv-shared-text-with-see-more"
            ]
            
            for selector in selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    return element.text.strip()
                except NoSuchElementException:
                    continue
            
            return "About section not found"
            
        except Exception as e:
            logger.warning(f"Error extracting about section: {str(e)}")
            return "About section not found"
    
    def _extract_experience(self):
        """Extract work experience"""
        try:
            experience_list = []
            
            # Navigate to experience section
            try:
                experience_section = self.driver.find_element(By.CSS_SELECTOR, "[data-section='experience']")
                experience_section.click()
                time.sleep(2)
            except NoSuchElementException:
                # Try alternative navigation
                try:
                    experience_link = self.driver.find_element(By.CSS_SELECTOR, "a[href*='experience']")
                    experience_link.click()
                    time.sleep(2)
                except NoSuchElementException:
                    pass
            
            # Extract experience items
            experience_items = self.driver.find_elements(By.CSS_SELECTOR, ".pvs-list__item--line-separated")
            
            for item in experience_items[:5]:  # Limit to first 5 experiences
                try:
                    title_element = item.find_element(By.CSS_SELECTOR, ".t-bold span")
                    company_element = item.find_element(By.CSS_SELECTOR, ".t-normal span")
                    
                    title = title_element.text.strip()
                    company = company_element.text.strip()
                    
                    if title and company:
                        experience_list.append({
                            'title': title,
                            'company': company
                        })
                except NoSuchElementException:
                    continue
            
            return experience_list
            
        except Exception as e:
            logger.warning(f"Error extracting experience: {str(e)}")
            return ["Experience not found"]
    
    def _extract_skills(self):
        """Extract skills"""
        try:
            skills_list = []
            
            # Navigate to skills section
            try:
                skills_section = self.driver.find_element(By.CSS_SELECTOR, "[data-section='skills']")
                skills_section.click()
                time.sleep(2)
            except NoSuchElementException:
                pass
            
            # Extract skills
            skill_elements = self.driver.find_elements(By.CSS_SELECTOR, ".pvs-list__item--line-separated .t-bold span")
            
            for element in skill_elements[:10]:  # Limit to first 10 skills
                skill = element.text.strip()
                if skill and len(skill) > 1:
                    skills_list.append(skill)
            
            return skills_list
            
        except Exception as e:
            logger.warning(f"Error extracting skills: {str(e)}")
            return ["Skills not found"]
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed")


def scrape_linkedin_profile(profile_url, headless=False):
    """
    Main function to scrape a LinkedIn profile
    
    Args:
        profile_url (str): LinkedIn profile URL
        headless (bool): Run browser in headless mode
        
    Returns:
        dict: Scraped profile data or None if failed
    """
    scraper = LinkedInScraper(headless=headless)
    
    try:
        # Setup driver
        if not scraper.setup_driver():
            return None
        
        # Login to LinkedIn
        if not scraper.login_to_linkedin(profile_url):
            return None
        
        # Scrape profile
        profile_data = scraper.scrape_profile(profile_url)
        
        return profile_data
        
    except Exception as e:
        logger.error(f"Error in scraping process: {str(e)}")
        return None
        
    finally:
        scraper.close()


if __name__ == "__main__":
    # Example usage
    profile_url = input("Enter LinkedIn profile URL: ")
    result = scrape_linkedin_profile(profile_url)
    
    if result:
        print("\n\n\t\tScraped Profile Data:\n\n")
        print(result)
    else:
        print("\n\n\t\tFailed to scrape profile\n\n") 