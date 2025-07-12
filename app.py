import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime

# Adobe product name patterns and aliases
adobe_patterns = [
    r'photoshop', r'lightroom', r'illustrator', r'xd', r'premiere', r'after[- ]?effects',
    r'indesign', r'audition', r'animate', r'bridge', r'acrobat', r'dreamweaver',
    r'dimension', r'substance', r'fresco', r'media[- ]?encoder',
    r'acrobat[- ]?pro[- ]?dc', r'acrobat[- ]?reader[- ]?dc', r'incopy',
    r'genp[- ]?universal[- ]?patch', r'premiere[- ]?pro', r'altium[- ]?designer',
    r'acrobat[- ]?classic', r'character[- ]?animator', r'videdit'
]
year_pattern = r'(20(1[9]|2[0-6]))'  # 2019-2026
product_year_regex = re.compile(
    r'(' + '|'.join(adobe_patterns) + r')[\w\-]*' + year_pattern,
    re.IGNORECASE
)

# Links to exclude
exclude_links = {
    "https://www.cybermania.ws/apps/",
}

# Links to force include
force_include_links = {
    "https://www.cybermania.ws/cybermania/disable-adobe-genuine-software-integrity-service/",
    "https://www.cybermania.ws/apps/ags-disabler-disable-adobe-genuine-software/",
    "https://www.cybermania.ws/apps/adobe-genp/",
    "https://www.cybermania.ws/apps/genp-universal-patch/"
}

link_prefix = "https://www.cybermania.ws/apps"
base_url = "https://www.cybermania.ws"
search_url = f"{base_url}/?s=adobe"

def beautify_software_name(folder_name):
    """Beautify folder name for display as software name"""
    return folder_name.replace('-', ' ').replace('_', ' ').title()

def is_valid_adobe_link(href):
    # Force include links return True directly
    if href in force_include_links:
        return True
    if not href.startswith(link_prefix):
        return False
    if "comment-page" in href or "#" in href or href in exclude_links:
        return False
    return bool(product_year_regex.search(href))

def get_links_from_page(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if is_valid_adobe_link(href):
            links.add(href)
    return links, soup

def has_next_page(soup, current_page):
    older_posts = soup.find("a", string=lambda s: s and "Older posts" in s)
    if older_posts:
        return True
    pagination = soup.find("div", class_="pagination")
    if pagination:
        next_links = pagination.find_all("a", href=True)
        for link in next_links:
            if f"/post/{current_page+1}/" in link["href"]:
                return True
    all_links = soup.find_all("a", href=True)
    for link in all_links:
        href = link["href"]
        if any(pattern in href for pattern in [
            f"/post/{current_page+1}/?s=adobe",
            f"/post/{current_page+1}/",
        ]):
            return True
    return False

def get_next_page_url(current_page):
    if current_page == 1:
        return search_url
    return f"{base_url}/post/{current_page}/?s=adobe"

def extract_folder_name(url):
    url = url.rstrip('/')
    if url in force_include_links:
        if url == "https://www.cybermania.ws/cybermania/disable-adobe-genuine-software-integrity-service/":
            return "disable-adobe-genuine-software-integrity-service"
        elif url == "https://www.cybermania.ws/apps/ags-disabler-disable-adobe-genuine-software/":
            return "ags-disabler-disable-adobe-genuine-software"
        elif url == "https://www.cybermania.ws/apps/adobe-genp/":
            return "adobe-genp"
        elif url == "https://www.cybermania.ws/apps/genp-universal-patch/":
            return "genp-universal-patch"
    if '/apps/' in url:
        return url.split('/apps/')[-1]
    elif '/cybermania/' in url:
        return url.split('/cybermania/')[-1]
    return None

def find_download_links(soup):
    """Find all Download links in the page"""
    download_links = []
    version_info = ""
    h1_tag = soup.find("h1", class_="insidepost")
    if h1_tag:
        version_info = h1_tag.get_text(strip=True)
        version_match = re.search(r'(\d+\.\d+\.\d+\.\d+|\d+\.\d+\.\d+|\d+\.\d+|\d+)$', version_info)
        if version_match:
            version_info = version_match.group(1)
    for a in soup.find_all("a", href=True):
        if a.get_text(strip=True).lower() == "download":
            install_mode = ""
            current = a
            found_strong = False
            while current and not found_strong:
                prev_sibling = current.find_previous_sibling()
                while prev_sibling and not found_strong:
                    strong = prev_sibling.find('strong')
                    if strong:
                        install_mode = strong.get_text(strip=True)
                        found_strong = True
                        break
                    strong = prev_sibling.find('strong', recursive=True)
                    if strong:
                        install_mode = strong.get_text(strip=True)
                        found_strong = True
                        break
                    prev_sibling = prev_sibling.find_previous_sibling()
                if not found_strong:
                    current = current.parent
            if not install_mode:
                h2_tag = a.find_parent('h2')
                if h2_tag:
                    prev_p = h2_tag.find_previous_sibling('p')
                    if prev_p:
                        strong = prev_p.find('strong')
                        if strong:
                            install_mode = strong.get_text(strip=True)
            if not install_mode:
                all_strongs = soup.find_all('strong')
                download_position = None
                for i, tag in enumerate(soup.find_all()):
                    if tag == a:
                        download_position = i
                        break
                if download_position is not None:
                    for strong in all_strongs:
                        strong_position = None
                        for i, tag in enumerate(soup.find_all()):
                            if tag == strong:
                                strong_position = i
                                break
                        if strong_position is not None and strong_position < download_position:
                            install_mode = strong.get_text(strip=True)
                            break
            download_links.append({
                'url': a['href'],
                'version_info': version_info,
                'install_mode': install_mode
            })
    return download_links

def create_download_html(download_url, version_info="", install_mode="", software_name="Download Link"):
    """Create HTML content for download page"""
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Download Link</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 50px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .download-btn {{
            display: inline-block;
            background-color: #007bff;
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 5px;
            font-size: 18px;
            font-weight: bold;
            transition: background-color 0.3s;
        }}
        .download-btn:hover {{
            background-color: #0056b3;
        }}
        .info {{
            margin-bottom: 20px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="info">
            <h2>{software_name}</h2>
            {f'<p><strong>Version:</strong> {version_info}</p>' if version_info else ''}
            {f'<p><strong>Install Mode:</strong> {install_mode}</p>' if install_mode else ''}
        </div>
        <a href="{download_url}" class="download-btn" target="_blank">
            Download Now
        </a>
    </div>
</body>
</html>"""
    return html_content

def process_download_links():
    """Process all links in data.txt"""
    data_file = "data/data.txt"
    if not os.path.exists(data_file):
        print(f"Error: File not found {data_file}")
        return
    with open(data_file, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
    print(f"Starting to process {len(urls)} links...")
    for i, url in enumerate(urls, 1):
        print(f"\nProcessing link {i}/{len(urls)}: {url}")
        folder_name = extract_folder_name(url)
        if not folder_name:
            print(f"  Skip: Cannot extract folder name")
            continue
        software_name = beautify_software_name(folder_name)
        folder_path = os.path.join("DownloadLinks", folder_name)
        os.makedirs(folder_path, exist_ok=True)
        print(f"  Created folder: {folder_path}")
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            download_links = find_download_links(soup)
            print(f"  Found {len(download_links)} download links")
            if not download_links:
                default_html = create_download_html("", "", "", software_name)
                with open(os.path.join(folder_path, "DownloadPage.html"), 'w', encoding='utf-8') as f:
                    f.write(default_html)
                print(f"  Created default download page: DownloadPage.html")
            else:
                for j, download_info in enumerate(download_links, 1):
                    version_info = download_info['version_info']
                    install_mode = download_info['install_mode']
                    download_url = download_info['url']
                    if version_info and install_mode:
                        clean_version = re.sub(r'[<>:"/\\|?*]', '_', version_info)
                        clean_install_mode = re.sub(r'[<>:"/\\|?*]', '_', install_mode)
                        filename = f"{clean_version}-{clean_install_mode}-DownloadPage.html"
                    elif version_info:
                        clean_version = re.sub(r'[<>:"/\\|?*]', '_', version_info)
                        filename = f"{clean_version}-DownloadPage.html"
                    elif install_mode:
                        clean_install_mode = re.sub(r'[<>:"/\\|?*]', '_', install_mode)
                        filename = f"{clean_install_mode}-DownloadPage.html"
                    else:
                        filename = f"DownloadPage-{j}.html" if len(download_links) > 1 else "DownloadPage.html"
                    html_content = create_download_html(download_url, version_info, install_mode, software_name)
                    file_path = os.path.join(folder_path, filename)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    print(f"  Saved download page: {filename} -> {download_url}")
                    if version_info:
                        print(f"    Version info: {version_info}")
                    if install_mode:
                        print(f"    Install mode: {install_mode}")
        except Exception as e:
            print(f"  Error: {e}")
            continue
    print(f"\nProcessing completed!")

def create_main_download_page():
    """Create main download page"""
    if not os.path.exists("DownloadLinks"):
        print("Error: DownloadLinks directory does not exist")
        return
    download_items = []
    for folder_name in os.listdir("DownloadLinks"):
        folder_path = os.path.join("DownloadLinks", folder_name)
        if os.path.isdir(folder_path):
            html_files = [f for f in os.listdir(folder_path) if f.endswith('.html')]
            if html_files:
                download_files = []
                for html_file in html_files:
                    html_file_path = os.path.join(folder_path, html_file)
                    try:
                        with open(html_file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            href_match = re.search(r'href="([^"]+)"', content)
                            download_url = href_match.group(1) if href_match else ""
                            version_match = re.search(r'<strong>Version:</strong> ([^<]+)</p>', content)
                            version_info = version_match.group(1) if version_match else ""
                            install_match = re.search(r'<strong>Install Mode:</strong> ([^<]+)</p>', content)
                            install_mode = install_match.group(1) if install_match else ""
                            download_files.append({
                                'file_name': html_file,
                                'download_url': download_url,
                                'version_info': version_info,
                                'install_mode': install_mode
                            })
                    except Exception as e:
                        print(f"Error processing file {html_file}: {e}")
                if download_files:
                    display_name = folder_name.replace('-', ' ').replace('_', ' ').title()
                    download_items.append({
                        'name': display_name,
                        'folder': folder_name,
                        'files': download_files
                    })
    download_items.sort(key=lambda x: x['name'])
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Adobe GenP Downloads</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }}
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        .stats {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            border-bottom: 1px solid #e9ecef;
        }}
        .stats span {{
            display: inline-block;
            margin: 0 20px;
            font-size: 1.1em;
            color: #6c757d;
        }}
        .stats strong {{
            color: #667eea;
            font-size: 1.3em;
        }}
        .content {{
            padding: 40px;
        }}
        .download-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 25px;
            margin-top: 30px;
        }}
        .download-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            border: 2px solid transparent;
        }}
        .download-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
            border-color: #667eea;
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }}
        .software-name {{
            font-size: 1.3em;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 5px;
        }}
        .file-count {{
            background: #e9ecef;
            color: #6c757d;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.7em;
        }}
        .download-links {{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        .download-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 15px;
            background: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #e9ecef;
            transition: all 0.3s ease;
        }}
        .download-item:hover {{
            background: #e9ecef;
            border-color: #667eea;
        }}
        .version-info {{
            font-size: 0.9em;
            color: #6c757d;
            font-weight: 500;
        }}
        .download-btn {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 8px 15px;
            text-decoration: none;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.8em;
            transition: all 0.3s ease;
        }}
        .download-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            color: white;
            text-decoration: none;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            color: #6c757d;
            border-top: 1px solid #e9ecef;
        }}
        .search-box {{
            margin-bottom: 30px;
            text-align: center;
        }}
        .search-input {{
            width: 100%;
            max-width: 400px;
            padding: 15px 20px;
            border: 2px solid #e9ecef;
            border-radius: 25px;
            font-size: 1em;
            outline: none;
            transition: border-color 0.3s ease;
        }}
        .search-input:focus {{
            border-color: #667eea;
        }}
        .no-results {{
            text-align: center;
            color: #6c757d;
            font-size: 1.2em;
            margin-top: 50px;
        }}
        @media (max-width: 768px) {{
            .download-grid {{
                grid-template-columns: 1fr;
            }}
            .header h1 {{
                font-size: 2em;
            }}
            .content {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
        <h1>Adobe Downloads</h1>
            <p>Professional design software, one-click download, easy to get</p>
        </div>
        <div class="stats">
            <span>Files: <strong>{len(download_items)}</strong></span>
            <span>UpdateTime: <strong>{datetime.now().strftime('%Y-%m-%d %H:%M')}</strong></span>
        </div>
        <div class="content">
            <div class="search-box">
                <input type="text" class="search-input" id="searchInput" placeholder="Search here..." onkeyup="filterSoftware()">
            </div>
            <div class="download-grid" id="downloadGrid">
"""
    for item in download_items:
        file_count_text = f"{len(item['files'])} Versions" if len(item['files']) > 1 else "1 Version"
        html_content += f"""
                <div class="download-card" data-name="{item['name'].lower()}">
                    <div class="card-header">
                        <div>
                            <div class="software-name">{item['name']}</div>
                            <div class="file-count">{file_count_text}</div>
                        </div>
                    </div>
                    <div class="download-links">
"""
        for i, file_info in enumerate(item['files'], 1):
            version_display = file_info['version_info'] if file_info['version_info'] else "Standard"
            install_mode_display = file_info['install_mode'] if file_info['install_mode'] else ""
            html_content += f"""
                        <div class="download-item">
                            <div class="version-info">{version_display} {install_mode_display}</div>
                            <a href="./DownloadLinks/{item['folder']}/{file_info['file_name']}" class="download-btn" target="_blank">
                                📥 Download
                            </a>
                        </div>
"""
        html_content += """
                    </div>
                </div>
"""
    html_content += """
            </div>
            <div class="no-results" id="noResults" style="display: none;">
                No results found
            </div>
        </div>
        <div class="footer">
            <p>© 2025 Adobe GenP Downloads | All software is from the network, for learning only</p>
        </div>
    </div>
    <script>
        function filterSoftware() {
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const cards = document.querySelectorAll('.download-card');
            const noResults = document.getElementById('noResults');
            let visibleCount = 0;
            cards.forEach(card => {
                const softwareName = card.getAttribute('data-name');
                if (softwareName.includes(searchTerm)) {
                    card.style.display = 'block';
                    visibleCount++;
                } else {
                    card.style.display = 'none';
                }
            });
            if (visibleCount === 0) {
                noResults.style.display = 'block';
            } else {
                noResults.style.display = 'none';
            }
        }
        document.addEventListener('DOMContentLoaded', function() {
            const cards = document.querySelectorAll('.download-card');
            cards.forEach((card, index) => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                setTimeout(() => {
                    card.style.transition = 'all 0.5s ease';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, index * 100);
            });
        });
    </script>
</body>
</html>"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated download center page: index.html")
    print(f"Contains {len(download_items)} software download links")
    print("Please open index.html in your browser to view the results")

def main():
    os.makedirs("data", exist_ok=True)
    all_links = set()
    page = 1
    max_pages = 50
    all_links.update(force_include_links)
    print(f"Added {len(force_include_links)} forced include links")
    while page <= max_pages:
        url = get_next_page_url(page)
        print(f"Fetching page {page}: {url}")
        try:
            links, soup = get_links_from_page(url)
            print(f"Page {page} found {len(links)} valid links")
            if page == 1 and not links:
                print("Warning: No valid links found on the first page, please check the website structure")
                break
            if page > 1 and not links:
                print(f"Page {page} has no links, reached the last page")
                break
            all_links.update(links)
            if not has_next_page(soup, page):
                print(f"Page {page} has no next page links, stopped fetching")
                break
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"Page {page} returned 404, reached the last page")
                break
            else:
                print(f"Request for page {page} failed: {e}")
                break
        except Exception as e:
            print(f"Request for page {page} failed: {e}")
            break
        page += 1
    with open("data/data.txt", "w", encoding="utf-8") as f:
        for link in sorted(all_links):
            f.write(link + "\n")
    print(f"Total saved {len(all_links)} links to data/data.txt")
    print("\nStarting to process download links...")
    process_download_links()
    print("\nStarting to generate download center page...")
    create_main_download_page()

if __name__ == "__main__":
    main()