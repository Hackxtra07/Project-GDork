"""
Person Intelligence Engine - Phase 5
Complete person investigation: HIBP, Holehe, Sherlock, Dehashed, PimEyes, FaceCheck, LeakCheck, VirusTotal URL
"""

import requests
import subprocess
import threading
import json
import os
import base64
import time
import re
from urllib.parse import quote_plus


# ─────────────────────────────────────────────
#  HAVE I BEEN PWNED (HIBP)
# ─────────────────────────────────────────────
class HIBPEngine:
    """Check email against HaveIBeenPwned breach database."""

    BASE_URL = "https://haveibeenpwned.com/api/v3"

    def __init__(self, api_key=""):
        self.api_key = api_key
        self.headers = {
            "hibp-api-key": api_key,
            "user-agent": "GDork-OSINT-Suite/5.0"
        }

    def check_email(self, email):
        """Check if email appears in known data breaches."""
        if not self.api_key:
            return {"error": "HIBP API Key required. Get one free at haveibeenpwned.com/API/Key"}
        try:
            url = f"{self.BASE_URL}/breachedaccount/{quote_plus(email)}?truncateResponse=false"
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                breaches = resp.json()
                return {
                    "found": True,
                    "count": len(breaches),
                    "breaches": [
                        {
                            "name": b.get("Name"),
                            "domain": b.get("Domain"),
                            "breach_date": b.get("BreachDate"),
                            "pwn_count": b.get("PwnCount"),
                            "data_classes": b.get("DataClasses", [])
                        }
                        for b in breaches
                    ]
                }
            elif resp.status_code == 404:
                return {"found": False, "count": 0, "breaches": []}
            elif resp.status_code == 401:
                return {"error": "Invalid HIBP API Key."}
            elif resp.status_code == 429:
                return {"error": "Rate limited. Wait 1 second between requests."}
            else:
                return {"error": f"HIBP Error: {resp.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def check_password(self, password):
        """k-anonymity check of password hash prefix against HIBP Pwned Passwords."""
        import hashlib
        sha1 = hashlib.sha1(password.encode()).hexdigest().upper()
        prefix, suffix = sha1[:5], sha1[5:]
        try:
            resp = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}", timeout=10)
            if resp.status_code == 200:
                hashes = resp.text.splitlines()
                for h in hashes:
                    h_suffix, count = h.split(":")
                    if h_suffix == suffix:
                        return {"pwned": True, "count": int(count)}
                return {"pwned": False, "count": 0}
        except Exception as e:
            return {"error": str(e)}


# ─────────────────────────────────────────────
#  HOLEHE (Email → Registered Sites)
# ─────────────────────────────────────────────
class HoleheEngine:
    """Run holehe to check email registration on 120+ sites."""

    def __init__(self, callback=None):
        self.callback = callback
        self.running = False

    def is_installed(self):
        try:
            result = subprocess.run(
                ["holehe", "--help"],
                capture_output=True, text=True, timeout=5
            )
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            # Try python -m holehe
            try:
                result = subprocess.run(
                    ["python", "-m", "holehe", "--help"],
                    capture_output=True, text=True, timeout=5
                )
                return result.returncode == 0
            except:
                return False

    def run(self, email):
        """Run holehe against an email in a background thread."""
        self.running = True
        threading.Thread(target=self._worker, args=(email,), daemon=True).start()

    def _worker(self, email):
        if self.callback:
            self.callback(f"\n[HOLEHE] Checking registration for: {email}")
            self.callback("[HOLEHE] Scanning 120+ sites...\n")
        
        # Determine correct command to execute (standalone vs python module)
        cmd = ["holehe", email, "--no-color", "--only-used"]
        try:
            # Quick test to see if standalone command is available
            subprocess.run(["holehe", "--help"], capture_output=True, timeout=2)
        except (FileNotFoundError, subprocess.SubprocessError):
            cmd = ["python", "-m", "holehe", email, "--no-color", "--only-used"]
            
        try:
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1
            )
            for line in iter(proc.stdout.readline, ''):
                if not self.running:
                    proc.terminate()
                    break
                line = line.rstrip()
                if line and self.callback:
                    # Color code ✔ (found) vs ✗ (not found)
                    self.callback(f"  {line}")
            proc.wait()
        except Exception as e:
            if self.callback:
                self.callback(f"  [HOLEHE ERROR] {e}")
                self.callback("  [INFO] Install holehe: pip install holehe")
        finally:
            self.running = False
            if self.callback:
                self.callback("\n[HOLEHE] Scan complete.")

    def stop(self):
        self.running = False


# ─────────────────────────────────────────────
#  SHERLOCK (Username → Social Profiles)
# ─────────────────────────────────────────────
class SherlockEngine:
    """Run Sherlock to find usernames across 400+ social networks."""

    def __init__(self, callback=None):
        self.callback = callback
        self.running = False
        self.process = None
        self.found_urls = []

    def is_installed(self):
        try:
            result = subprocess.run(
                ["sherlock", "--help"],
                capture_output=True, text=True, timeout=5
            )
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            try:
                result = subprocess.run(
                    ["python", "-m", "sherlock", "--help"],
                    capture_output=True, text=True, timeout=5
                )
                return result.returncode == 0
            except:
                return False

    def run(self, username, timeout=10):
        """Run Sherlock for a username in a background thread."""
        self.running = True
        self.found_urls = []
        threading.Thread(target=self._worker, args=(username, timeout), daemon=True).start()

    def _worker(self, username, timeout):
        if self.callback:
            self.callback(f"\n[SHERLOCK] Hunting username: {username}")
            self.callback("[SHERLOCK] Scanning 400+ social platforms...\n")

        cmd = ["python", "-m", "sherlock", username, "--timeout", str(timeout), "--print-found"]
        try:
            self.process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1
            )
            for line in iter(self.process.stdout.readline, ''):
                if not self.running:
                    self.process.terminate()
                    break
                line = line.rstrip()
                if line and self.callback:
                    self.callback(f"  {line}")
                # Collect found URLs
                if "[+]" in line or "http" in line.lower():
                    url_match = re.search(r'https?://\S+', line)
                    if url_match:
                        self.found_urls.append(url_match.group(0))
            self.process.wait()
        except Exception as e:
            if self.callback:
                self.callback(f"  [SHERLOCK ERROR] {e}")
                self.callback("  [INFO] Install sherlock: pip install sherlock-project")
        finally:
            self.running = False
            if self.callback:
                self.callback(f"\n[SHERLOCK] Done. Found {len(self.found_urls)} profiles.")

    def stop(self):
        self.running = False
        if self.process:
            self.process.terminate()


# ─────────────────────────────────────────────
#  DEHASHED (Deep Breach Search)
# ─────────────────────────────────────────────
class DehashedEngine:
    """Query Dehashed for email/username/IP/password breach data."""

    BASE_URL = "https://api.dehashed.com/search"

    def __init__(self, email="", api_key=""):
        self.auth_email = email
        self.api_key = api_key

    def search(self, query, query_type="email"):
        """Search Dehashed. query_type: email, username, ip_address, password, name, vin."""
        if not self.api_key or not self.auth_email:
            return {"error": "Dehashed requires both account email and API key. Visit dehashed.com"}
        try:
            params = {"query": f"{query_type}:{query}", "size": 20}
            resp = requests.get(
                self.BASE_URL,
                auth=(self.auth_email, self.api_key),
                params=params,
                headers={"Accept": "application/json"},
                timeout=15
            )
            if resp.status_code == 200:
                data = resp.json()
                entries = data.get("entries") or []
                return {
                    "total": data.get("total", 0),
                    "entries": [
                        {
                            "email": e.get("email"),
                            "username": e.get("username"),
                            "password": e.get("password"),
                            "hashed_password": e.get("hashed_password"),
                            "name": e.get("name"),
                            "phone": e.get("phone"),
                            "database_name": e.get("database_name"),
                        }
                        for e in entries[:20]
                    ]
                }
            elif resp.status_code == 401:
                return {"error": "Invalid Dehashed credentials."}
            elif resp.status_code == 302:
                return {"error": "Dehashed subscription required."}
            else:
                return {"error": f"Dehashed Error {resp.status_code}: {resp.text[:100]}"}
        except Exception as e:
            return {"error": str(e)}


# ─────────────────────────────────────────────
#  LEAKCHECK.IO (Free Breach Lookup)
# ─────────────────────────────────────────────
class LeakCheckEngine:
    """Free/freemium breach lookup via leakcheck.io."""

    BASE_URL = "https://leakcheck.io/api/public"

    def __init__(self, api_key=""):
        self.api_key = api_key

    def check(self, query, query_type="email"):
        """Check for breaches. query_type: email, username, phone, hash, domain."""
        try:
            params = {"check": query}
            if self.api_key:
                params["key"] = self.api_key
            resp = requests.get(self.BASE_URL, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success"):
                    return {
                        "found": data.get("found", 0) > 0,
                        "count": data.get("found", 0),
                        "sources": data.get("sources", [])
                    }
                return {"error": data.get("error", "Unknown error")}
            return {"error": f"LeakCheck Error: {resp.status_code}"}
        except Exception as e:
            return {"error": str(e)}


# ─────────────────────────────────────────────
#  PIMEYES (Facial Recognition)
# ─────────────────────────────────────────────
class PimEyesEngine:
    """PimEyes facial recognition API integration."""

    BASE_URL = "https://pimeyes.com/api"

    def __init__(self, api_key=""):
        self.api_key = api_key

    def search_face(self, image_path):
        """Upload an image and search for face matches."""
        if not self.api_key:
            return {"error": "PimEyes API key required. Visit pimeyes.com for pricing."}
        try:
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode()

            headers = {"x-api-key": self.api_key, "Content-Type": "application/json"}
            
            # Upload image
            upload_resp = requests.post(
                f"{self.BASE_URL}/upload/face",
                json={"image": f"data:image/jpeg;base64,{image_data}"},
                headers=headers, timeout=30
            )
            if upload_resp.status_code != 200:
                return {"error": f"PimEyes upload failed: {upload_resp.status_code} - {upload_resp.text[:100]}"}

            upload_data = upload_resp.json()
            faces = upload_data.get("faces", [])
            if not faces:
                return {"error": "No faces detected in the uploaded image."}

            face_id = faces[0].get("id")

            # Search
            search_resp = requests.post(
                f"{self.BASE_URL}/search/face",
                json={"faceId": face_id, "limit": 20},
                headers=headers, timeout=30
            )
            if search_resp.status_code == 200:
                results = search_resp.json().get("results", [])
                return {
                    "found": len(results) > 0,
                    "count": len(results),
                    "matches": [
                        {
                            "url": r.get("pageUrl"),
                            "thumbnail": r.get("thumbnailUrl"),
                            "similarity": r.get("score")
                        }
                        for r in results
                    ]
                }
            return {"error": f"PimEyes search failed: {search_resp.status_code}"}
        except FileNotFoundError:
            return {"error": f"Image file not found: {image_path}"}
        except Exception as e:
            return {"error": str(e)}


# ─────────────────────────────────────────────
#  FACECHECK.ID (Facial Recognition)
# ─────────────────────────────────────────────
class FaceCheckEngine:
    """FaceCheck.id facial recognition API integration."""

    BASE_URL = "https://facecheck.id/api"

    def __init__(self, api_token=""):
        self.api_token = api_token

    def search_face(self, image_path):
        """Upload image to FaceCheck.id and get matches."""
        if not self.api_token:
            return {"error": "FaceCheck.id API token required. Visit facecheck.id for access."}
        try:
            with open(image_path, "rb") as f:
                files = {"images": f}
                headers = {"accept": "application/json"}
                params = {"id_search": self.api_token}
                
                # Post image
                post_resp = requests.post(
                    f"{self.BASE_URL}/upload_pic",
                    files=files, params=params, headers=headers, timeout=30
                )
            if post_resp.status_code != 200:
                return {"error": f"FaceCheck upload error: {post_resp.status_code}"}

            upload_data = post_resp.json()
            id_search = upload_data.get("id_search") or upload_data.get("output", {}).get("id_search")
            if not id_search:
                return {"error": "No search ID returned from FaceCheck."}

            # Poll for results
            for attempt in range(15):
                time.sleep(3)
                search_resp = requests.post(
                    f"{self.BASE_URL}/search",
                    json={"id_search": id_search, "with_progress": True},
                    headers={**headers, "Content-Type": "application/json"},
                    params=params, timeout=30
                )
                if search_resp.status_code == 200:
                    data = search_resp.json()
                    if data.get("output", {}).get("items"):
                        items = data["output"]["items"]
                        return {
                            "found": len(items) > 0,
                            "count": len(items),
                            "matches": [
                                {
                                    "url": item.get("url"),
                                    "score": item.get("score"),
                                    "guid": item.get("guid")
                                }
                                for item in items[:10]
                            ]
                        }
            return {"error": "FaceCheck search timed out."}
        except FileNotFoundError:
            return {"error": f"Image file not found: {image_path}"}
        except Exception as e:
            return {"error": str(e)}


# ─────────────────────────────────────────────
#  VIRUSTOTAL EXPANDED (URL / Domain / Hash)
# ─────────────────────────────────────────────
class VirusTotalExpanded:
    """Extended VirusTotal for URLs, domains, and file hashes."""

    BASE_URL = "https://www.virustotal.com/api/v3"

    def __init__(self, api_key=""):
        self.api_key = api_key
        self.headers = {"x-apikey": api_key}

    def _get_stats(self, endpoint):
        if not self.api_key:
            return {"error": "VirusTotal API key missing."}
        try:
            resp = requests.get(f"{self.BASE_URL}/{endpoint}", headers=self.headers, timeout=15)
            if resp.status_code == 200:
                attrs = resp.json().get("data", {}).get("attributes", {})
                stats = attrs.get("last_analysis_stats", {})
                return {
                    "malicious": stats.get("malicious", 0),
                    "suspicious": stats.get("suspicious", 0),
                    "harmless": stats.get("harmless", 0),
                    "undetected": stats.get("undetected", 0),
                    "reputation": attrs.get("reputation", "N/A"),
                    "categories": attrs.get("categories", {}),
                    "tags": attrs.get("tags", [])
                }
            elif resp.status_code == 404:
                return {"error": "Not found in VirusTotal database."}
            return {"error": f"VT Error: {resp.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def scan_url(self, url):
        url_id = base64.urlsafe_b64encode(url.encode()).decode().rstrip("=")
        return self._get_stats(f"urls/{url_id}")

    def scan_domain(self, domain):
        return self._get_stats(f"domains/{domain}")

    def scan_hash(self, file_hash):
        return self._get_stats(f"files/{file_hash}")

    def submit_url_for_analysis(self, url):
        """Submit a URL for fresh analysis."""
        if not self.api_key:
            return {"error": "API key missing."}
        try:
            resp = requests.post(
                f"{self.BASE_URL}/urls",
                headers=self.headers,
                data={"url": url}, timeout=15
            )
            if resp.status_code in (200, 201):
                analysis_id = resp.json().get("data", {}).get("id")
                return {"submitted": True, "analysis_id": analysis_id}
            return {"error": f"VT submission error: {resp.status_code}"}
        except Exception as e:
            return {"error": str(e)}


# ─────────────────────────────────────────────
#  PERSON INVESTIGATION ORCHESTRATOR
# ─────────────────────────────────────────────
class PersonInvestigator:
    """
    Master orchestrator that runs all person investigation engines
    simultaneously and compiles a unified dossier.
    """

    def __init__(self, keys: dict, callback=None, progress_callback=None):
        self.keys = keys
        self.callback = callback
        self.progress_callback = progress_callback
        self.running = False
        self.results = {}

        # Initialize engines
        self.hibp = HIBPEngine(api_key=keys.get("hibp", ""))
        self.holehe = HoleheEngine(callback=callback)
        self.sherlock = SherlockEngine(callback=callback)
        self.dehashed = DehashedEngine(
            email=keys.get("dehashed_email", ""),
            api_key=keys.get("dehashed", "")
        )
        self.leakcheck = LeakCheckEngine(api_key=keys.get("leakcheck", ""))
        self.pimeyes = PimEyesEngine(api_key=keys.get("pimeyes", ""))
        self.facecheck = FaceCheckEngine(api_token=keys.get("facecheck", ""))
        self.vt = VirusTotalExpanded(api_key=keys.get("virustotal", ""))

    def _log(self, msg):
        if self.callback:
            self.callback(msg)

    def _progress(self, step, total, label):
        if self.progress_callback:
            self.progress_callback(step, total, label)

    def investigate(self, name="", email="", username="", phone="", image_path=""):
        """Launch full investigation in background thread."""
        self.running = True
        self.results = {}
        threading.Thread(
            target=self._run_all,
            args=(name, email, username, phone, image_path),
            daemon=True
        ).start()

    def _run_all(self, name, email, username, phone, image_path):
        total_steps = 7
        step = 0

        self._log("=" * 60)
        self._log(f"🎯 FULL PERSON INVESTIGATION INITIATED")
        self._log(f"   Name: {name or 'N/A'} | Email: {email or 'N/A'}")
        self._log(f"   Username: {username or 'N/A'} | Phone: {phone or 'N/A'}")
        self._log("=" * 60)

        # ── Step 1: HIBP ──────────────────────────────────────────
        if email:
            step += 1
            self._progress(step, total_steps, "Checking HaveIBeenPwned...")
            self._log("\n📧 [HIBP] Checking email breach history...")
            hibp_result = self.hibp.check_email(email)
            self.results["hibp"] = hibp_result
            if "error" in hibp_result:
                self._log(f"  -> Error: {hibp_result['error']}")
            elif hibp_result.get("found"):
                self._log(f"  ⚠️  PWNED! Found in {hibp_result['count']} breach(es):")
                for b in hibp_result["breaches"][:5]:
                    self._log(f"    • {b['name']} ({b['breach_date']}) — {', '.join(b['data_classes'][:3])}")
            else:
                self._log("  ✅ Not found in any known breaches.")
            time.sleep(1.5)

        # ── Step 2: LeakCheck ─────────────────────────────────────
        if email:
            step += 1
            self._progress(step, total_steps, "Querying LeakCheck.io...")
            self._log("\n💥 [LEAKCHECK] Cross-referencing with LeakCheck.io...")
            lc_result = self.leakcheck.check(email)
            self.results["leakcheck"] = lc_result
            if "error" in lc_result:
                self._log(f"  -> Error: {lc_result['error']}")
            elif lc_result.get("found"):
                self._log(f"  ⚠️  Found in {lc_result['count']} breach source(s):")
                for src in lc_result.get("sources", [])[:5]:
                    self._log(f"    • {src.get('name')} — {src.get('date', 'N/A')}")
            else:
                self._log("  ✅ Not found in LeakCheck database.")

        # ── Step 3: Dehashed ──────────────────────────────────────
        if email and self.keys.get("dehashed"):
            step += 1
            self._progress(step, total_steps, "Searching Dehashed...")
            self._log("\n🗄️ [DEHASHED] Searching breach database...")
            dh_result = self.dehashed.search(email, "email")
            self.results["dehashed"] = dh_result
            if "error" in dh_result:
                self._log(f"  -> Error: {dh_result['error']}")
            else:
                self._log(f"  Found {dh_result.get('total', 0)} records:")
                for e in dh_result.get("entries", [])[:5]:
                    self._log(f"    • DB: {e['database_name']} | Pass: {e.get('password','[hidden]')} | User: {e.get('username','')}")

        # ── Step 4: Holehe ────────────────────────────────────────
        if email:
            step += 1
            self._progress(step, total_steps, "Running Holehe (120+ sites)...")
            self._log("\n🔍 [HOLEHE] Checking site registrations...")
            if self.holehe.is_installed():
                holehe_done = threading.Event()
                orig_cb = self.holehe.callback
                def wrapped_cb(msg):
                    if orig_cb: orig_cb(msg)
                    if "Scan complete" in msg:
                        holehe_done.set()
                self.holehe.callback = wrapped_cb
                self.holehe.run(email)
                holehe_done.wait(timeout=120)
                self.holehe.callback = orig_cb
            else:
                self._log("  [HOLEHE] Not installed. Run: pip install holehe")

        # ── Step 5: Sherlock ──────────────────────────────────────
        if username:
            step += 1
            self._progress(step, total_steps, "Running Sherlock (400+ platforms)...")
            self._log("\n🕵️ [SHERLOCK] Username hunt across the internet...")
            if self.sherlock.is_installed():
                sherlock_done = threading.Event()
                orig_cb = self.sherlock.callback
                def wrapped_cb(msg):
                    if orig_cb: orig_cb(msg)
                    if "Done." in msg:
                        sherlock_done.set()
                self.sherlock.callback = wrapped_cb
                self.sherlock.run(username)
                sherlock_done.wait(timeout=180)
                self.sherlock.callback = orig_cb
                self.results["sherlock_urls"] = self.sherlock.found_urls
            else:
                self._log("  [SHERLOCK] Not installed. Run: pip install sherlock-project")

        # ── Step 6: Face Recognition ──────────────────────────────
        if image_path and os.path.exists(image_path):
            step += 1
            self._progress(step, total_steps, "Running Face Recognition...")
            self._log("\n📸 [FACE SEARCH] Running PimEyes + FaceCheck.id...")

            if self.keys.get("pimeyes"):
                self._log("  [PIMEYES] Uploading and searching...")
                pe_result = self.pimeyes.search_face(image_path)
                self.results["pimeyes"] = pe_result
                if "error" in pe_result:
                    self._log(f"  -> PimEyes Error: {pe_result['error']}")
                else:
                    self._log(f"  ✅ PimEyes found {pe_result.get('count', 0)} matches.")
                    for m in pe_result.get("matches", [])[:3]:
                        self._log(f"    • {m.get('url')} (score: {m.get('similarity')})")
            else:
                self._log("  [PIMEYES] API key not configured. Go to Settings to add it.")

            if self.keys.get("facecheck"):
                self._log("  [FACECHECK] Uploading and polling results...")
                fc_result = self.facecheck.search_face(image_path)
                self.results["facecheck"] = fc_result
                if "error" in fc_result:
                    self._log(f"  -> FaceCheck Error: {fc_result['error']}")
                else:
                    self._log(f"  ✅ FaceCheck found {fc_result.get('count', 0)} matches.")
                    for m in fc_result.get("matches", [])[:3]:
                        self._log(f"    • Score: {m.get('score')} -> {m.get('url')}")
            else:
                self._log("  [FACECHECK] API token not configured. Go to Settings to add it.")

        # ── Step 7: Finalize ──────────────────────────────────────
        step += 1
        self._progress(step, total_steps, "Finalizing dossier...")
        self._log("\n" + "=" * 60)
        self._log("📋 INVESTIGATION COMPLETE — DOSSIER SUMMARY")
        self._log("=" * 60)
        self._log(f"  Target: {name or 'Unknown'} | Email: {email or 'N/A'} | Username: {username or 'N/A'}")

        hibp_r = self.results.get("hibp", {})
        if not hibp_r.get("error") and hibp_r.get("found"):
            self._log(f"  ⚠️  Breaches: {hibp_r.get('count', 0)} (HIBP)")

        lc_r = self.results.get("leakcheck", {})
        if not lc_r.get("error") and lc_r.get("found"):
            self._log(f"  ⚠️  Breaches: {lc_r.get('count', 0)} (LeakCheck)")

        sherlock_urls = self.results.get("sherlock_urls", [])
        if sherlock_urls:
            self._log(f"  👤 Social Profiles: {len(sherlock_urls)} found by Sherlock")
            for url in sherlock_urls[:5]:
                self._log(f"    → {url}")

        self._log("=" * 60)
        self.running = False

    def stop(self):
        self.running = False
        self.holehe.stop()
        self.sherlock.stop()

    def generate_html_dossier(self, name="", email=""):
        """Generate a styled HTML report from investigation results."""
        breaches = self.results.get("hibp", {}).get("breaches", [])
        lc_sources = self.results.get("leakcheck", {}).get("sources", [])
        sherlock_urls = self.results.get("sherlock_urls", [])
        pimeyes_matches = self.results.get("pimeyes", {}).get("matches", [])
        facecheck_matches = self.results.get("facecheck", {}).get("matches", [])

        def rows(items, keys):
            if not items:
                return "<tr><td colspan='10'>No data found.</td></tr>"
            html = ""
            for item in items:
                html += "<tr>" + "".join(f"<td>{item.get(k,'')}</td>" for k in keys) + "</tr>"
            return html

        html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8">
<title>Person Dossier — {name}</title>
<style>
body{{background:#0d0d0d;color:#eee;font-family:'Segoe UI',sans-serif;padding:30px}}
h1{{color:#4285f4;border-bottom:2px solid #4285f4;padding-bottom:10px}}
h2{{color:#fbbc05;margin-top:30px}}
table{{width:100%;border-collapse:collapse;margin:10px 0}}
th{{background:#1a1a2e;color:#4285f4;padding:8px;text-align:left}}
td{{border-bottom:1px solid #333;padding:7px;font-size:13px}}
.badge-danger{{background:#ea4335;color:white;padding:2px 8px;border-radius:4px}}
.badge-safe{{background:#34a853;color:white;padding:2px 8px;border-radius:4px}}
a{{color:#4285f4}}
</style></head>
<body>
<h1>🎯 Intelligence Dossier: {name}</h1>
<p><b>Email:</b> {email} &nbsp; <b>Generated:</b> {time.strftime('%Y-%m-%d %H:%M')}</p>

<h2>📧 HaveIBeenPwned Breaches ({len(breaches)} found)</h2>
<table><tr><th>Breach</th><th>Domain</th><th>Date</th><th>Records</th><th>Data Types</th></tr>
{rows(breaches, ['name','domain','breach_date','pwn_count','data_classes'])}
</table>

<h2>💥 LeakCheck Sources ({len(lc_sources)} sources)</h2>
<table><tr><th>Source</th><th>Date</th></tr>
{rows(lc_sources, ['name','date'])}
</table>

<h2>👤 Sherlock — Social Profiles ({len(sherlock_urls)} found)</h2>
<table><tr><th>Profile URL</th></tr>
{''.join(f'<tr><td><a href="{u}" target="_blank">{u}</a></td></tr>' for u in sherlock_urls)}
</table>

<h2>📸 PimEyes Face Matches ({len(pimeyes_matches)} found)</h2>
<table><tr><th>URL</th><th>Similarity</th></tr>
{rows(pimeyes_matches, ['url','similarity'])}
</table>

<h2>📸 FaceCheck.id Matches ({len(facecheck_matches)} found)</h2>
<table><tr><th>URL</th><th>Score</th></tr>
{rows(facecheck_matches, ['url','score'])}
</table>
</body></html>"""

        fname = f"dossier_{name.replace(' ','_')}_{int(time.time())}.html"
        output_path = os.path.join(os.path.dirname(__file__), '..', fname)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        return output_path
