import argparse
import requests
import re
import json
import Messages

class WebsiteTechnologyScanner:
    """Scans a website to identify the technology it uses."""

    TECHNOLOGIES = {
        "WordPress": re.compile(r"wp-content|wordpress", re.I),
        "Django": re.compile(r"csrfmiddlewaretoken|django", re.I),
        "Flask": re.compile(r"flask-session|flask", re.I),
        "Ruby on Rails": re.compile(r"ruby|rails", re.I),
        "Laravel": re.compile(r"laravel|php artisan", re.I),
        "Next.js": re.compile(r"nextjs|_next", re.I),
        "React": re.compile(r"react|react-dom", re.I),
        "Vue.js": re.compile(r"vuejs|vue-router", re.I),
        "CS-Cart": re.compile(r"cscart|var/(cache|compiled)", re.I),
        "Bitrix": re.compile(r"bitrix|bxcore", re.I),
    }

    WEB_SERVERS = {
        "nginx": re.compile(r"nginx", re.I),
        "Apache": re.compile(r"apache", re.I),
        "LiteSpeed": re.compile(r"LiteSpeed", re.I),
    }

    BACKEND_LANGUAGES = {
        "PHP": re.compile(r"php", re.I),
        "Python": re.compile(r"python", re.I),
        "Ruby": re.compile(r"ruby", re.I),
        "Node.js": re.compile(r"node.js|javascript", re.I),
    }

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    def __init__(self, url, verbose=True, output_json=False):
        self.url = url
        self.verbose = verbose
        self.output_json = output_json
        self.results = {}

    def fetch_website(self):
        """Fetches the website content."""
        try:
            if self.verbose:
                Messages.info(f"Fetching content from {self.url}")
            response = requests.get(self.url, headers=self.HEADERS, timeout=10)
            response.raise_for_status()
            server = response.headers.get("Server", "Unknown")
            if self.verbose:
                Messages.success(f"Web Server: {server}")
            self.results["Web Server"] = server
            self.detect_web_server(server)
            return response.text, response.headers
        except requests.RequestException as e:
            Messages.error(f"Connection error: {e}")
            return None, None

    def detect_web_server(self, server_info):
        """Detects the web server from the response headers."""
        Messages.info("Analyzing web server information.")
        for server, pattern in self.WEB_SERVERS.items():
            if pattern.search(server_info):
                Messages.success(f"Detected web server: {server}")
                self.results["Web Server"] = server
                return
        Messages.warn("No known web server detected.")

    def identify_technology(self, html):
        """Identifies the technology based on HTML content."""
        Messages.info("Analyzing website content for technology patterns.")
        for tech, pattern in self.TECHNOLOGIES.items():
            match = pattern.search(html)
            if match:
                Messages.success(f"Frontend: {tech} (Detected by: {match.group()})")
                self.results["Frontend"] = {
                    "name": tech,
                    "detected_by": match.group()
                }

    def identify_backend_language(self, html, headers):
        """Identifies the backend language from the HTML content and headers."""
        Messages.info("Analyzing website content and headers for backend language patterns.")
        for lang, pattern in self.BACKEND_LANGUAGES.items():
            match_html = pattern.search(html)
            match_header = any(pattern.search(value) for value in headers.values())

            if match_html or match_header:
                source = "HTML" if match_html else "Headers"
                match_value = match_html.group() if match_html else next(
                    (value for value in headers.values() if pattern.search(value)), "Unknown")
                Messages.success(f"Language: {lang} (Detected in {source} by: {match_value})")
                self.results["Backend Language"] = {
                    "name": lang,
                    "source": source,
                    "detected_by": match_value
                }
                return
        Messages.warn("No backend language detected.")

    def run(self):
        """Executes the scanning process."""
        Messages.banner()
        Messages.info(f"Starting scan for website: {self.url}")
        html_content, headers = self.fetch_website()

        if not html_content:
            Messages.warn("Failed to retrieve website content.")
            return

        self.identify_technology(html_content)
        self.identify_backend_language(html_content, headers)

        if self.results:
            Messages.info("Scan results:")
            for key, value in self.results.items():
                if isinstance(value, dict):
                    Messages.success(f"{key}: {value['name']} (Detected by: {value['detected_by']})")
                else:
                    Messages.success(f"{key}: {value}")
        else:
            Messages.warn("No technologies detected.")

        if self.output_json:
            print(json.dumps(self.results, indent=4))
        Messages.info("Scan completed.")

def main():
    parser = argparse.ArgumentParser(description="Website Technology Scanner")
    parser.add_argument("url", help="URL of the website to scan")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    args = parser.parse_args()

    scanner = WebsiteTechnologyScanner(url=args.url, verbose=args.verbose or True, output_json=args.json)
    scanner.run()

if __name__ == "__main__":
    main()
