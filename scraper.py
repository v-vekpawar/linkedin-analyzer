import logging
from dotenv import load_dotenv
from linkedin_login import LinkedInLogin

logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - %(levelname)s - %(message)s'
    )
logger = logging.getLogger(__name__)
load_dotenv()

class LinkedInScraper:

    def __init__(self, headless):
        self.auth = LinkedInLogin(headless)

    @property
    def page(self):
        return self.auth.page

    def random_delay(self, min_sec=1, max_sec=3):
        self.auth.random_delay(min_sec, max_sec)

    def scrape_profile(self, profile_url, max_login_retries=3):
        """Scrape LinkedIn profile data with account rotation only when needed"""
        self.profile_url = profile_url
        
        if not self.auth.ensure_logged_in(profile_url, max_login_retries):
            return None
            
        logger.info("Starting profile scraping...")
        # Scroll to load all sections
        try:
            logger.info("Scrolling page to load all sections...")
            for i in range(3):
                self.page.evaluate("window.scrollBy(0, 800)")
                self.random_delay(0.5, 1)
            self.page.evaluate("window.scrollTo(0, 0)")
            self.random_delay(1, 2)
        except Exception as scroll_error:
            logger.warning(f"Error scrolling page: {scroll_error}")

        try:
            profile_data = {
                'name': self._extract_name(),
                'headline': self._extract_headline(),
                'about': self._extract_about(),
                'education': self._extract_education(),
                'certifications': self._extract_certificate(),
                'experience': self._extract_experience(),
                'skills': self._extract_skills(),
                'url': profile_url
            }
            logger.info("Profile scraping completed successfully")
            return profile_data

        except Exception as e:
            logger.error(f"Error scraping profile: {str(e)}")
            return None
    
    def _extract_name(self):
        try:
            self.page.wait_for_selector("//h1", timeout= 10 * 1000)
            element = self.page.query_selector("//h1")
            return element.inner_text().strip() if element else "Name not found"
        except Exception as e:
            logger.error(f"Name extraction error: {str(e)}")
            return "Name not found"
        
    def _extract_headline(self):
        try:
            element = self.page.query_selector("//h1/ancestor::div[1]/following-sibling::div[contains(@class,'text-body-medium')]")
            return element.inner_text().strip() if element else "Headline not found"
        except Exception as e:
            logger.error(f"Headline extraction error: {str(e)}")
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
                            logger.info("About section extracted successfully")
                            return text
            return "About section not found"
        except Exception as e:
            logger.error(f"About section extraction error: {str(e)}")

    def _extract_experience(self):
        try:
            experience_list = []

            try:
                logger.info("Scrolling to Experience section...")
                self.page.evaluate("window.scrollBy(0, 500)")
                self.random_delay(1, 2)
            except:
                pass
            
            try:
                experience_header = self.page.wait_for_selector(
                    "//h2[.//span[text()='Experience']]", 
                    timeout=5000
                )
                if not experience_header:
                    logger.info("No Experience section found on profile")
                    return []
            except Exception as timeout_error:
                logger.warning(f"Experience section not found")
                return []
        
            logger.info("Experience section found, navigating to details page...")
            self.page.goto(f"{self.profile_url}/details/experience/", timeout=30000)
            self.random_delay(2, 3)
            
            try:
                self.page.wait_for_selector("//li[contains(@class, 'artdeco-list__item')]", timeout=10000)
                experience_items = self.page.locator("xpath=//li[contains(@class, 'artdeco-list__item')]").all()
                
                for item in experience_items[:5]:
                    try:
                        title_element = item.locator("xpath=.//div[contains(@class, 't-bold')]//span[@aria-hidden='true']").first
                        company_element = item.locator("xpath=.//span[contains(@class,'t-normal')]//span[@aria-hidden='true']").first
                        duration_element = item.locator("xpath=.//span[contains(@class,'t-normal')]//span[contains(@class,'pvs-entity') and @aria-hidden='true']").first

                        title = title_element.inner_text().strip() if title_element else ""
                        company = company_element.inner_text().strip().split('·')[0].strip() if company_element else ""
                        duration = duration_element.inner_text().strip().split('·')[-1].strip() if duration_element else ""

                        if title and company:
                            experience_list.append({
                                'title': title, 
                                'company': company,
                                'duration': duration,
                            })
                    except:
                        continue
                
                logger.info(f"Extracted {len(experience_list)} experience entries")
            except Exception as extract_error:
                logger.warning(f"Could not extract experience items")
            
            self.page.go_back()
            self.random_delay(1, 2)
            return experience_list
            
        except Exception as e:
            logger.error(f"Experience extraction error: {str(e)}")
            try:
                self.page.go_back()
            except:
                pass
            return []

    def _extract_skills(self):
        try:
            skills_list = []
            
            try:
                logger.info("Scrolling to Skills section...")
                self.page.evaluate("window.scrollBy(0, 1000)")
                self.random_delay(1, 2)
            except:
                pass
            
            try:
                skills_header = self.page.wait_for_selector(
                    "//h2[.//span[text()='Skills']]",
                    timeout=5000
                )
                if not skills_header:
                    logger.info("No Skills section found on profile")
                    return []
            except Exception as timeout_error:
                logger.warning(f"Skills section not found")
                return []
            
            logger.info("Skills section found, navigating to details page...")
            self.page.goto(f"{self.profile_url}/details/skills", timeout=30000)
            self.random_delay(2, 3)
            
            try:
                self.page.wait_for_selector("//li[contains(@class,'artdeco-list__item')]", timeout=10000)
                skill_items = self.page.locator("xpath=//li[contains(@class,'artdeco-list__item')]").all()
                
                for item in skill_items[:15]:
                    try:
                        skill_element = item.locator("xpath=.//div[contains(@class, 't-bold')]//span[@aria-hidden='true']").first
                        if skill_element:
                            skill = skill_element.inner_text().strip()
                            if skill:
                                skills_list.append(skill)
                    except:
                        continue
                
                skills_list = list(dict.fromkeys(skills_list))
                logger.info(f"Extracted {len(skills_list)} skills")
            except Exception as extract_error:
                logger.warning(f"Could not extract skill items")
            
            self.page.go_back()
            self.random_delay(1, 2)
            return skills_list
            
        except Exception as e:
            logger.error(f"Skills extraction error: {str(e)}")
            try:
                self.page.go_back()
            except:
                pass
            return []
    
    def _extract_education(self):
        try:
            education_list = []
            education_header = self.page.locator("//h2[.//span[text()='Education']]")
            if education_header.count() == 0:
                return []

            education_container = education_header.locator("xpath=./ancestor::div[4]").first
            education_section = education_container.locator("xpath=./following-sibling::div").first
            
            main_page_education = education_section.locator("xpath=.//li[contains(@class,'artdeco-list__item')]").all()
            
            for item in main_page_education[:5]:
                try:
                    # Extract school name
                    school_element = item.locator("xpath=.//div[contains(@class, 't-bold')]//span[@aria-hidden='true']").first
                    school = school_element.inner_text().strip() if school_element else ""
                    
                    # Extract degree and field
                    degree_element = school_element.locator("xpath=./ancestor::div[4]/following-sibling::span//span[@aria-hidden='true']").first
                    degree_text = degree_element.inner_text().strip() if degree_element else ""
                    
                    # Extract year/duration
                    year_element = degree_element.locator("xpath=./ancestor::span/following-sibling::span//span[@aria-hidden='true']").first
                    year = year_element.inner_text().strip() if year_element else ""
                    
                    # ALTERNATIVE: Simple try-except approach
                    degree = ""
                    field = ""
                    
                    try:
                        if degree_text:
                            # Try to split by "-"
                            parts = degree_text.split("-", 1)  # maxsplit=1
                            degree = parts[0].strip()
                            
                            if len(parts) > 1:
                                # Try to split by ","
                                field_parts = parts[1].split(",", 1)  # maxsplit=1
                                field = field_parts[1].strip() if len(field_parts) > 1 else field_parts[0].strip()
                    except:
                        # If parsing fails, just use the whole text as degree
                        degree = degree_text

                    if school:
                        education_entry = {
                            'school': school,
                            'degree': degree or 'Degree',
                            'field': field or 'Field of Study',
                            'year': year or 'Year'
                        }
                        education_list.append(education_entry)
                        
                except Exception as item_error:
                    logger.warning(f"Error extracting education item: {item_error}")
                    continue
            
            if education_list:
                logger.info(f"✅ Extracted {len(education_list)} education entries")
            
            return education_list
            
        except Exception as e:
            logger.error(f"Education extraction error: {str(e)}")
            return []

    def _extract_certificate(self):
        try:
            certificate_list = []
            certification_header = self.page.locator("//h2[.//span[text()='Licenses & certifications']]")
            if certification_header.count() == 0:
                return []
            
            self.page.goto(f"{self.profile_url}/details/certifications")
            try:
                self.page.wait_for_selector("//section[contains(@class,'artdeco-card')]//li[contains(@class,'artdeco-list__item')]", timeout=10000)
                certificate_items = self.page.locator("xpath=//section[contains(@class,'artdeco-card')]//li[contains(@class,'artdeco-list__item')]").all()
                
                for item in certificate_items[:5]:
                    try:
                        # Extract certificate name
                        certificate_element = item.locator("xpath=.//div[contains(@class, 't-bold')]//span[@aria-hidden='true']").first
                        certificate = certificate_element.inner_text().strip() if certificate_element else ""
                        
                        # Extract certificate link
                        link_element = item.locator("xpath=.//a").nth(1)
                        certificate_link = link_element.get_attribute("href") if link_element else ""

                        # Extract certificate issuer
                        issuer_element = certificate_element.locator("xpath=ancestor::div[4]/following-sibling::span//span[@aria-hidden='true']").first
                        issuer = issuer_element.inner_text().strip() if issuer_element else ""

                        # Extract issued date
                        date_element = issuer_element.locator("xpath=./ancestor::span/following-sibling::span//span[@aria-hidden='true']").first
                        date = date_element.inner_text().strip() if date_element else ""

                        if certificate:
                            certificate_entry = {
                                'certificate': certificate,
                                'link': certificate_link or 'Link to Certificate',
                                'issuer': issuer or 'Issued By __',
                                'date': date or 'Issued Date'
                            }
                            certificate_list.append(certificate_entry)
                    except Exception as item_error:
                        logger.warning(f"Error extracting certificate item: {item_error}")
            
            except Exception as wait_error:
                    logger.warning(f"Certificates content didn't load: {wait_error}")

            logger.info("Extracted Certificates section successfully") if certificate_list else logger.warning("Empty certificates section found")
            self.page.go_back()
            return certificate_list

        except Exception as e:
            logger.error(f"Certificate extraction error: {str(e)}")
            return []
    
    def close(self):
        self.auth.close()

def scrape_linkedin_profile(profile_url, headless=True):
    """Convenience function to scrape a LinkedIn profile"""
    scraper = LinkedInScraper(headless=headless)
    try:
        profile_data = scraper.scrape_profile(profile_url)
        return profile_data
    except Exception as e:
        logger.error(f"Scrape error: {str(e)}")
        return None
    finally:
        scraper.close()