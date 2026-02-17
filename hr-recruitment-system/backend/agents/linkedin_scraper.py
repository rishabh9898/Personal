"""
LinkedIn Scraper Agent
Searches for candidates on LinkedIn using web scraping
"""

import asyncio
from typing import Dict, Any, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
from .base_agent import BaseAgent


class LinkedInScraperAgent(BaseAgent):
    """
    Agent for scraping candidate profiles from LinkedIn
    """

    def __init__(self, agent_id: str = "linkedin_scraper", config: Dict[str, Any] = None):
        super().__init__(agent_id, config)
        self.headless = config.get('headless', True)
        self.scrape_delay = config.get('scrape_delay', 2)
        self.max_candidates = config.get('max_candidates', 50)
        self.driver = None

    def setup_driver(self):
        """
        Setup Selenium WebDriver with Chrome
        """
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument("--headless")

        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

        # Prevent detection
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def close_driver(self):
        """
        Close the WebDriver
        """
        if self.driver:
            self.driver.quit()
            self.driver = None

    async def login_to_linkedin(self, email: str, password: str) -> bool:
        """
        Login to LinkedIn (optional, for better access)

        Args:
            email: LinkedIn email
            password: LinkedIn password

        Returns:
            True if login successful, False otherwise
        """
        try:
            self.driver.get("https://www.linkedin.com/login")
            await asyncio.sleep(2)

            # Enter credentials
            email_field = self.driver.find_element(By.ID, "username")
            email_field.send_keys(email)

            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(password)

            # Click login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()

            await asyncio.sleep(3)

            # Check if login was successful
            if "feed" in self.driver.current_url or "mynetwork" in self.driver.current_url:
                self.log("LinkedIn login successful")
                return True
            else:
                self.log("LinkedIn login may have failed - check credentials", "warning")
                return False

        except Exception as e:
            self.add_error(f"LinkedIn login failed: {e}", e)
            return False

    async def search_candidates(self, job_title: str, location: str = "", keywords: List[str] = None) -> List[Dict[str, Any]]:
        """
        Search for candidates on LinkedIn

        Args:
            job_title: Job title to search for
            location: Location filter
            keywords: Additional keywords to search

        Returns:
            List of candidate profiles
        """
        candidates = []

        # Build search query
        search_query = job_title
        if keywords:
            search_query += " " + " ".join(keywords)

        # Construct LinkedIn search URL (public search, no login required)
        base_url = "https://www.linkedin.com/search/results/people/"
        params = f"?keywords={search_query.replace(' ', '%20')}"

        if location:
            params += f"&location={location.replace(' ', '%20')}"

        search_url = base_url + params

        self.log(f"Searching LinkedIn: {search_url}")

        try:
            self.driver.get(search_url)
            await asyncio.sleep(self.scrape_delay)

            # Scroll to load more results
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(1)

            # Extract candidate information from search results
            result_items = self.driver.find_elements(By.CSS_SELECTOR, ".reusable-search__result-container")

            for idx, item in enumerate(result_items[:self.max_candidates]):
                try:
                    candidate = self.extract_candidate_info(item)
                    if candidate:
                        candidates.append(candidate)
                        self.log(f"Found candidate: {candidate.get('name', 'Unknown')}")

                except Exception as e:
                    self.log(f"Error extracting candidate {idx}: {e}", "warning")
                    continue

                await asyncio.sleep(0.5)  # Small delay between extractions

        except Exception as e:
            self.add_error(f"LinkedIn search failed: {e}", e)
            raise

        return candidates

    def extract_candidate_info(self, element) -> Dict[str, Any]:
        """
        Extract candidate information from search result element

        Args:
            element: Selenium web element

        Returns:
            Candidate information dictionary
        """
        candidate = {}

        try:
            # Name
            name_elem = element.find_element(By.CSS_SELECTOR, ".entity-result__title-text a span[aria-hidden='true']")
            candidate['name'] = name_elem.text.strip()

            # Current title/headline
            try:
                headline_elem = element.find_element(By.CSS_SELECTOR, ".entity-result__primary-subtitle")
                candidate['headline'] = headline_elem.text.strip()
            except NoSuchElementException:
                candidate['headline'] = None

            # Location
            try:
                location_elem = element.find_element(By.CSS_SELECTOR, ".entity-result__secondary-subtitle")
                candidate['location'] = location_elem.text.strip()
            except NoSuchElementException:
                candidate['location'] = None

            # Profile URL
            try:
                profile_link = element.find_element(By.CSS_SELECTOR, ".entity-result__title-text a")
                candidate['profile_url'] = profile_link.get_attribute('href')
            except NoSuchElementException:
                candidate['profile_url'] = None

            # Summary text (if available)
            try:
                summary_elem = element.find_element(By.CSS_SELECTOR, ".entity-result__summary")
                candidate['summary'] = summary_elem.text.strip()
            except NoSuchElementException:
                candidate['summary'] = None

            candidate['source'] = 'LinkedIn'

        except Exception as e:
            self.log(f"Error parsing candidate element: {e}", "warning")
            return None

        return candidate

    async def execute(self, job_title: str, location: str = "", keywords: List[str] = None,
                     linkedin_email: str = None, linkedin_password: str = None, **kwargs) -> Dict[str, Any]:
        """
        Execute LinkedIn candidate search

        Args:
            job_title: Job title to search for
            location: Location filter
            keywords: Additional keywords
            linkedin_email: LinkedIn email for login (optional)
            linkedin_password: LinkedIn password for login (optional)

        Returns:
            Search results with candidate list
        """
        self.log(f"Starting LinkedIn search for: {job_title}")

        try:
            # Setup browser
            self.setup_driver()

            # Login if credentials provided
            if linkedin_email and linkedin_password:
                await self.login_to_linkedin(linkedin_email, linkedin_password)

            # Search for candidates
            candidates = await self.search_candidates(job_title, location, keywords)

            result = {
                'job_title': job_title,
                'location': location,
                'keywords': keywords,
                'candidates_found': len(candidates),
                'candidates': candidates
            }

            self.add_result(result)
            self.log(f"LinkedIn search completed: {len(candidates)} candidates found")

            return result

        finally:
            # Always close the driver
            self.close_driver()
