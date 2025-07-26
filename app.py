import os
import re
import requests
import json
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
    r'acrobat[- ]?classic', r'character[- ]?animator' 
]
year_pattern = r'(20(1[9]|2[0-6]))'  # 2019-2026
product_year_regex = re.compile(
    r'(' + '|'.join(adobe_patterns) + r')[\w\-]*' + year_pattern,
    re.IGNORECASE
)

# 新增：匹配没有年份的Adobe产品链接
adobe_product_regex = re.compile(
    r'(' + '|'.join(adobe_patterns) + r')[\w\-]*',
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

def parse_date(date_str):
    """Parse date string to datetime object"""
    if not date_str:
        return None
    try:
        # 处理常见的日期格式
        date_formats = [
            "%B %d, %Y",  # July 19, 2025
            "%b %d, %Y",   # Jul 19, 2025
            "%d %B %Y",    # 19 July 2025
            "%Y-%m-%d",    # 2025-07-19
            "%m/%d/%Y",    # 07/19/2025
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        # 如果标准格式都失败，尝试更宽松的解析
        return datetime.strptime(date_str.strip(), "%B %d, %Y")
    except:
        return None

def extract_list_page_date(soup, url):
    """Extract publication date from list page"""
    # 查找包含该链接的文章
    for article in soup.find_all("article"):
        link_elem = article.find("a", href=url)
        if link_elem:
            # 查找该文章中的post_date
            post_date_div = article.find("div", class_="post_date")
            if post_date_div:
                date_text = post_date_div.get_text(strip=True)
                return parse_date(date_text)
    return None

def extract_detail_page_date(soup):
    """Extract publication date from detail page"""
    # 查找insidepost_date
    date_div = soup.find("div", class_="insidepost_date")
    if date_div:
        date_text = date_div.get_text(strip=True)
        # 提取日期部分（去掉链接部分）
        if " - " in date_text:
            date_text = date_text.split(" - ")[0]
        return parse_date(date_text)
    return None

def load_processed_links():
    """Load previously processed links and their dates"""
    processed_file = "data/processed_links.json"
    if os.path.exists(processed_file):
        try:
            with open(processed_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_processed_links(processed_links):
    """Save processed links and their dates"""
    processed_file = "data/processed_links.json"
    os.makedirs("data", exist_ok=True)
    with open(processed_file, 'w', encoding='utf-8') as f:
        json.dump(processed_links, f, indent=2, default=str)

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
    # 检查是否有年份的产品链接
    if product_year_regex.search(href):
        return True
    # 检查没有年份的Adobe产品链接
    if adobe_product_regex.search(href):
        return True
    return False

def get_links_from_page(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    links = set()
    link_dates = {}  # 存储链接和对应的日期
    
    for a in soup.find_all("a", href=True):
        try:
            href = a["href"]
            if is_valid_adobe_link(href):
                links.add(href)
                # 提取列表页日期
                list_date = extract_list_page_date(soup, href)
                if list_date:
                    link_dates[href] = list_date
        except (KeyError, TypeError):
            continue
    return links, soup, link_dates

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

def extract_page_info(soup):
    """Extract software image and description from the page"""
    image_url = ""
    description = ""
    
    # Find image in post_img div
    post_img_div = soup.find("div", class_="post_img")
    if post_img_div:
        img_tag = post_img_div.find("img")
        if img_tag and img_tag.get("src"):
            image_url = str(img_tag["src"])
    
    # Find description in the first p tag after post_img div
    if post_img_div:
        next_p = post_img_div.find_next_sibling("p")
        if next_p:
            description = next_p.get_text(strip=True)
    
    return image_url, description

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

def create_download_html(download_url, version_info="", install_mode="", software_name="Download Link", image_url="", description=""):
    """Create HTML content for download page"""
    # 先拼好图片HTML，避免f-string嵌套冲突
    img_html = (
        f"<img src='{image_url}' alt='{software_name}' />"
        if image_url else
        ""
    )
    js_script = ''
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Download Link</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}
        .header {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 30px 0;
            text-align: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }}
        .header h1 {{
            color: white;
            font-size: 2.5em;
            margin: 0;
            font-weight: 300;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }}
        .main-content {{
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 40px 20px;
        }}
        .software-card {{
            background: white;
            border-radius: 25px;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
            overflow: hidden;
            max-width: 600px;
            width: 100%;
            text-align: center;
        }}
        .software-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 50px 40px;
            text-align: center;
        }}
        .software-image {{
            width: 120px;
            height: 120px;
            border-radius: 25px;
            overflow: hidden;
            box-shadow: 0 15px 35px rgba(0,0,0,0.3);
            margin: 0 auto 30px;
            background: white;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .software-image img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        .software-name {{
            font-size: 36px;
            font-weight: 700;
            margin-bottom: 20px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            line-height: 1.2;
        }}
        .software-description {{
            font-size: 18px;
            opacity: 0.9;
            line-height: 1.6;
            max-width: 500px;
            margin: 0 auto;
        }}
        .software-body {{
            padding: 50px 40px;
            text-align: center;
        }}
        .info-section {{
            margin-bottom: 40px;
            display: flex;
            gap: 20px;
            justify-content: center;
        }}
        .info-item {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 25px;
            border-radius: 15px;
            border: 1px solid #e9ecef;
            text-align: center;
            flex: 1;
            max-width: 250px;
        }}
        .info-item h3 {{
            color: #495057;
            font-size: 14px;
            font-weight: 600;
            margin: 0 0 10px 0;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .info-item p {{
            color: #2c3e50;
            font-size: 20px;
            font-weight: 600;
            margin: 0;
        }}
        .download-section {{
            text-align: center;
            padding: 40px;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 20px;
            border: 2px solid #e9ecef;
        }}
        .download-btn {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 22px 60px;
            text-decoration: none;
            border-radius: 50px;
            font-size: 22px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 12px 35px rgba(102, 126, 234, 0.3);
            min-width: 280px;
            position: relative;
            overflow: hidden;
        }}
        .download-btn::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }}
        .download-btn:hover::before {{
            left: 100%;
        }}
        .download-btn:hover {{
            transform: translateY(-5px);
            box-shadow: 0 18px 45px rgba(102, 126, 234, 0.4);
            color: white;
            text-decoration: none;
        }}
        .placeholder-image {{
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 35px;
        }}

        .footer {{
            text-align: center;
            padding: 30px;
            color: rgba(255, 255, 255, 0.8);
            font-size: 14px;
        }}
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 2em;
            }}
            .software-header {{
                padding: 40px 30px;
            }}
            .software-name {{
                font-size: 28px;
            }}
            .software-body {{
                padding: 40px 30px;
            }}
            .download-btn {{
                padding: 20px 50px;
                font-size: 20px;
                min-width: 250px;
            }}
        }}
    </style>
    {js_script}
</head>
<body>
    <div class="header">
        <h1>Software Download</h1>
    </div>
    
    <div class="main-content">
        <div class="software-card">
            <div class="software-header">
                {f'''
                <div class="software-image">
                    {img_html}
                </div>
                ''' if image_url else ''}
                <div class="software-name">{software_name}</div>
                {f'<div class="software-description">{description}</div>' if description else ''}
            </div>
            
            <div class="software-body">
                <div class="info-section">
                    {f'''
                    <div class="info-item">
                        <h3>Version</h3>
                        <p>{version_info}</p>
                    </div>
                    ''' if version_info else ''}
                    {f'''
                    <div class="info-item">
                        <h3>Install Mode</h3>
                        <p>{install_mode}</p>
                    </div>
                    ''' if install_mode else ''}
                </div>
                
                <div class="download-section">
                    <a href="{download_url}" class="download-btn" target="_blank">
                        Download Now
                    </a>
                </div>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>© 2025 Adobe GenP Downloads | Professional software for creative professionals</p>
    </div>
</body>
</html>"""
    return html_content

def load_list_page_dates():
    """Load list page dates from link_dates.json"""
    dates_file = "data/link_dates.json"
    if os.path.exists(dates_file):
        try:
            with open(dates_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def process_download_links():
    """Process all links in data.txt with date comparison"""
    data_file = "data/data.txt"
    if not os.path.exists(data_file):
        print(f"Error: File not found {data_file}")
        return
    
    # 加载已处理的链接和列表页日期
    processed_links = load_processed_links()
    list_page_dates = load_list_page_dates()
    print(f"Loaded {len(processed_links)} previously processed links")
    print(f"Loaded {len(list_page_dates)} list page dates")
    
    with open(data_file, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    print(f"Starting to process {len(urls)} links...")
    updated_count = 0
    skipped_count = 0
    
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
            
            # 提取详情页日期
            detail_date = extract_detail_page_date(soup)
            if detail_date:
                print(f"  Detail page date: {detail_date.strftime('%Y-%m-%d')}")
            
            # 获取列表页日期
            list_date = None
            if url in list_page_dates:
                list_date = parse_date(list_page_dates[url])
                if list_date:
                    print(f"  List page date: {list_date.strftime('%Y-%m-%d')}")
            
            # 检查是否需要更新（比较日期）
            should_update = True
            if url in processed_links:
                last_processed_date = processed_links[url].get('detail_date')
                if last_processed_date:
                    last_date = parse_date(last_processed_date)
                    if last_date and detail_date:
                        if detail_date <= last_date:
                            print(f"  Skip: Detail page date ({detail_date.strftime('%Y-%m-%d')}) is not newer than last processed ({last_date.strftime('%Y-%m-%d')})")
                            should_update = False
                            skipped_count += 1
            
            # 如果详情页日期比列表页日期新，则更新
            if list_date and detail_date and detail_date > list_date:
                print(f"  Update: Detail page date ({detail_date.strftime('%Y-%m-%d')}) is newer than list page date ({list_date.strftime('%Y-%m-%d')})")
                should_update = True
            
            if not should_update:
                continue
            
            # Extract page info (image and description)
            image_url, description = extract_page_info(soup)
            if image_url:
                print(f"  Found software image: {image_url}")
            if description:
                print(f"  Found software description: {description[:100]}...")
            
            download_links = find_download_links(soup)
            print(f"  Found {len(download_links)} download links")
            
            if not download_links:
                default_html = create_download_html("", "", "", software_name, image_url, description)
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
                    html_content = create_download_html(download_url, version_info, install_mode, software_name, image_url, description)
                    file_path = os.path.join(folder_path, filename)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    print(f"  Saved download page: {filename} -> {download_url}")
                    if version_info:
                        print(f"    Version info: {version_info}")
                    if install_mode:
                        print(f"    Install mode: {install_mode}")
            
            # 保存处理信息
            processed_links[url] = {
                'detail_date': detail_date.strftime('%Y-%m-%d') if detail_date else None,
                'processed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'folder_name': folder_name,
                'software_name': software_name
            }
            updated_count += 1
            
        except Exception as e:
            print(f"  Error: {e}")
            continue
    
    # 保存更新后的处理信息
    save_processed_links(processed_links)
    print(f"\nProcessing completed!")
    print(f"Updated: {updated_count} links")
    print(f"Skipped: {skipped_count} links")
    print(f"Total processed: {len(processed_links)} links")

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
                            # 修复version-info提取逻辑，匹配分开的Version和Install Mode
                            version_match = re.search(r'<h3>Version</h3>\s*<p>([^<]+)</p>', content)
                            version_info = version_match.group(1) if version_match else ""
                            
                            install_match = re.search(r'<h3>Install Mode</h3>\s*<p>([^<]+)</p>', content)
                            install_mode = install_match.group(1) if install_match else ""
                            
                            # Extract image URL and description
                            image_url = ""
                            description = ""
                            img_match = re.search(r'<img src="([^"]+)"', content)
                            if img_match:
                                image_url = img_match.group(1)
                            desc_match = re.search(r'<div class="software-description">([^<]+)</div>', content)
                            if desc_match:
                                description = desc_match.group(1)
                            
                            download_files.append({
                                'file_name': html_file,
                                'download_url': download_url,
                                'version_info': version_info,
                                'install_mode': install_mode,
                                'image_url': image_url,
                                'description': description
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
            align-items: center;
            gap: 15px;
            margin-bottom: 20px;
        }}
        .software-icon {{
            width: 60px;
            height: 60px;
            border-radius: 10px;
            overflow: hidden;
            flex-shrink: 0;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .software-icon img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        .software-icon .placeholder {{
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 20px;
        }}
        .software-info {{
            flex: 1;
        }}
        .software-name {{
            font-size: 1.3em;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 5px;
        }}
        .software-description {{
            font-size: 0.9em;
            color: #6c757d;
            line-height: 1.4;
            margin-bottom: 8px;
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
    <script>
        function filterSoftware() {{
            const input = document.getElementById('searchInput');
            const grid = document.getElementById('downloadGrid');
            const noResults = document.getElementById('noResults');
            const filter = input.value.toLowerCase();
            const cards = grid.getElementsByClassName('download-card');
            let visibleCount = 0;
            
            for (let card of cards) {{
                const searchData = card.getAttribute('data-search');
                if (searchData && searchData.includes(filter)) {{
                    card.style.display = 'block';
                    visibleCount++;
                }} else {{
                    card.style.display = 'none';
                }}
            }}
            
            if (visibleCount === 0) {{
                noResults.style.display = 'block';
            }} else {{
                noResults.style.display = 'none';
            }}
        }}
    </script>
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
        
        # Get the first file's image and description for the card
        first_file = item['files'][0] if item['files'] else {}
        image_url = first_file.get('image_url', '')
        description = first_file.get('description', '')
        
        # 收集所有版本信息和简介用于搜索
        all_version_info = []
        all_descriptions = []
        for file_info in item['files']:
            version_text = f"{file_info.get('version_info', '')} {file_info.get('install_mode', '')}".strip()
            if version_text:
                all_version_info.append(version_text)
            if file_info.get('description'):
                all_descriptions.append(file_info.get('description'))
        
        # 合并搜索数据
        search_data = f"{item['name'].lower()} {' '.join(all_version_info)} {' '.join(all_descriptions)}".lower()
        
        html_content += f"""
                <div class="download-card" data-name="{item['name'].lower()}" data-search="{search_data}">
                    <div class="card-header">
                        {f'''
                        <div class="software-icon">
                            <img src="{image_url}" alt="{item["name"]}">
                        </div>
                        ''' if image_url else ''}
                        <div class="software-info">
                            <div class="software-name">{item['name']}</div>
                            {f'<div class="software-description">{description[:100]}{"..." if len(description) > 100 else ""}</div>' if description else ''}
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
                                Download
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
    all_link_dates = {}  # 存储所有链接的日期信息
    page = 1
    max_pages = 50
    all_links.update(force_include_links)
    print(f"Added {len(force_include_links)} forced include links")
    
    while page <= max_pages:
        url = get_next_page_url(page)
        print(f"Fetching page {page}: {url}")
        try:
            links, soup, link_dates = get_links_from_page(url)
            print(f"Page {page} found {len(links)} valid links")
            
            # 合并链接和日期信息
            all_links.update(links)
            all_link_dates.update(link_dates)
            
            if page == 1 and not links:
                print("Warning: No valid links found on the first page, please check the website structure")
                break
            if page > 1 and not links:
                print(f"Page {page} has no links, reached the last page")
                break
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
    
    # 保存链接和日期信息
    with open("data/data.txt", "w", encoding="utf-8") as f:
        for link in sorted(all_links):
            f.write(link + "\n")
    
    # 保存日期信息到单独的文件
    with open("data/link_dates.json", "w", encoding="utf-8") as f:
        # 转换datetime对象为字符串
        dates_dict = {}
        for link, date in all_link_dates.items():
            if date:
                dates_dict[link] = date.strftime('%Y-%m-%d')
        json.dump(dates_dict, f, indent=2)
    
    print(f"Total saved {len(all_links)} links to data/data.txt")
    print(f"Saved {len(all_link_dates)} link dates to data/link_dates.json")
    print("\nStarting to process download links...")
    process_download_links()
    print("\nStarting to generate download center page...")
    create_main_download_page()

if __name__ == "__main__":
    main()