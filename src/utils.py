import re
from bs4 import BeautifulSoup
from tempfile import gettempdir
from pathlib import Path
import requests
import traceback
import logging

import src.constants as constants
from src.log import CustomFormatter

# create logger with 'spam_application'
logger = logging.getLogger("APK DOWNLOADER")
logger.setLevel(logging.DEBUG)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

ch.setFormatter(CustomFormatter())
logger.addHandler(ch)


def strict_package_check(user_input):
    """Strict package name check."""
    pat = re.compile(r'^\w+\.*[\w\.\$]+$')
    resp = re.match(pat, user_input)
    if not resp:
        logger.error('Invalid package/class name')
    return resp

def try_provider(package, provider, domain):
    """Try using a provider."""
    downloaded_file = None
    data = None
    apk_name = f'{package}.apk'
    temp_file = f"{constants.DESTINATION_PATH}/{apk_name}"
    #temp_file = Path(gettempdir() + "/Downloads") / apk_name
    link = find_apk_link(provider, domain)
    if link:
        downloaded_file = download_file(link, temp_file)
    if downloaded_file:
        logger.info("success file downloaded")
        return download_file
    return None

def download_file(url, outfile):
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' 
            'AppleWebKit/537.36 (KHTML, like Gecko)' 
            'Chrome/105.0.0.0 Safari/537.36 OPR/91.0.4516.95'
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/39.0.2171.95 Safari/537.36'),
        'Accept-Encoding': 'deflate, gzip'}
    try:
        logger.debug('Downloading APK...')
        with requests.get(url, stream=True, headers=headers) as r:
            r.raise_for_status()
            with open(outfile, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return outfile
    except Exception:
        pass
    return None

def apk_download_list(filename):
    with open(filename, 'r') as f:
        for line in f:
            apk_download(line.replace("\n", ""))

def apk_download(package):
    """Download APK."""
    downloaded_file = None
    data = None
    try:
        if not strict_package_check(package):
            return None
        logger.warning('Attempting to download: %s', package)
        # APKPURE
        data = try_provider(
            package,
            constants.APKPURE.format(package),
            'apkpure.com')
        if data:
            return data
        # APKTADA
        data = try_provider(
            package,
            f'{constants.APKTADA}{package}',
            'apktada.com')
        if data:
            return data
        # APKPLZ
        data = try_provider(
            package,
            f'{constants.APKPLZ}{package}',
            'apkplz.net')
        if data:
            return data
        logger.debug('Unable to find download link for %s', package)
        return None
    except Exception:
        traceback.print_exc()
        logger.debug('Failed to download the apk')

        return None
    finally:
        if downloaded_file:
            downloaded_file.unlink()

def find_apk_link(url, domain):
    """Find APK download link."""
    try:
        logger.debug('Looking for download link form %s', domain)
        bsp = fetch_html(url)
        if not bsp:
            logger.error("couldn't fetch url")
            return None
        if(domain == "apkpure.com"):
            link = bsp.find('a', class_="download-start-btn", href=True)
        else:
            link = bsp.find('a', href=True, string='click here')
        if link:
            logger.debug('Download link found from %s', domain)
            t = link['href']
            logger.debug(f'apk pure link : {t}')
            return link['href']
        logger.error('Download link not found in %s', domain)
    except Exception:
        logger.error('Failed to obtain download link from %s', domain)
    return None


def fetch_html(url):
    """Get Result HTML."""
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' 
            'AppleWebKit/537.36 (KHTML, like Gecko)' 
            'Chrome/105.0.0.0 Safari/537.36 OPR/91.0.4516.95'
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/39.0.2171.95 Safari/537.36'),
        'Accept-Encoding': 'deflate, gzip'}
    try:
        res = requests.get(url,
                           headers=headers,
                           stream=True)
        if res.status_code == 200:
            return BeautifulSoup(res.text, features='lxml')
    except Exception:
        pass
    return None