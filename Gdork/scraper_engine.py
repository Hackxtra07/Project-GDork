import re
import time
import random
import threading
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

class DeepScraper:
    """Extracts PII and Metadata from a given URL."""
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }
        
        # Regex Patterns for PII
        self.patterns = {
            'emails': r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',
            'phones': r'\(?\b[0-9]{3}\)?[-. ]?[0-9]{3}[-. ]?[0-9]{4}\b',
            'socials': r'(https?://(www\.)?(linkedin\.com|twitter\.com|facebook\.com|instagram\.com|github\.com)/[A-Za-z0-9_-]+)',
            'crypto_btc': r'\b([13][a-km-zA-HJ-NP-Z1-9]{25,34}|bc1[a-zA-HJ-NP-Z0-9]{39,59})\b',
            'ips': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        }

    def scrape_url(self, url):
        """Visits a URL and extracts all matching PII."""
        data = {
            'emails': set(),
            'phones': set(),
            'socials': set(),
            'crypto': set(),
            'ips': set()
        }
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                text = response.text
                
                data['emails'].update(re.findall(self.patterns['emails'], text))
                data['phones'].update(re.findall(self.patterns['phones'], text))
                
                social_matches = re.findall(self.patterns['socials'], text)
                if social_matches:
                    data['socials'].update([match[0] for match in social_matches])
                    
                data['crypto'].update(re.findall(self.patterns['crypto_btc'], text))
                data['ips'].update(re.findall(self.patterns['ips'], text))
                
        except Exception as e:
            pass # Silently fail on unreachable domains during bulk scrape
            
        return data

class EntityProfiler:
    """Orchestrates Dork generation, Google searching, and Deep Scraping to build a Dossier."""
    def __init__(self, callback=None):
        self.callback = callback
        self.scraper = DeepScraper()
        self.running = False
        
    def generate_entity_dorks(self, name, username=None, company=None, location=None, nicknames=None):
        dorks = []
        name_quote = f'"{name}"'
        
        # Social & Docs
        dorks.append(f'{name_quote} site:linkedin.com/in/')
        dorks.append(f'{name_quote} filetype:pdf OR filetype:docx')
        
        # Leaks
        dorks.append(f'{name_quote} site:pastebin.com OR site:controlc.com')
        
        if username:
            dorks.append(f'"{username}" site:twitter.com OR site:github.com')
            dorks.append(f'inurl:{username} OR intext:"{username}"')
            
        if company:
            dorks.append(f'{name_quote} "{company}" email OR contact')
            
        if location:
            dorks.append(f'{name_quote} "{location}"')
            
        if nicknames:
            for nick in [n.strip() for n in nicknames.split(',') if n.strip()]:
                dorks.append(f'"{nick}"')
            
        return dorks

    def run_profiler(self, name, username, company, location=None, nicknames=None, search_engine="Google+DDG", search_depth=10, extract_types=None):
        self.running = True
        threading.Thread(
            target=self._profiler_worker,
            args=(name, username, company, location, nicknames, search_engine, search_depth, extract_types),
            daemon=True
        ).start()

    def _get_google_links(self, dork, depth=10):
        """Attempt to extract actual URLs from Google search results."""
        links = set()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }
        url = f"https://www.google.com/search?q={requests.utils.quote(dork)}&num={depth}"
        try:
            time.sleep(random.uniform(2, 4)) # Throttle
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Try finding standard result links
                for a_tag in soup.find_all('a', href=True):
                    href = a_tag['href']
                    if href.startswith('http') and not 'google.com' in href:
                        links.add(href)
                    elif href.startswith('/url?q='):
                        # Extract from redirect
                        parsed_url = parse_qs(urlparse(href).query).get('q')
                        if parsed_url and parsed_url[0].startswith('http'):
                            links.add(parsed_url[0])
        except Exception:
            pass
        return list(links)

    def _get_ddg_links(self, dork, depth=10):
        """Extract URLs from DuckDuckGo HTML search (no JS required)."""
        links = set()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
        }
        url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(dork)}"
        try:
            time.sleep(random.uniform(1.5, 3)) # Throttle
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                for a_tag in soup.find_all('a', class_='result__url', href=True):
                    href = a_tag['href']
                    if 'uddg=' in href:
                        # Extract redirect url parameter
                        parsed = parse_qs(urlparse(href).query).get('uddg')
                        if parsed and parsed[0].startswith('http'):
                            links.add(parsed[0])
                    elif href.startswith('http'):
                        links.add(href)
        except Exception:
            pass
        return list(links)[:depth]

    def _profiler_worker(self, name, username, company, location, nicknames, search_engine, search_depth, extract_types):
        if self.callback: self.callback(f"Starting Dossier generation for: {name}")
        if not extract_types:
            extract_types = ['emails', 'phones', 'socials', 'crypto', 'ips']
        
        dorks = self.generate_entity_dorks(name, username, company, location, nicknames)
        all_links = set()
        
        # Phase 1: Search and Extract URLs
        if self.callback: self.callback(f"Phase 1: Querying engines (Target: {search_engine}) for {len(dorks)} Dorks...")
        for dork in dorks:
            if not self.running: return
            google_links = []
            ddg_links = []
            
            if search_engine in ("Google Only", "Google+DDG"):
                if self.callback: self.callback(f"  -> [Google] Querying: {dork}")
                google_links = self._get_google_links(dork, search_depth)
                all_links.update(google_links)
                
            if search_engine in ("DDG Only", "Google+DDG") or (search_engine == "Google+DDG" and not google_links):
                # Fallback to DDG if Google returned 0 links (Likely Captcha blocked)
                engine_label = "DDG Fallback" if (search_engine == "Google+DDG" and not google_links) else "DuckDuckGo"
                if self.callback: self.callback(f"  -> [{engine_label}] Querying: {dork}")
                ddg_links = self._get_ddg_links(dork, search_depth)
                all_links.update(ddg_links)
            
        if not all_links:
            if self.callback: self.callback("No URLs found or both search engines blocked the requests. Try again later.")
            self.running = False
            return
            
        # Phase 2: Deep Scrape URLs
        if self.callback: self.callback(f"\nPhase 2: Deep Scraping {len(all_links)} discovered URLs for PII...")
        
        aggregated_data = {
            'emails': set(),
            'phones': set(),
            'socials': set(),
            'crypto': set(),
            'ips': set()
        }
        
        for i, link in enumerate(all_links, 1):
            if not self.running: return
            if self.callback: self.callback(f"  -> [{i}/{len(all_links)}] Scraping: {link[:50]}...")
            
            site_data = self.scraper.scrape_url(link)
            
            for key in aggregated_data:
                if key in extract_types:
                    aggregated_data[key].update(site_data[key])
                
        # Final Dossier Report
        if self.callback:
            self.callback("\n" + "="*40)
            self.callback(f"🎯 ENTITY DOSSIER: {name.upper()}")
            self.callback("="*40)
            
            if 'emails' in extract_types:
                self.callback("\n📧 EMAILS FOUND:")
                for e in list(aggregated_data['emails'])[:15]: self.callback(f"  - {e}")
                if not aggregated_data['emails']: self.callback("  None found.")
                
            if 'phones' in extract_types:
                self.callback("\n📱 PHONES FOUND:")
                for p in list(aggregated_data['phones'])[:15]: self.callback(f"  - {p}")
                if not aggregated_data['phones']: self.callback("  None found.")
                
            if 'socials' in extract_types:
                self.callback("\n🔗 SOCIAL PROFILES:")
                for s in list(aggregated_data['socials'])[:15]: self.callback(f"  - {s}")
                if not aggregated_data['socials']: self.callback("  None found.")
                
            if 'ips' in extract_types:
                self.callback("\n🌐 RELATED IPs:")
                for ip in list(aggregated_data['ips'])[:15]: self.callback(f"  - {ip}")
                if not aggregated_data['ips']: self.callback("  None found.")
                
            if 'crypto' in extract_types:
                self.callback("\n💰 CRYPTO WALLETS (BTC):")
                for b in list(aggregated_data['crypto'])[:15]: self.callback(f"  - {b}")
                if not aggregated_data['crypto']: self.callback("  None found.")
                
            self.callback("\n" + "="*40)
            self.callback("Dossier Generation Complete.")
            
        self.running = False
        
    def stop(self):
        self.running = False
