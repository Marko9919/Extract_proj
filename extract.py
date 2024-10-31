import re
import sys
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.parse import urljoin


def printUsage():
    """
    Prints the usage instructions for the script.

    This function is called when the script is run 
    with no or incorrect arguments or when an arugemt is either -h or --help.
    """
    print("\n")
    print("Pass an url of a website as an only argument to exatract logo url and phone number.")
    print("Options:")
    print("  -h or --help:      shows this help")
    print("  <web page url>:    e.g. https://www.zaba.hr/home/en")
    print("\n")


def extPhoneNum(soup):
    """
    Extracts phone numbers from the website and prints them in a comma-separated format.

    Parameters:
    soup: The parsed HTML content of the webpage.

    If no phone numbers are found, prints 'None'.
    """
    phone_num_pattern = re.compile(
        r"""
        (?!\b\d{6}\b)
        \+?\d{1,3}[\s\-]?              # Optional country code (e.g., +1, +385)
        (?:\(?\d{1,4}\)?[\s\-]?)?      # Optional area code (with or without parentheses)
        (?:\d{1,4}[\s\-]?){1,2} 
        \d{1,4}                        # First block of digits (4 digits max)
        [\s\-]?                        # Optional separator
        \d{1,4}                        # Second block of digits (4 digits max)
        [\s\-]?                        # Optional separator
        \d{1,4}                        # Final block of digits (4 digits max)
        |                              # OR
        \(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}
        """,
        re.VERBOSE
    )

    matches = phone_num_pattern.findall(soup.text)
    found_numbers = set()
    for match in matches:
        match = re.sub(r"[^0-9+()\s]", " ", match)
        if 6 <= len(match) <= 18:
            found_numbers.add(match)

    if found_numbers:
        print(", ".join(found_numbers))
    else:
        print("None")


def extLogoUrl(soup,url):
    """
    Extracts the logo URL from the website's HTML content and prints it.

    Parameters:
    soup: The parsed HTML content of the webpage.
    url: The base URL of the webpage to resolve relative paths.

    If no logo URL is found, prints 'None'.
    """
    logo_url = None
    for img in soup.find_all('img', {"src": lambda x: x and x.endswith((".png", ".jpg", ".jpeg", ".webp", ".svg"))}):
        src = img.get('src')
        if src:
            full_url = urljoin(url, src).replace(" ", "%20")
            if re.search(r'logo', full_url, re.IGNORECASE):
                logo_url = full_url
                break

    print(logo_url if logo_url else "None")


def extract(url):
    """
    Initializes a headless Chrome WebDriver session, retrieves the HTML content, and
    extracts phone numbers and logo URL.

    Parameters:
    url: The URL of the website to extract information from.
    
    Calls `extPhoneNum` and `extLogoUrl` to print the results.
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    r = webdriver.Chrome(options=options)
    r.implicitly_wait(10)
    r.get(url)
    soup = BeautifulSoup(r.page_source, features='html.parser')
    r.quit()

    extPhoneNum(soup)
    extLogoUrl(soup,url)


def main(argv):
    """
    Parses command-line arguments and directs the script's flow accordingly.

    Parameters:
    argv: The argument passed to the script (either a URL or a help flag).

    Prints usage instructions if the input is invalid.
    """
    if argv in ['-h', '--help']:
        printUsage()
    elif argv[:4] == 'http':
        extract(argv)
    else:
        print("Not a validurl.")
        printUsage()


if __name__ == '__main__':
    """
    Entry point for the script. Verifies argument count and calls the main function.
    """
    if len(sys.argv)-1 == 1:
        main(sys.argv[1])
    elif len(sys.argv)-1 < 1:
        print("There is no argument.")
        printUsage()
    else:
        print("To many arguments.")
        printUsage()
