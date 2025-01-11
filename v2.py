import argparse
import requests
import re
import json
from Messages import Messages

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
    
    def detect_technologies(html):
        tech_patterns = {
            "WordPress": r"/wp-content/",
            "Django": r"name=['\"]csrfmiddlewaretoken['\"]",
            "Flask": r"flask",
            "React": r"/static/js/main\.\w+\.js",  # React's bundled JS
            "Vue.js": r"vue.runtime.min.js",
            "Laravel": r"/js/app.js",
            "Ruby on Rails": r"data-turbolinks-track",
            "Next.js": r"__NEXT_DATA__",
        }

        detected_tech = []
        for tech, pattern in tech_patterns.items():
            if re.search(pattern, html, re.I):
                detected_tech.append(tech)

        if detected_tech:
            Messages.success(f"Detected technologies: {', '.join(detected_tech)}")
        else:
            Messages.warning("No technologies detected.")
        return detected_tech


    def detect_backend(headers, html):
        """Detects the backend language used."""
        backend_patterns = {
            "PHP": r"\.php",
            "Python": r"(wsgi|django|flask)",
            "Ruby": r"(rails|\.rb)",
            "Node.js": r"express|node.js",
        }

        detected_backend = None

        # Check headers for backend clues
        for backend, pattern in backend_patterns.items():
            if any(re.search(pattern, value, re.I) for value in headers.values()):
                detected_backend = backend
                break

        # Check HTML content for backend clues
        if not detected_backend:
            for backend, pattern in backend_patterns.items():
                if re.search(pattern, html, re.I):
                    detected_backend = backend
                    break

        if detected_backend:
            Messages.success(f"Detected backend language: {detected_backend}")
        else:
            Messages.warning("No backend language detected.")
        return detected_backend

    
    def detect_web_server(self, server_info):
        """Detects the web server from the response headers."""
        Messages.info("Analyzing web server information.")
        for server, pattern in self.WEB_SERVERS.items():
            if pattern.search(server_info):
                Messages.success(f"Detected web server: {server}")
                self.results["Web Server"] = server
                return
        Messages.warn("No known web server detected.")

    def identify_technology_with_context(self, html):
        """Enhanced technology detection with context."""
        Messages.info("Analyzing website content for technologies.")
        
        for tech, pattern in self.TECHNOLOGIES.items():
            matches = pattern.findall(html)
            
            # Validate matches by checking for meaningful context
            for match in matches:
                context = html[max(0, html.find(match) - 50):html.find(match) + 50]
                if self.is_valid_context(context, tech):
                    Messages.success(f"Detected Frontend: {tech} (Context: {context.strip()})")
                    self.results["Frontend"] = {"name": tech, "detected_by": match}
                    return

        Messages.warn("No frontend technologies detected.")

    def is_valid_context(self, context, tech):
        """Checks if the match context is valid for the given technology."""
        # Example: Ensure context includes related keywords or structural hints
        related_keywords = {
            "WordPress": ["wp-content", "wp-includes"],
            "Django": ["csrfmiddlewaretoken"],
            "Flask": ["flask-session"],
            "React": ["react-dom", "jsx"],
            # Add more specific contexts for other technologies
        }
        
        return any(keyword in context for keyword in related_keywords.get(tech, []))


    def identify_backend_language_with_context(self, html, headers):
        """Enhanced backend language detection with context."""
        Messages.info("Analyzing website headers and content for backend language.")
        
        for lang, pattern in self.BACKEND_LANGUAGES.items():
            match_html = pattern.search(html)
            match_header = any(pattern.search(value) for value in headers.values())
            
            # Validate matches with context
            if match_html:
                context = html[max(0, match_html.start() - 50):match_html.end() + 50]
                if self.is_valid_context(context, lang):
                    Messages.success(f"Detected Backend Language: {lang} (Context: {context.strip()})")
                    self.results["Backend Language"] = {"name": lang, "detected_by": context.strip()}
                    return
            
            if match_header:
                header_value = next(value for key, value in headers.items() if pattern.search(value))
                Messages.success(f"Detected Backend Language: {lang} (Header: {header_value})")
                self.results["Backend Language"] = {"name": lang, "detected_by": "Headers"}
                return

        Messages.warn("No backend language detected.")


    def run(self):
        """Executes the scanning process."""
        Messages.banner()
        Messages.info(f"Starting scan for website: {self.url}")
        
        # Fetch website content and headers
        html_content, headers = self.fetch_website()

        if not html_content:
            Messages.warn("Failed to retrieve website content.")
            return

        # Identify technologies and backend language with enhanced checks
        self.identify_technology_with_context(html_content)
        self.identify_backend_language_with_context(html_content, headers)

        # Display results
        if self.results:
            Messages.info("Scan results:")
            for key, value in self.results.items():
                if isinstance(value, dict):
                    Messages.success(f"{key}: {value['name']} (Detected by: {value['detected_by']})")
                else:
                    Messages.success(f"{key}: {value}")
        else:
            Messages.warn("No technologies detected.")

        # Output results in JSON format if required
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
