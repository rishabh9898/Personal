"""
Indeed Scraper Agent
Searches for candidates/job postings on Indeed using web scraping
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


class IndeedScraperAgent(BaseAgent):
    """
    Agent for scraping job postings and candidate information from Indeed
    """

    def __init__(self, agent_id: str = "indeed_scraper", config: Dict[str, Any] = None):
        super().__init__(agent_id, config)
        self.headless = config.get('headless', True)
        self.scrape_delay = config.get('scrape_delay', 2)
        self.max_results = config.get('max_candidates', 50)
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

    async def search_resumes(self, job_title: str, location: str = "") -> List[Dict[str, Any]]:
        """
        Search for resumes on Indeed (requires Indeed Resume access)

        Args:
            job_title: Job title/skills to search for
            location: Location filter

        Returns:
            List of candidate profiles from resumes
        """
        candidates = []

        # Note: Indeed Resume search requires employer account
        # This is a simplified version that searches job postings to understand market
        self.log("Note: Indeed Resume search requires employer account. Searching job postings instead.")

        # Build search URL for job postings (to understand what candidates are looking for)
        base_url = "https://www.indeed.com/jobs"
        params = f"?q={job_title.replace(' ', '+')}"

        if location:
            params += f"&l={location.replace(' ', '+')}"

        search_url = base_url + params

        self.log(f"Searching Indeed: {search_url}")

        try:
            self.driver.get(search_url)
            await asyncio.sleep(self.scrape_delay)

            # Extract job postings (which can help identify potential candidates)
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, ".job_seen_beacon, .jobsearch-ResultsList > li")

            for idx, card in enumerate(job_cards[:self.max_results]):
                try:
                    job_info = self.extract_job_info(card)
                    if job_info:
                        candidates.append(job_info)
                        self.log(f"Found job posting: {job_info.get('title', 'Unknown')}")

                except Exception as e:
                    self.log(f"Error extracting job {idx}: {e}", "warning")
                    continue

                await asyncio.sleep(0.5)

        except Exception as e:
            self.add_error(f"Indeed search failed: {e}", e)
            raise

        return candidates

    def extract_job_info(self, element) -> Dict[str, Any]:
        """
        Extract job information from job card element

        Args:
            element: Selenium web element

        Returns:
            Job information dictionary
        """
        job_info = {}

        try:
            # Job title
            try:
                title_elem = element.find_element(By.CSS_SELECTOR, "h2.jobTitle span[title], .jobTitle a")
                job_info['title'] = title_elem.text.strip() or title_elem.get_attribute('title')
            except NoSuchElementException:
                return None

            # Company name
            try:
                company_elem = element.find_element(By.CSS_SELECTOR, "[data-testid='company-name'], .companyName")
                job_info['company'] = company_elem.text.strip()
            except NoSuchElementException:
                job_info['company'] = None

            # Location
            try:
                location_elem = element.find_element(By.CSS_SELECTOR, "[data-testid='text-location'], .companyLocation")
                job_info['location'] = location_elem.text.strip()
            except NoSuchElementException:
                job_info['location'] = None

            # Salary (if available)
            try:
                salary_elem = element.find_element(By.CSS_SELECTOR, "[data-testid='attribute_snippet_testid'], .salary-snippet")
                job_info['salary'] = salary_elem.text.strip()
            except NoSuchElementException:
                job_info['salary'] = None

            # Job snippet/description
            try:
                snippet_elem = element.find_element(By.CSS_SELECTOR, ".job-snippet, td.resultContent > div > div")
                job_info['snippet'] = snippet_elem.text.strip()
            except NoSuchElementException:
                job_info['snippet'] = None

            # Job URL
            try:
                link_elem = element.find_element(By.CSS_SELECTOR, "a[data-jk], h2.jobTitle a")
                job_url = link_elem.get_attribute('href')
                if job_url and not job_url.startswith('http'):
                    job_url = 'https://www.indeed.com' + job_url
                job_info['url'] = job_url
            except NoSuchElementException:
                job_info['url'] = None

            # Date posted (if available)
            try:
                date_elem = element.find_element(By.CSS_SELECTOR, ".date, [data-testid='myJobsStateDate']")
                job_info['date_posted'] = date_elem.text.strip()
            except NoSuchElementException:
                job_info['date_posted'] = None

            job_info['source'] = 'Indeed'
            job_info['type'] = 'job_posting'

        except Exception as e:
            self.log(f"Error parsing job element: {e}", "warning")
            return None

        return job_info

    async def get_job_details(self, job_url: str) -> Dict[str, Any]:
        """
        Get detailed information from a job posting

        Args:
            job_url: URL of the job posting

        Returns:
            Detailed job information
        """
        try:
            self.driver.get(job_url)
            await asyncio.sleep(2)

            details = {}

            # Full job description
            try:
                desc_elem = self.driver.find_element(By.ID, "jobDescriptionText")
                details['full_description'] = desc_elem.text.strip()
            except NoSuchElementException:
                details['full_description'] = None

            # Requirements (if separately listed)
            try:
                req_elems = self.driver.find_elements(By.CSS_SELECTOR, ".jobsearch-JobDescriptionSection-sectionItem")
                details['requirements'] = [elem.text.strip() for elem in req_elems]
            except NoSuchElementException:
                details['requirements'] = []

            return details

        except Exception as e:
            self.log(f"Error getting job details: {e}", "warning")
            return {}

    async def execute(self, job_title: str, location: str = "", get_details: bool = False, **kwargs) -> Dict[str, Any]:
        """
        Execute Indeed search

        Args:
            job_title: Job title to search for
            location: Location filter
            get_details: Whether to fetch full job details (slower)

        Returns:
            Search results
        """
        self.log(f"Starting Indeed search for: {job_title}")

        try:
            # Setup browser
            self.setup_driver()

            # Search for jobs/resumes
            results = await self.search_resumes(job_title, location)

            # Optionally get full details for each job
            if get_details and results:
                self.log("Fetching detailed information for top results...")
                for result in results[:10]:  # Limit to top 10 to avoid too long execution
                    if result.get('url'):
                        details = await self.get_job_details(result['url'])
                        result.update(details)

            result = {
                'job_title': job_title,
                'location': location,
                'results_found': len(results),
                'results': results
            }

            self.add_result(result)
            self.log(f"Indeed search completed: {len(results)} results found")

            return result

        finally:
            # Always close the driver
            self.close_driver()
