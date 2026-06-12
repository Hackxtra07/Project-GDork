"""
Advanced Intelligence Modules for Project-GDork Phase 4
Includes: Nuclei, SOCMINT, GEOINT, TOR Routing, CAPTCHA Solver
"""

import re
import time
import random
import threading
import requests
import subprocess
import os
import json
from urllib.parse import quote_plus

# ─────────────────────────────────────────────
#  TOR ROUTING LAYER
# ─────────────────────────────────────────────
class TORRouter:
    """Routes all HTTP requests through TOR SOCKS5 proxy."""
    TOR_PROXY = {
        'http': 'socks5h://127.0.0.1:9050',
        'https': 'socks5h://127.0.0.1:9050'
    }
    _enabled = False

    @classmethod
    def enable(cls):
        cls._enabled = True

    @classmethod
    def disable(cls):
        cls._enabled = False

    @classmethod
    def is_enabled(cls):
        return cls._enabled

    @classmethod
    def get(cls, url, **kwargs):
        if cls._enabled:
            kwargs['proxies'] = cls.TOR_PROXY
        return requests.get(url, timeout=15, **kwargs)

    @classmethod
    def check_tor(cls):
        """Check if TOR is running and reachable."""
        try:
            r = requests.get('https://check.torproject.org/api/ip', 
                           proxies=cls.TOR_PROXY, timeout=10)
            data = r.json()
            return data.get('IsTor', False), data.get('IP', 'Unknown')
        except Exception as e:
            return False, str(e)

    @classmethod
    def new_circuit(cls):
        """Request a new TOR circuit (identity) via control port."""
        try:
            import socket
            s = socket.create_connection(('127.0.0.1', 9051), timeout=5)
            s.send(b'AUTHENTICATE ""\r\nSIGNAL NEWNYM\r\nQUIT\r\n')
            s.close()
            time.sleep(2)
            return True
        except:
            return False


# ─────────────────────────────────────────────
#  CAPTCHA SOLVER
# ─────────────────────────────────────────────
class CaptchaSolver:
    """Auto CAPTCHA bypass: 2Captcha API + rotate/retry fallback."""

    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/16.5 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1',
    ]

    def __init__(self, two_captcha_key=None):
        self.two_captcha_key = two_captcha_key
        self._ua_index = 0

    def is_captcha(self, html_text):
        """Detect if the response is a CAPTCHA page."""
        captcha_markers = [
            'recaptcha', 'g-recaptcha', 'captcha', 
            'unusual traffic', 'Our systems have detected', 
            '/sorry/index'
        ]
        return any(marker.lower() in html_text.lower() for marker in captcha_markers)

    def rotate_ua(self):
        """Rotate to the next User-Agent."""
        self._ua_index = (self._ua_index + 1) % len(self.USER_AGENTS)
        return self.USER_AGENTS[self._ua_index]

    def get_with_bypass(self, url, max_retries=3, callback=None):
        """Attempt a GET request with automatic CAPTCHA bypass."""
        for attempt in range(max_retries):
            ua = self.rotate_ua()
            headers = {'User-Agent': ua}
            delay = random.uniform(3, 8) + (attempt * 2)
            time.sleep(delay)

            try:
                if TORRouter.is_enabled() and attempt > 0:
                    if callback: callback(f"  [TOR] Requesting new circuit (attempt {attempt+1})...")
                    TORRouter.new_circuit()

                resp = TORRouter.get(url, headers=headers)
                
                if not self.is_captcha(resp.text):
                    return resp
                
                if callback:
                    callback(f"  [CAPTCHA] Detected on attempt {attempt+1}. Rotating UA and retrying...")
                
                # Try 2Captcha if available
                if self.two_captcha_key and 'recaptcha' in resp.text.lower():
                    token = self._solve_recaptcha(url, resp.text)
                    if token and callback:
                        callback(f"  [CAPTCHA] 2Captcha solved! Token: {token[:20]}...")

            except requests.RequestException as e:
                if callback: callback(f"  [ERROR] Request failed: {e}")

        return None

    def _solve_recaptcha(self, url, html):
        """Submit reCAPTCHA to 2Captcha API."""
        try:
            # Extract sitekey
            match = re.search(r'data-sitekey="([^"]+)"', html)
            if not match:
                return None
            sitekey = match.group(1)

            # Submit to 2Captcha
            submit = requests.post('http://2captcha.com/in.php', data={
                'key': self.two_captcha_key,
                'method': 'userrecaptcha',
                'googlekey': sitekey,
                'pageurl': url,
                'json': 1
            }, timeout=10)
            captcha_id = submit.json().get('request')
            if not captcha_id:
                return None

            # Poll for solution
            for _ in range(20):
                time.sleep(5)
                res = requests.get(f'http://2captcha.com/res.php', params={
                    'key': self.two_captcha_key,
                    'action': 'get',
                    'id': captcha_id,
                    'json': 1
                }, timeout=10)
                data = res.json()
                if data.get('status') == 1:
                    return data.get('request')
        except:
            pass
        return None


# ─────────────────────────────────────────────
#  NUCLEI SCANNER
# ─────────────────────────────────────────────
class NucleiScanner:
    """Wrapper around the nuclei binary for vulnerability scanning."""

    TEMPLATE_CATEGORIES = [
        'cves', 'exposures', 'misconfigs', 'takeovers',
        'technologies', 'vulnerabilities', 'ssl', 'dns', 'network', 'file', 'default-logins'
    ]

    def __init__(self, callback=None):
        self.callback = callback
        self.running = False
        self.process = None

    def is_installed(self):
        """Check if nuclei binary is available."""
        try:
            result = subprocess.run(['nuclei', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def scan(self, target, templates=None, custom_template_path=None, severity='medium,high,critical',
             concurrency=None, rate_limit=None, headers=None, proxy=None, headless=False,
             scan_all_ips=False, silent=False):
        """Launch nuclei scan in background thread."""
        if not self.is_installed():
            if self.callback:
                self.callback("[ERROR] Nuclei is not installed or not in PATH.")
                self.callback("[INFO] Download from: https://github.com/projectdiscovery/nuclei/releases")
            return
        self.running = True
        threading.Thread(
            target=self._scan_worker, 
            args=(target, templates, custom_template_path, severity, concurrency, rate_limit, headers, proxy, headless, scan_all_ips, silent), 
            daemon=True
        ).start()

    def _scan_worker(self, target, templates, custom_template_path, severity, concurrency, rate_limit, headers, proxy, headless, scan_all_ips, silent):
        cmd = ['nuclei', '-u', target, '-severity', severity, '-nc']
        if silent:
            cmd += ['-silent']
            
        if templates:
            cmd += ['-t', ','.join(templates)]
        elif custom_template_path:
            cmd += ['-t', custom_template_path]
        else:
            cmd += ['-automatic-scan']
            
        if concurrency:
            cmd += ['-c', str(concurrency)]
        if rate_limit:
            cmd += ['-rl', str(rate_limit)]
        if headers:
            for h in headers:
                if h.strip() and ':' in h:
                    cmd += ['-H', h.strip()]
        if proxy:
            cmd += ['-proxy', proxy]
        if headless:
            cmd += ['-headless']
        if scan_all_ips:
            cmd += ['-scan-all-ips']

        if self.callback:
            self.callback(f"[NUCLEI] Starting scan on: {target}")
            self.callback(f"[NUCLEI] Command: {' '.join(cmd)}\n")

        try:
            self.process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1
            )
            for line in iter(self.process.stdout.readline, ''):
                if not self.running:
                    self.process.terminate()
                    break
                if self.callback:
                    self.callback(line.rstrip())
            self.process.wait()
        except Exception as e:
            if self.callback:
                self.callback(f"[ERROR] Nuclei scan failed: {e}")
        finally:
            self.running = False
            if self.callback:
                self.callback("\n[NUCLEI] Scan complete.")

    def stop(self):
        self.running = False
        if self.process:
            self.process.terminate()


# ─────────────────────────────────────────────
#  SOCMINT ENGINE
# ─────────────────────────────────────────────
class SOCMINTEngine:
    """Social Media Intelligence - aggregates intel from Reddit, GitHub, Pastebin, Twitter, LinkedIn, Instagram, Facebook."""

    def __init__(self, github_token=None, twitter_bearer=None, callback=None):
        self.github_token = github_token
        self.twitter_bearer = twitter_bearer
        self.callback = callback
        self.running = False
        self.captcha_solver = CaptchaSolver()

    def run(self, target, platforms=None, limit=10):
        """Run selected SOCMINT sources in parallel threads."""
        self.running = True
        if not platforms:
            platforms = ['reddit', 'github', 'pastebin']
            if self.twitter_bearer:
                platforms.append('twitter')
        
        threads = []
        if 'reddit' in platforms:
            threads.append(threading.Thread(target=self._search_reddit, args=(target, limit), daemon=True))
        if 'github' in platforms:
            threads.append(threading.Thread(target=self._search_github, args=(target, limit), daemon=True))
        if 'pastebin' in platforms:
            threads.append(threading.Thread(target=self._search_pastebin_dork, args=(target, limit), daemon=True))
        if 'twitter' in platforms and self.twitter_bearer:
            threads.append(threading.Thread(target=self._search_twitter, args=(target, limit), daemon=True))
        if 'linkedin' in platforms:
            threads.append(threading.Thread(target=self._search_linkedin_dork, args=(target, limit), daemon=True))
        if 'instagram' in platforms:
            threads.append(threading.Thread(target=self._search_instagram_dork, args=(target, limit), daemon=True))
        if 'facebook' in platforms:
            threads.append(threading.Thread(target=self._search_facebook_dork, args=(target, limit), daemon=True))

        for t in threads:
            t.start()

    def _log(self, msg):
        if self.callback:
            self.callback(msg)

    def _search_reddit(self, target, limit=10):
        self._log(f"\n[REDDIT] Searching for mentions of: {target}")
        try:
            url = f"https://www.reddit.com/search.json?q={quote_plus(target)}&sort=new&limit={limit}"
            headers = {'User-Agent': 'Mozilla/5.0 GDork/4.0'}
            resp = TORRouter.get(url, headers=headers)
            data = resp.json()
            posts = data.get('data', {}).get('children', [])
            if not posts:
                self._log(f"  [REDDIT] No mentions found.")
                return
            for post in posts[:limit]:
                p = post.get('data', {})
                self._log(f"  [r/{p.get('subreddit')}] {p.get('title')}")
                self._log(f"    -> https://reddit.com{p.get('permalink')}")
        except Exception as e:
            self._log(f"  [REDDIT] Error: {e}")

    def _search_github(self, target, limit=10):
        self._log(f"\n[GITHUB] Searching code for: {target}")
        headers = {'Accept': 'application/vnd.github+json'}
        if self.github_token:
            headers['Authorization'] = f'Bearer {self.github_token}'
        try:
            url = f"https://api.github.com/search/code?q={quote_plus(target)}&per_page={limit}"
            resp = TORRouter.get(url, headers=headers)
            data = resp.json()
            items = data.get('items', [])
            if not items:
                self._log(f"  [GITHUB] No code matches found.")
                return
            for item in items[:limit]:
                self._log(f"  [GITHUB] {item.get('repository', {}).get('full_name')} -> {item.get('html_url')}")
        except Exception as e:
            self._log(f"  [GITHUB] Error: {e}")

    def _search_pastebin_dork(self, target, limit=10):
        self._log(f"\n[PASTEBIN] Searching for: {target}")
        try:
            url = f"https://www.google.com/search?q=site:pastebin.com+\"{quote_plus(target)}\""
            resp = self.captcha_solver.get_with_bypass(url, callback=self.callback)
            if resp:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, 'html.parser')
                links = soup.select('a[href*="pastebin.com"]')
                if not links:
                     self._log(f"  [PASTEBIN] No results or Google Captcha blocked.")
                for a in links[:limit]:
                    self._log(f"  [PASTEBIN] {a.get('href')}")
            else:
                self._log(f"  [PASTEBIN] Could not bypass CAPTCHA.")
        except Exception as e:
            self._log(f"  [PASTEBIN] Error: {e}")

    def _search_twitter(self, target, limit=10):
        self._log(f"\n[TWITTER] Searching tweets for: {target}")
        try:
            headers = {'Authorization': f'Bearer {self.twitter_bearer}'}
            url = "https://api.twitter.com/2/tweets/search/recent"
            params = {'query': target, 'max_results': limit, 'tweet.fields': 'created_at,author_id'}
            resp = TORRouter.get(url, headers=headers, params=params)
            tweets = resp.json().get('data', [])
            if not tweets:
                self._log(f"  [TWITTER] No recent tweets found.")
                return
            for tweet in tweets[:limit]:
                self._log(f"  [TWITTER] {tweet.get('created_at')}: {tweet.get('text')[:100]}...")
        except Exception as e:
            self._log(f"  [TWITTER] Error: {e}")

    def _search_linkedin_dork(self, target, limit=10):
        self._log(f"\n[LINKEDIN] Searching for: {target}")
        try:
            url = f"https://www.google.com/search?q=site:linkedin.com/in/+\"{quote_plus(target)}\" OR site:linkedin.com/pub/+\"{quote_plus(target)}\""
            resp = self.captcha_solver.get_with_bypass(url, callback=self.callback)
            if resp:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, 'html.parser')
                links = [a.get('href') for a in soup.select('a[href*="linkedin.com"]') if 'google.com' not in a.get('href', '')]
                if not links:
                    self._log(f"  [LINKEDIN] No results or Google Captcha blocked.")
                for link in list(set(links))[:limit]:
                    self._log(f"  [LINKEDIN] {link}")
            else:
                self._log(f"  [LINKEDIN] Could not bypass CAPTCHA.")
        except Exception as e:
            self._log(f"  [LINKEDIN] Error: {e}")

    def _search_instagram_dork(self, target, limit=10):
        self._log(f"\n[INSTAGRAM] Searching for: {target}")
        try:
            url = f"https://www.google.com/search?q=site:instagram.com+\"{quote_plus(target)}\""
            resp = self.captcha_solver.get_with_bypass(url, callback=self.callback)
            if resp:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, 'html.parser')
                links = [a.get('href') for a in soup.select('a[href*="instagram.com"]') if 'google.com' not in a.get('href', '')]
                if not links:
                    self._log(f"  [INSTAGRAM] No results or Google Captcha blocked.")
                for link in list(set(links))[:limit]:
                    self._log(f"  [INSTAGRAM] {link}")
            else:
                self._log(f"  [INSTAGRAM] Could not bypass CAPTCHA.")
        except Exception as e:
            self._log(f"  [INSTAGRAM] Error: {e}")

    def _search_facebook_dork(self, target, limit=10):
        self._log(f"\n[FACEBOOK] Searching for: {target}")
        try:
            url = f"https://www.google.com/search?q=site:facebook.com+\"{quote_plus(target)}\""
            resp = self.captcha_solver.get_with_bypass(url, callback=self.callback)
            if resp:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, 'html.parser')
                links = [a.get('href') for a in soup.select('a[href*="facebook.com"]') if 'google.com' not in a.get('href', '')]
                if not links:
                    self._log(f"  [FACEBOOK] No results or Google Captcha blocked.")
                for link in list(set(links))[:limit]:
                    self._log(f"  [FACEBOOK] {link}")
            else:
                self._log(f"  [FACEBOOK] Could not bypass CAPTCHA.")
        except Exception as e:
            self._log(f"  [FACEBOOK] Error: {e}")

    def stop(self):
        self.running = False


# ─────────────────────────────────────────────
#  GEOINT ENGINE
# ─────────────────────────────────────────────
class GEOINTEngine:
    """Geospatial Intelligence - resolves IPs to full geolocation data."""

    def __init__(self, callback=None):
        self.callback = callback
        self.results = []

    def geolocate_ip(self, ip):
        """Fetch geolocation for a single IP using ipapi.co."""
        try:
            resp = TORRouter.get(f"https://ipapi.co/{ip}/json/")
            data = resp.json()
            if 'error' in data:
                return None
            result = {
                'ip': ip,
                'city': data.get('city', 'Unknown'),
                'region': data.get('region', 'Unknown'),
                'country': data.get('country_name', 'Unknown'),
                'country_code': data.get('country_code', '??'),
                'org': data.get('org', 'Unknown'),
                'asn': data.get('asn', 'Unknown'),
                'lat': data.get('latitude'),
                'lon': data.get('longitude'),
                'timezone': data.get('timezone', 'Unknown'),
            }
            self.results.append(result)
            return result
        except Exception as e:
            return {'ip': ip, 'error': str(e)}

    def geolocate_bulk(self, ips, progress_callback=None):
        """Geolocate a list of IPs with rate limiting."""
        self.results = []
        for i, ip in enumerate(ips):
            if progress_callback:
                progress_callback(f"  [GEOINT] [{i+1}/{len(ips)}] Locating {ip}...")
            result = self.geolocate_ip(ip)
            if result and progress_callback:
                if 'error' in result:
                    progress_callback(f"    -> Error: {result['error']}")
                else:
                    progress_callback(
                        f"    -> {result['city']}, {result['country']} | "
                        f"Org: {result['org']} | Coords: {result['lat']},{result['lon']}"
                    )
            time.sleep(1.2)  # Rate limit: ~50 req/min on free tier
        return self.results

    def get_map_url(self, lat, lon):
        """Generate an OpenStreetMap URL for coordinates."""
        return f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=12/{lat}/{lon}"
