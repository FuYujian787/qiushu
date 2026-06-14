"""CAS Diagnostic Test Script — Probe ZJU CAS + ZDBK API Endpoints

Usage: cd server && python test_cas_diagnostic.py
Credentials: 3240104192 / zju20240157
"""
import re, ssl, sys, json, time, logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
from urllib.parse import unquote

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s',
                    datefmt='%H:%M:%S', stream=sys.stderr)
logger = logging.getLogger('cas-diag')

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

def print_json(data, label='', max_len=500):
    s = json.dumps(data, ensure_ascii=False, indent=2)[:max_len]
    print(f'      {label}: {s}')

def main():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    })
    session.mount('https://', _EduTLSSAdapter())

    # ====== STEP 1: CAS Login ======
    print('\n' + '='*70)
    print('STEP 1: CAS Login')
    print('='*70)

    try:
        resp = session.get(CAS_LOGIN_URL, allow_redirects=False, timeout=15)
        print(f'  1a. GET CAS login -> HTTP {resp.status_code}')
        match = re.search(r'name="execution" value="(.*?)"', resp.text)
        if not match:
            print('  [FAIL] Cannot extract execution token')
            return
        execution = match.group(1)
        print(f'  1a. execution: {execution[:60]}...')

        resp = session.get(CAS_PUBKEY_URL, timeout=15)
        print(f'  1b. GET pubkey -> HTTP {resp.status_code}')
        pubkey = resp.json()
        modulus_hex = pubkey['modulus']
        exponent_hex = pubkey['exponent']
        modulus = int(modulus_hex, 16)
        exponent = int(exponent_hex, 16)
        print(f'  1b. RSA: {len(modulus_hex)} hex chars ({len(modulus_hex)*4} bit), exponent={exponent_hex}')

        encrypted_pwd = rsa_encrypt(PASSWORD, modulus, exponent, len(modulus_hex))
        print(f'  1c. Encrypted password: {len(encrypted_pwd)} hex chars')

        resp = session.post(
            CAS_LOGIN_URL,
            data={
                'username': STUDENT_ID,
                'password': encrypted_pwd,
                'authcode': '',
                'execution': execution,
                '_eventId': 'submit',
                'rememberMe': 'true',
            },
            headers={'Referer': CAS_LOGIN_URL},
            allow_redirects=False,
            timeout=15,
        )
        print(f'  1c. POST CAS login -> HTTP {resp.status_code}')
        print(f'      Location: {resp.headers.get("Location", "none")[:120]}')

        sso_cookie = resp.cookies.get('iPlanetDirectoryPro')
        if not sso_cookie:
            resp_text = resp.text or ''
            if '密码错误' in resp_text:
                print('  [FAIL] Wrong password')
            elif '验证码' in resp_text:
                print('  [FAIL] CAPTCHA required')
            elif '锁定' in resp_text:
                print('  [FAIL] Account locked')
            else:
                print(f'  [FAIL] No SSO cookie. Response snippet: {resp_text[:400]}')
            return

        print(f'  [OK] CAS login success! SSO={sso_cookie[:40]}...')

        # Distribute SSO cookie to subdomains
        raw_cookie = unquote(sso_cookie)
        for domain in ['zdbk.zju.edu.cn', 'courses.zju.edu.cn', 'zju.edu.cn']:
            session.cookies.set('iPlanetDirectoryPro', raw_cookie, domain=domain, path='/')
        print(f'  1d. SSO Cookie distributed to subdomains')

    except Exception as e:
        print(f'  [FAIL] Exception: {e}')
        import traceback
        traceback.print_exc()
        return

    # ====== STEP 2: courses.zju.edu.cn API ======
    print('\n' + '='*70)
    print('STEP 2: courses.zju.edu.cn APIs')
    print('='*70)

    courses_probes = [
        ('GET', 'https://courses.zju.edu.cn/api/profile', None),
        ('GET', 'https://courses.zju.edu.cn/api/todos', None),
        ('GET', 'https://courses.zju.edu.cn/api/courses', None),
        ('GET', 'https://courses.zju.edu.cn/api/user', None),
        ('GET', 'https://courses.zju.edu.cn/api/me', None),
        ('GET', 'https://courses.zju.edu.cn/api/semesters', None),
        ('GET', 'https://courses.zju.edu.cn/api/announcements', None),
        ('GET', 'https://courses.zju.edu.cn/user/index', None),
    ]

    for method, url, extra in courses_probes:
        try:
            resp = session.get(url, timeout=10, allow_redirects=True)
            data = try_json(resp)
            if data:
                if isinstance(data, dict):
                    keys = list(data.keys())
                    print(f'  [OK] {url.split("/")[-1]:20s} -> HTTP {resp.status_code} | keys: {keys}')
                    print_json(data)
                else:
                    print(f'  [OK] {url.split("/")[-1]:20s} -> HTTP {resp.status_code} | list[{len(data)}]')
                    if data: print_json(data[0])
            else:
                ct = resp.headers.get('Content-Type','')
                size = len(resp.text or '')
                snippet = (resp.text or '')[:150].replace('\n',' ').replace('\r','')
                print(f'  [--] {url.split("/")[-1]:20s} -> HTTP {resp.status_code} | {ct}({size}B) | {snippet}')
        except Exception as e:
            print(f'  [ERR] {url.split("/")[-1]:20s} -> {e}')

    # ====== STEP 3: zdbk.zju.edu.cn SSO redirect ======
    print('\n' + '='*70)
    print('STEP 3: zdbk.zju.edu.cn SSO Redirect')
    print('='*70)

    jsessionid = None
    route = ''
    zdbk_service_url = (
        f'{CAS_LOGIN_URL}?service='
        f'https%3A%2F%2Fzdbk.zju.edu.cn%2Fjwglxt%2Fxtgl%2Flogin_ssologin.html'
    )
    try:
        resp = session.get(zdbk_service_url, allow_redirects=True, timeout=15)
        final_url = resp.url
        print(f'  Final URL: {final_url[:150]}')

        jsessionid = resp.cookies.get('JSESSIONID')
        if not jsessionid:
            m = re.search(r';jsessionid=([A-Fa-f0-9]+)', final_url)
            if m: jsessionid = m.group(1)
        if not jsessionid:
            for c in session.cookies:
                if 'JSESSION' in c.name.upper():
                    jsessionid = c.value
                    break
        route = resp.cookies.get('route', '')
        print(f'  JSESSIONID: {jsessionid[:50] if jsessionid else "[FAIL] Not found"}...')
        print(f'  route: {route}')
    except Exception as e:
        print(f'  [FAIL] Exception: {e}')

    # ====== STEP 4: ZDBK API probe ======
    print('\n' + '='*70)
    print('STEP 4: zdbk.zju.edu.cn API Probe')
    print('='*70)

    if not jsessionid:
        print('  [SKIP] No JSESSIONID')
    else:
        # 4a. Index menu page
        print('\n  4a. Fetching ZDBK index page...')
        try:
            resp = session.get(
                'https://zdbk.zju.edu.cn/jwglxt/xtgl/index_initMenu.html',
                params={'jsessionid': jsessionid},
                cookies={'route': route},
                timeout=15,
            )
            print(f'      -> HTTP {resp.status_code}, size={len(resp.text or "")}')
            if resp.status_code == 200:
                # Extract embedded API references
                api_refs = re.findall(r'["\']([^"\']*?\.(?:html|do|action)[^"\']*?)["\']', resp.text or '')
                if api_refs:
                    print(f'      Found {len(api_refs)} API references:')
                    for ref in api_refs[:30]:
                        print(f'        {ref}')
        except Exception as e:
            print(f'      [ERR] {e}')

        # 4b. Systematic probe of student info APIs
        print('\n  4b. Probing student info APIs...')

        probes = [
            # Student personal info (old paths)
            ('POST', '/jwglxt/xsxxxggl/xsgrxxwh_cxXsgrxx.html', {}),
            ('POST', '/jwglxt/xsxxxggl/xsgrxxwh_cxXsgrxx.html?gnmkdm=N100801', {}),
            ('POST', '/jwglxt/xsxxxggl/xsxxxxxx_cxXsxxxxxx.html', {}),
            ('POST', '/jwglxt/xsxxxggl/xsgrxx_cxXsgrxx.html', {}),
            ('POST', '/jwglxt/xsxxxggl/xsjbxx_cxXsjbxx.html', {}),
            # With params
            ('POST', '/jwglxt/xsxxxggl/xsgrxxwh_cxXsgrxx.html', {'xnm': '', 'xqm': ''}),
            ('POST', '/jwglxt/xsxxxggl/xsgrxxwh_cxXsgrxx.html', {'xnm': '2024', 'xqm': '3'}),
            ('POST', '/jwglxt/xsxxxggl/xsgrxxwh_cxXsgrxx.html', {'xnm': '2024', 'xqm': '12'}),
            # Menu page
            ('GET', '/jwglxt/xtgl/initMenu_json.html', None),
            ('POST', '/jwglxt/xtgl/initMenu_json.html', {}),
            # Grade query
            ('POST', '/jwglxt/cjcx/cjcx_cxDgXscj.html', {}),
            ('POST', '/jwglxt/cjcx/cjcx_cxXscj.html', {}),
            # Schedule
            ('POST', '/jwglxt/kbcx/xskbcx_cxXsKb.html', {}),
            # Alternative path formats
            ('POST', '/jwglxt/xsxxxggl/xsgrxxwh/xsgrxx_wh.html', {}),
            ('GET', '/jwglxt/xsxxxggl/xsgrxxwh/xsgrxx_wh.html', None),
            # RESTful guesses
            ('GET', '/jwglxt/api/xsxxxggl/xsgrxx', None),
            ('GET', '/jwglxt/api/student/info', None),
            # Index pages
            ('GET', '/jwglxt/xsxxxggl/xsgrxxwh_cxXsgrxxIndex.html', None),
            ('GET', '/jwglxt/xsxxxggl/xsjbxxIndex.html', None),
            # CSRF token page
            ('GET', '/jwglxt/xtgl/login_slogin.html', None),
        ]

        for method, path, body in probes:
            if body is None: body = {}
            url = f'https://zdbk.zju.edu.cn{path}'
            if jsessionid:
                if '?' in url:
                    url += f'&jsessionid={jsessionid}'
                else:
                    url += f';jsessionid={jsessionid}'

            try:
                if method == 'GET':
                    resp = session.get(url, cookies={'route': route},
                        headers={'Referer': 'https://zdbk.zju.edu.cn/jwglxt/xtgl/index_initMenu.html'},
                        timeout=10)
                else:
                    resp = session.post(url, data=body, cookies={'route': route},
                        headers={
                            'Referer': 'https://zdbk.zju.edu.cn/jwglxt/xtgl/index_initMenu.html',
                            'X-Requested-With': 'XMLHttpRequest',
                            'Content-Type': 'application/x-www-form-urlencoded',
                        }, timeout=10)

                if resp.status_code == 200:
                    data = try_json(resp)
                    if data:
                        if isinstance(data, dict):
                            keys = list(data.keys())
                            print(f'  [OK] {path.split("/")[-1][:40]:40s} -> JSON | keys: {keys}')
                            print_json(data)
                        elif isinstance(data, list) and data:
                            print(f'  [OK] {path.split("/")[-1][:40]:40s} -> JSON list[{len(data)}]')
                            print_json(data[0])
                        else:
                            print(f'  [--] {path.split("/")[-1][:40]:40s} -> JSON empty/null')
                    else:
                        text = resp.text or ''
                        size = len(text)
                        # Check for student info keywords in HTML
                        kw_found = [kw for kw in ['xh','xm','jgmc','zymc','nj','学号','姓名','专业','学院','年级'] if kw in text]
                        if kw_found:
                            print(f'  [HTML] {path.split("/")[-1][:40]:40s} -> HTML({size}B) keywords: {kw_found}')
                            for kw in kw_found[:2]:
                                idx = text.find(kw)
                                if idx >= 0:
                                    snip = text[max(0,idx-20):idx+80].replace('\n',' ').replace('\r','')[:150]
                                    print(f'         ...{snip}...')
                        elif size > 100:
                            print(f'  [--] {path.split("/")[-1][:40]:40s} -> HTML/Text({size}B)')
                elif resp.status_code == 404:
                    pass  # Skip 404 spam
                elif resp.status_code in (302, 301):
                    print(f'  [REDIRECT] {path.split("/")[-1][:40]:40s} -> {resp.status_code}')
                elif resp.status_code >= 500:
                    print(f'  [ERR] {path.split("/")[-1][:40]:40s} -> HTTP {resp.status_code}')
                else:
                    print(f'  [???] {path.split("/")[-1][:40]:40s} -> HTTP {resp.status_code}')
            except Exception as e:
                short_err = str(e)[:80]
                if '404' not in short_err:
                    print(f'  [EXC] {path.split("/")[-1][:40]:40s} -> {short_err}')

    # ====== STEP 5: Other subdomains ======
    print('\n' + '='*70)
    print('STEP 5: Other endpoints')
    print('='*70)

    other_probes = [
        ('GET', 'https://zjuam.zju.edu.cn/cas/oauth2.0/profile'),
        ('GET', 'https://zjuam.zju.edu.cn/cas/actuator/info'),
        ('GET', 'https://identity.zju.edu.cn/api/user'),
        ('GET', 'https://my.zju.edu.cn/api/user/profile'),
    ]

    for method, url in other_probes:
        try:
            resp = session.get(url, timeout=8, allow_redirects=True)
            data = try_json(resp)
            if data and isinstance(data, dict) and data:
                keys = list(data.keys())
                print(f'  [OK] {url.split("/")[-1]:20s} -> JSON | keys: {keys}')
                print_json(data)
            else:
                print(f'  [--] {url.split("/")[-1]:20s} -> HTTP {resp.status_code}')
        except Exception as e:
            print(f'  [ERR] {url.split("/")[-1]:20s} -> {e}')

    # ====== STEP 6: Summary ======
    print('\n' + '='*70)
    print('Diagnostic Complete')
    print('='*70)

if __name__ == '__main__':
    main()
