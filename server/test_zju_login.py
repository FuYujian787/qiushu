import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import re
import time
import json
from urllib.parse import urljoin, urlparse, parse_qs
import xml.etree.ElementTree as ET

CAS_LOGIN_URL = 'https://zjuam.zju.edu.cn/cas/login'
EDU_BASE_URL = 'https://zdbk.zju.edu.cn'
INDEX_MENU_PATH = '/jwglxt/xtgl/index_initMenu.html'

student_id = '3240104192'
password = 'zju20240157'

session = requests.Session()
session.verify = False
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
})

service_url = urljoin(EDU_BASE_URL, INDEX_MENU_PATH)

resp = session.get(CAS_LOGIN_URL, params={'service': service_url}, timeout=10)
execution = None
for pattern in [r'name="execution"\s+value="([^"]+)"', r'name=["\x27]execution["\x27]\s+value=["\x27]([^"\x27]+)["\x27]']:
    match = re.search(pattern, resp.text)
    if match:
        execution = match.group(1)
        break

resp = session.post(CAS_LOGIN_URL, data={
    'username': student_id, 'password': password,
    'execution': execution, '_eventId': 'submit',
    'geolocation': '', 'service': service_url,
}, timeout=15, allow_redirects=False)
location = resp.headers.get('Location', '')
parsed = urlparse(location)
ticket = parse_qs(parsed.query).get('ticket', [None])[0]

# Get CAS serviceValidate response
validate_url = 'https://zjuam.zju.edu.cn/cas/serviceValidate'
resp = session.get(validate_url, params={
    'service': service_url,
    'ticket': ticket,
}, timeout=10)

# Parse XML with proper encoding
resp.encoding = 'utf-8'
text = resp.text

# Try to extract fields with regex
ns = '{http://www.yale.edu/tp/cas}'
fields = {
    'user': 'user',
    'name': 'XM',
    'department': 'DWMC',
    'code': 'CODE',
    'user_type': 'YHLX',
    'dept_code': 'DWH',
    'major_code': 'ZYDM',
    'class_name': 'BJ',
    'grade': 'NJ',
    'gender': 'XB',
}

for key, tag in fields.items():
    value = re.search(rf'<{ns}{tag}>(.*?)</{ns}{tag}>', text)
    if value:
        val = value.group(1)
        print(f'{key}: {val}')

# Try to properly decode the Chinese text
print('\n--- Raw bytes ---')
xm_match = re.search(r'<cas:XM>(.*?)</cas:XM>', text)
if xm_match:
    raw = xm_match.group(1)
    print(f'XM raw: {raw}')
    print(f'XM hex: {raw.encode("latin-1").hex()}')
    try:
        decoded = raw.encode('latin-1').decode('utf-8')
        print(f'XM decoded: {decoded}')
    except:
        pass

dw_match = re.search(r'<cas:DWMC>(.*?)</cas:DWMC>', text)
if dw_match:
    raw = dw_match.group(1)
    print(f'DWMC raw: {raw}')
    print(f'DWMC hex: {raw.encode("latin-1").hex()}')
    try:
        decoded = raw.encode('latin-1').decode('utf-8')
        print(f'DWMC decoded: {decoded}')
    except:
        pass

session.close()