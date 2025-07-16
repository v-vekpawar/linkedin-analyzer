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
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
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

            # ✅ NEW: Use persistent Chrome user data folder
            chrome_options.add_argument("--user-data-dir=/app/chrome-profile")

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
        If session cookie is valid → skip login.
        Else → open login page & wait for manual login.
        """
        try:
            logger.info("\n\n\t\tChecking if already logged in...\n\n")

            # Open LinkedIn home page directly
            self.driver.get("https://www.linkedin.com/login/")

            time.sleep(2)

            current_url = self.driver.current_url
            logger.info(f"\n\t\tCurrent URL: {current_url}")

            # ✅ If we're on feed → we are logged in
            if "feed" in current_url:
                logger.info("\n\t\tAlready logged in, skipping manual login.")

                # Go to profile page if provided
                if profile_url:
                    logger.info(f"\n\t\tNavigating to profile: {profile_url}")
                    self.driver.get(profile_url)
                    time.sleep(2)

                return True

            # ✅ If redirected to login → manual login needed
            logger.info("\n\t\tNot logged in → opening login page for manual login.")
            self.driver.get("https://www.linkedin.com/login")
            self.wait.until(EC.presence_of_element_located((By.ID, "username")))

            logger.info("\n\t\tWaiting for you to log in manually...")

            max_wait = 300
            poll_interval = 2
            waited = 0

            while waited < max_wait:
                current_url = self.driver.current_url
                if "feed" in current_url or ("linkedin.com" in current_url and "login" not in current_url):
                    logger.info("\n\t\tLogin detected, proceeding!")
                    break
                time.sleep(poll_interval)
                waited += poll_interval
            else:
                logger.error("\n\t\tTimeout waiting for login.")
                return False

            # After manual login → go to profile page
            if profile_url:
                logger.info(f"\n\t\tNavigating to profile page: {profile_url}")
                self.driver.get(profile_url)
                time.sleep(2)

            return True

        except Exception as e:
            logger.error(f"\n\t\tError during login check: {str(e)}")
            return False
    
    def scrape_profile(self, profile_url):
        """
        Scrape LinkedIn profile data
        Args:
            profile_url (str): LinkedIn profile URL to scrape
        Returns:
            dict: Scraped profile data
        """
        if not self.login_to_linkedin(profile_url):  # ✅ Fixed
            logger.error("Login failed, cannot scrape profile")
            return None

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
        """Extract profile name using robust XPath only"""
        try:
            # Try robust XPath for <h1>
            element = self.wait.until(EC.visibility_of_element_located((By.XPATH,"//h1")))
            name = element.text.strip()
            return name if name else "Name not found"

        except Exception as e:
            logger.warning(f"Error extracting name: {str(e)}")
            return "Name not found"
    
    def _extract_headline(self):
        """Extract headline using the confirmed structure"""
        try:
            # XPath matches: top container → text-body-medium div
            element = self.driver.find_element(By.XPATH,"//h1/ancestor::div[1]/following-sibling::div[contains(@class,'text-body-medium')]")
            headline = element.text.strip()
            return headline if headline else "Headline not found"

        except Exception as e:
            logger.warning(f"Error extracting headline: {str(e)}")
            return "Headline not found"
            
        except Exception as e:
            logger.warning(f"Error extracting headline: {str(e)}")
            return "Headline not found"
    
    def _extract_about(self):
        """Extract About section"""
        try:
            # Find the About header
            about_header = self.driver.find_element(By.XPATH, "//h2[.//span[text()='About']]")

            # Try to click Show more using XPath (more reliable)
            try:
                show_more = self.driver.find_element(By.XPATH, "//div[contains(@class, 'display-flex ph5 pv3')]//span[contains(@class, 'inline-show-more-text__link-container-collapsed')]//button")
                self.driver.execute_script("arguments[0].click();", show_more)
                time.sleep(1)
            except NoSuchElementException:
                pass

            # Try more general XPath selectors
            selectors = [
                "//div[contains(@class, 'display-flex ph5 pv3')]//span[@aria-hidden='true']",
                "//section[contains(@class, 'pv-about-section')]//span",
                "//div[contains(@class, 'pv-shared-text')]//span",
                "//div[contains(@id, 'about')]//span"
            ]

            for selector in selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    text = element.text.strip()
                    if text:
                        return text
                except NoSuchElementException:
                    continue

            return "About section not found"

        except Exception as e:
            return f"Error: {e}"

    
    def _extract_experience(self):
        """Extract work experience"""
        try:
            experience_list = []

            #Find the Experience header
            experience_header = self.driver.find_element(By.XPATH, "//h2[.//span[text()='Experience']]")

            #Find its container div
            experience_container = experience_header.find_element(By.XPATH, "./ancestor::div[4]")

            #Find the next sibling that holds the list
            experience_section = experience_container.find_element(By.XPATH, "./following-sibling::div")

            #Find all <li> experience items
            experience_items = experience_section.find_elements(By.XPATH, ".//li[contains(@class, 'artdeco-list__item')]")

            for item in experience_items[:5]:
                try:
                    # Title with fallback
                    try:
                        title_element = item.find_element(
                            By.XPATH, ".//div[contains(@class, 't-bold')]//span[@aria-hidden='true']"
                        )
                    except NoSuchElementException:
                        title_element = item.find_element(
                            By.XPATH, ".//span[@aria-hidden='true']"
                        )

                    # Company with fallback
                    try:
                        company_element = item.find_element(
                            By.XPATH, ".//span[contains(@class,'t-normal')]//span[@aria-hidden='true']"
                        )
                    except NoSuchElementException:
                        company_element = item.find_element(
                            By.XPATH, ".//span[@aria-hidden='true']"
                        )

                    title = title_element.text.strip()
                    company = company_element.text.strip()

                    if title and company:
                        experience_list.append({
                            'title': title,
                            'company': company
                        })

                except NoSuchElementException:
                    continue

            return experience_list if experience_list else ["Experience not found"]

        except Exception as e:
            logger.warning(f"Error extracting experience: {str(e)}")
            return ["Experience not found"]

    
    def _extract_skills(self):
        """Extract skills from LinkedIn profile"""
        try:
            skills_list = []

            #Find the Skills header
            skills_header = self.driver.find_element(By.XPATH, "//h2[.//span[text()='Skills']]")

            #Get its container div
            skills_container = skills_header.find_element(By.XPATH, "./ancestor::div[4]")

            #Get the following sibling that holds the skills list
            skills_section = skills_container.find_element(By.XPATH, "./following-sibling::div")

            #Click "Show all skills" if visible
            try:
                #Find the link with robust XPath
                show_all_link = skills_section.find_element(By.XPATH,".//div[contains(@class,'pv-action')]//a[.//span[contains(normalize-space(.), 'Show all') and contains(normalize-space(.), 'skills')]]")

                href = show_all_link.get_attribute("href")
                print("Show all link href:", href)

                #Scroll & click via JS
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", show_all_link)
                time.sleep(0.5)

                try:
                    self.driver.execute_script("arguments[0].click();", show_all_link)
                except ElementClickInterceptedException:
                    show_all_link.send_keys(Keys.RETURN)

                time.sleep(2)

                #Fallback: force navigate if click did not fire a redirect
                if href and href not in self.driver.current_url:
                    self.driver.get(href)
                    time.sleep(2)


            except NoSuchElementException:
                logger.warning("No Show All link found.")

            #Now find all <li> skill items in the expanded list
            skill_items = self.driver.find_elements(By.XPATH, "//li[contains(@class,'artdeco-list__item')]")

            for item in skill_items[:10]:  # Limit to first 10
                try:
                    # Use aria-hidden="true" to get only visible text
                    skill_element = item.find_element(By.XPATH, ".//div[contains(@class, 't-bold')]//span[@aria-hidden='true']")
                    skill = skill_element.text.strip()
                    if skill and len(skill) > 1:
                        skills_list.append(skill)
                except NoSuchElementException:
                    continue  # Skip if no clean span found

            return skills_list if skills_list else ["Skills not found"]

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
        # if not scraper.login_to_linkedin(profile_url):
        #     return None
        
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