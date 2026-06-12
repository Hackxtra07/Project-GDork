import requests
import json
import os

class ConfigManager:
    def __init__(self):
        self.config_file = os.path.join(os.path.dirname(__file__), 'api_config.json')
        self.keys = self.load_keys()

    def load_keys(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_keys(self, shodan_key, vt_key):
        self.keys = {
            'shodan': shodan_key,
            'virustotal': vt_key
        }
        with open(self.config_file, 'w') as f:
            json.dump(self.keys, f, indent=4)

class ShodanEngine:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.shodan.io"

    def scan_ip(self, ip):
        if not self.api_key:
            return {"error": "Shodan API Key is missing."}
        try:
            url = f"{self.base_url}/shodan/host/{ip}?key={self.api_key}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "ip": data.get("ip_str"),
                    "org": data.get("org", "Unknown"),
                    "os": data.get("os", "Unknown"),
                    "ports": data.get("ports", []),
                    "vulns": data.get("vulns", [])
                }
            elif resp.status_code == 401:
                return {"error": "Invalid Shodan API Key."}
            else:
                return {"error": f"Shodan API Error: {resp.status_code}"}
        except Exception as e:
            return {"error": str(e)}

class VirusTotalEngine:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://www.virustotal.com/api/v3"
        self.headers = {
            "x-apikey": self.api_key
        }

    def scan_ip(self, ip):
        if not self.api_key:
            return {"error": "VirusTotal API Key is missing."}
        try:
            url = f"{self.base_url}/ip_addresses/{ip}"
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
                return {
                    "malicious": stats.get("malicious", 0),
                    "suspicious": stats.get("suspicious", 0),
                    "harmless": stats.get("harmless", 0),
                    "undetected": stats.get("undetected", 0)
                }
            elif resp.status_code == 401:
                return {"error": "Invalid VirusTotal API Key."}
            else:
                return {"error": f"VT API Error: {resp.status_code}"}
        except Exception as e:
            return {"error": str(e)}
