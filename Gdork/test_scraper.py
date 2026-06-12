from scraper_engine import DeepScraper

def test_scraper():
    scraper = DeepScraper()
    print("Testing Regex Patterns on mock data...")
    mock_html = """
    <html>
        <body>
            Contact me at test.user@example.com or support@company.co.uk!
            Call us at (555) 123-4567 or 555-987-6543.
            Follow me on https://twitter.com/johndoe and https://github.com/coder_123
            Donate BTC: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
            Server IP: 192.168.1.100
        </body>
    </html>
    """
    
    import re
    emails = re.findall(scraper.patterns['emails'], mock_html)
    phones = re.findall(scraper.patterns['phones'], mock_html)
    socials = re.findall(scraper.patterns['socials'], mock_html)
    crypto = re.findall(scraper.patterns['crypto_btc'], mock_html)
    ips = re.findall(scraper.patterns['ips'], mock_html)
    
    assert 'test.user@example.com' in emails
    assert 'support@company.co.uk' in emails
    assert '(555) 123-4567' in phones
    assert '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa' in crypto
    assert '192.168.1.100' in ips
    
    print("All Regex tests passed!")

if __name__ == "__main__":
    test_scraper()
