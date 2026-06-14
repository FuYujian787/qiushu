"""Probe ZDBK course (xsxjc) and textbook APIs — discover working endpoints

The target page is: /jwglxt/xsxjc/xsxjc_cxXsxjcIndex.html?gnmkdm=N253535&layout=default&su=3240104192

This script systematically probes course-related APIs that the xsxjc page would call.
"""
import sys, os, json, re, ssl, logging
sys.path.insert(0, os.path.dirname(__file__))
import requests
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
from urllib.parse import unquote

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s',
                    datefmt='%H:%M:%S', stream=sys.stderr)
logger = logging.getLogger('zdbk-probe')

class _EduTLSSAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        ctx.set_ciphers('DEFAULT:@SECLEVEL=1')
        kwargs['ssl_context'] = ctx
        return super().init_poolmanager(*args, **kwargs)

CAS_LOGIN_URL = 'https://zjuam.zju.edu.cn/cas/login'
CAS_PUBKEY_URL = 'https://zjuam.zju.edu.cn/cas/v2/getPubKey'
STUDENT_ID = '3240104192'
PASSWORD = 'zju20240157'

def rsa_encrypt(plaintext, modulus, exponent, modulus_hex_len):
    pwd_bytes = plaintext.encode('utf-8')
    pwd_hex = pwd_bytes.hex()
    pwd_int = int(pwd_hex, 16)
    encrypted_int = pow(pwd_int, exponent, modulus)
    return hex(encrypted_int)[2:].zfill(modulus_hex_len)

def try_json(resp):
    try: return resp.json()
    except: return None

def save_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f'  -> Saved to {filename}')

def main():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    })
    session.mount('https://', _EduTLSSAdapter())

    # === Step 1: CAS Login ===
    print('\n=== Step 1: CAS Login ===')
    resp = session.get(CAS_LOGIN_URL, allow_redirects=False, timeout=15)
    match = re.search(r'name="execution" value="(.*?)"', resp.text)
    execution = match.group(1)
    resp = session.get(CAS_PUBKEY_URL, timeout=15)
    pubkey = resp.json()
    modulus = int(pubkey['modulus'], 16)
    exponent = int(pubkey['exponent'], 16)
    encrypted_pwd = rsa_encrypt(PASSWORD, modulus, exponent, len(pubkey['modulus']))
    resp = session.post(CAS_LOGIN_URL,
        data={'username': STUDENT_ID, 'password': encrypted_pwd, 'authcode': '',
              'execution': execution, '_eventId': 'submit', 'rememberMe': 'true'},
        headers={'Referer': CAS_LOGIN_URL}, allow_redirects=False, timeout=15)
    sso_cookie = resp.cookies.get('iPlanetDirectoryPro')
    if not sso_cookie:
        print(f'[FAIL] Login failed: {(resp.text or "")[:300]}')
        return
    print(f'[OK] CAS login success, SSO={sso_cookie[:40]}...')

    raw_cookie = unquote(sso_cookie)
    for d in ['zdbk.zju.edu.cn', 'zju.edu.cn']:
        session.cookies.set('iPlanetDirectoryPro', raw_cookie, domain=d, path='/')

    # === Step 2: ZDBK SSO Login ===
    print('\n=== Step 2: ZDBK SSO ===')
    service_url = f'{CAS_LOGIN_URL}?service=https%3A%2F%2Fzdbk.zju.edu.cn%2Fjwglxt%2Fxtgl%2Flogin_ssologin.html'
    resp = session.get(service_url, allow_redirects=True, timeout=15)
    jsessionid = resp.cookies.get('JSESSIONID')
    if not jsessionid:
        m = re.search(r';jsessionid=([A-Fa-f0-9]+)', resp.url)
        if m: jsessionid = m.group(1)
    route = resp.cookies.get('route', '')
    print(f'[OK] JSESSIONID={jsessionid[:30] if jsessionid else "None"}..., route={route}')

    if not jsessionid:
        print('[FAIL] No JSESSIONID')
        return

    # === Step 3: Probe xsxjc (student course selection) APIs ===
    print('\n=== Step 3: Probe XSXJC (Course Selection) APIs ===')

    xsxjc_probes = [
        # Course selection main page (the one user mentioned)
        ('GET', '/jwglxt/xsxjc/xsxjc_cxXsxjcIndex.html', {'gnmkdm': 'N253535', 'layout': 'default', 'su': STUDENT_ID}),
        # Course listing
        ('POST', '/jwglxt/xsxjc/xsxjc_cxXsxjcList.html', {'xnm': '', 'xqm': ''}),
        ('POST', '/jwglxt/xsxjc/xsxjc_cxXsxjcList.html', {'xnm': '2025', 'xqm': '3'}),
        ('POST', '/jwglxt/xsxjc/xsxjc_cxXsxjcList.html', {'xnm': '2025', 'xqm': '12'}),
        ('POST', '/jwglxt/xsxjc/xsxjc_cxXsxjcList.html', {}),
        # Course selection with different gnmkdm
        ('POST', '/jwglxt/xsxjc/xsxjc_cxXsxjcList.html', {'gnmkdm': 'N253535', 'xnm': '', 'xqm': ''}),
        # Textbook info related to courses
        ('GET', '/jwglxt/xsxjc/xsxjc_cxXsxjcIndex.html', {}),
        # Alternative xsxjc endpoints
        ('POST', '/jwglxt/xsxjc/xsxjc_cxJcsqList.html', {}),
        ('POST', '/jwglxt/xsxjc/xsxjc_cxKbxxList.html', {}),
        # Course details
        ('POST', '/jwglxt/xsxjc/xsxjc_cxXskbList.html', {}),
        # Book info
        ('POST', '/jwglxt/xsxjc/xsxjc_cxJcxxList.html', {}),
        # Selected courses
        ('POST', '/jwglxt/xsxjc/xsxjc_cxYxXkList.html', {}),
    ]

    for method, path, params in xsxjc_probes:
        name = path.split('/')[-1].replace('.html','')
        if jsessionid:
            url = f'https://zdbk.zju.edu.cn{path};jsessionid={jsessionid}'
        else:
            url = f'https://zdbk.zju.edu.cn{path}'

        try:
            if method == 'GET':
                resp = session.get(url, params=params, cookies={'route': route},
                    headers={'Referer': 'https://zdbk.zju.edu.cn/jwglxt/xtgl/index_initMenu.html'},
                    timeout=15)
            else:
                resp = session.post(url, data=params, cookies={'route': route},
                    headers={
                        'Referer': f'https://zdbk.zju.edu.cn/jwglxt/xsxjc/xsxjc_cxXsxjcIndex.html?gnmkdm=N253535&layout=default&su={STUDENT_ID}',
                        'X-Requested-With': 'XMLHttpRequest',
                        'Content-Type': 'application/x-www-form-urlencoded',
                    }, timeout=15)

            data = try_json(resp)
            if data and (isinstance(data, dict) and data) or (isinstance(data, list) and data):
                if isinstance(data, dict):
                    keys = list(data.keys())
                    print(f'  [OK] {name:35s} -> JSON | keys: {keys}')
                    save_json(f'test_zdbk_{name}.json', data)
                elif isinstance(data, list):
                    print(f'  [OK] {name:35s} -> JSON list[{len(data)}]')
                    save_json(f'test_zdbk_{name}.json', data[:3])
            elif resp.status_code == 200:
                text = resp.text or ''
                size = len(text)
                kw = [k for k in ['jc','教材','课本','书籍','book','课程','course','班级','class'] if k in text]
                print(f'  [--] {name:35s} -> HTTP 200 non-JSON({size}B)' + (f' | keywords: {kw}' if kw else ''))
                if kw or size < 500:
                    snippet = text[:300].replace('\n',' ').replace('\r','')
                    print(f'       {snippet}')
            elif resp.status_code == 404:
                pass  # skip 404 spam
            elif resp.status_code in (302, 301):
                print(f'  [REDIRECT] {name:35s} -> HTTP {resp.status_code}')
            elif resp.status_code >= 500:
                print(f'  [ERR] {name:35s} -> HTTP {resp.status_code}')
            else:
                ct = resp.headers.get('Content-Type','')
                print(f'  [???] {name:35s} -> HTTP {resp.status_code} | {ct}')
        except Exception as e:
            err = str(e)[:80]
            if '404' not in err:
                print(f'  [EXC] {name:35s} -> {err}')

    # === Step 4: Probe textbook/jcxx specific APIs ===
    print('\n=== Step 4: Probe Textbook APIs ===')
    textbook_probes = [
        ('POST', '/jwglxt/jcxx/jcxx_cxJcList.html', {'xnm': '2025', 'xqm': '3'}),
        ('POST', '/jwglxt/jcxx/jcxx_cxJcList.html', {'xnm': '2025', 'xqm': '12'}),
        ('POST', '/jwglxt/jcxx/jcxx_cxJcList.html', {}),
        ('POST', '/jwglxt/jcxx/jcxx_cxJcxxIndex.html', {}),
        ('GET', '/jwglxt/jcxx/jcxx_cxJcxxIndex.html', {}),
        # Book detail
        ('POST', '/jwglxt/jcxx/jcxx_cxJcDetail.html', {}),
        # Course-book mapping
        ('POST', '/jwglxt/jcxx/jcxx_cxKcJcList.html', {'xnm': '', 'xqm': ''}),
        ('POST', '/jwglxt/jcxx/jcxx_cxKcJcList.html', {'xnm': '2025', 'xqm': '3'}),
    ]

    for method, path, params in textbook_probes:
        name = path.split('/')[-1].replace('.html','')
        url = f'https://zdbk.zju.edu.cn{path};jsessionid={jsessionid}'
        try:
            if method == 'GET':
                resp = session.get(url, params=params, cookies={'route': route},
                    headers={'Referer': 'https://zdbk.zju.edu.cn/jwglxt/xtgl/index_initMenu.html'},
                    timeout=15)
            else:
                resp = session.post(url, data=params, cookies={'route': route},
                    headers={
                        'Referer': 'https://zdbk.zju.edu.cn/jwglxt/xtgl/index_initMenu.html',
                        'X-Requested-With': 'XMLHttpRequest',
                        'Content-Type': 'application/x-www-form-urlencoded',
                    }, timeout=15)

            data = try_json(resp)
            if data and (isinstance(data, dict) and data) or (isinstance(data, list) and data):
                if isinstance(data, dict):
                    keys = list(data.keys())
                    print(f'  [OK] {name:35s} -> JSON | keys: {keys}')
                    save_json(f'test_zdbk_{name}.json', data)
                elif isinstance(data, list):
                    print(f'  [OK] {name:35s} -> JSON list[{len(data)}]')
                    save_json(f'test_zdbk_{name}.json', data[:3])
            elif resp.status_code == 200:
                text = resp.text or ''
                size = len(text)
                print(f'  [--] {name:35s} -> HTTP 200 non-JSON({size}B)')
                if size < 500:
                    print(f'       {(text or "")[:300]}')
            elif resp.status_code == 404:
                pass
            elif resp.status_code >= 500:
                print(f'  [ERR] {name:35s} -> HTTP {resp.status_code}')
            else:
                print(f'  [???] {name:35s} -> HTTP {resp.status_code}')
        except Exception as e:
            err = str(e)[:80]
            if '404' not in err:
                print(f'  [EXC] {name:35s} -> {err}')

    # === Step 5: Probe more general API paths ===
    print('\n=== Step 5: Probe general course/pyfa APIs ===')
    general_probes = [
        # pyfa = 培养方案 (training plan)
        ('POST', '/jwglxt/pyfa/pyfa_cxCxPyfaList.html', {}),
        ('POST', '/jwglxt/pyfa/pyfa_cxXsPyfaList.html', {}),
        # kcb = 课程表
        ('POST', '/jwglxt/kbcx/xskbcx_cxXskbAllList.html', {}),
        # xk = 选课
        ('POST', '/jwglxt/xkgl/xkgl_cxXkList.html', {}),
    ]

    for method, path, params in general_probes:
        name = path.split('/')[-1].replace('.html','')
        url = f'https://zdbk.zju.edu.cn{path};jsessionid={jsessionid}'
        try:
            if method == 'GET':
                resp = session.get(url, params=params, cookies={'route': route},
                    headers={'Referer': 'https://zdbk.zju.edu.cn/jwglxt/xtgl/index_initMenu.html'},
                    timeout=15)
            else:
                resp = session.post(url, data=params, cookies={'route': route},
                    headers={
                        'Referer': 'https://zdbk.zju.edu.cn/jwglxt/xtgl/index_initMenu.html',
                        'X-Requested-With': 'XMLHttpRequest',
                        'Content-Type': 'application/x-www-form-urlencoded',
                    }, timeout=15)

            data = try_json(resp)
            if data and (isinstance(data, dict) and data) or (isinstance(data, list) and data):
                if isinstance(data, dict):
                    keys = list(data.keys())
                    print(f'  [OK] {name:35s} -> JSON | keys: {keys}')
                    save_json(f'test_zdbk_{name}.json', data)
                elif isinstance(data, list):
                    print(f'  [OK] {name:35s} -> JSON list[{len(data)}]')
                    save_json(f'test_zdbk_{name}.json', data[:5])
            elif resp.status_code == 200:
                size = len(resp.text or '')
                print(f'  [--] {name:35s} -> HTTP 200 non-JSON({size}B)')
            elif resp.status_code == 404:
                pass
            else:
                print(f'  [???] {name:35s} -> HTTP {resp.status_code}')
        except Exception as e:
            err = str(e)[:80]
            if '404' not in err:
                print(f'  [EXC] {name:35s} -> {err}')

    print('\n=== Probe complete ===')

if __name__ == '__main__':
    main()
