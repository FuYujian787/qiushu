// server.js
const express = require('express');
const axios = require('axios');
const forge = require('node-forge');
const { CookieJar } = require('tough-cookie');

const app = express();
app.use(express.json());
app.use(express.static('public'));

// ---------- 工具函数 ----------
async function getCookieHeader(jar, url) {
  const cookies = await jar.getCookies(url);
  return cookies.map(c => c.cookieString()).join('; ');
}

async function saveCookies(jar, url, response) {
  const setCookieHeaders = response.headers['set-cookie'];
  if (setCookieHeaders) {
    const headers = Array.isArray(setCookieHeaders) ? setCookieHeaders : [setCookieHeaders];
    for (const cookieStr of headers) {
      try {
        await jar.setCookie(cookieStr, url);
      } catch (e) { /* 忽略无效 cookie */ }
    }
  }
}

function createClient(jar) {
  const instance = axios.create({
    timeout: 30000,
    maxRedirects: 0,
    validateStatus: () => true,
  });

  instance.interceptors.request.use(async (config) => {
    if (!config.headers['Cookie']) {
      try {
        const cookieStr = await getCookieHeader(jar, config.url);
        if (cookieStr) {
          config.headers['Cookie'] = cookieStr;
        }
      } catch (e) {}
    }
    return config;
  });

  instance.interceptors.response.use(async (response) => {
    try {
      await saveCookies(jar, response.config.url, response);
    } catch (e) {}
    return response;
  });

  return instance;
}

// ============= RSA 加密（模拟 ZJU 前端 security.js 的 encryptedString） =============

/**
 * 模拟 ZJU 前端的 RSAUtils.encryptedString
 * 
 * ZJU 前端加密逻辑（来自 security.js）：
 * 1. 将密码字符串反转
 * 2. 转为 charCode 数组
 * 3. 填充到 chunkSize 的整数倍（chunkSize = 2 * biHighIndex(modulus)）
 * 4. 每 2 个字节组成一个 16-bit digit（小端序：digits[j] = a[k] + (a[k+1] << 8)）
 * 5. 使用模幂加密（BigInteger.modPow）
 * 6. 输出十六进制字符串（空格分隔），biToHex 从高索引到低索引输出
 */
function zjuRSAEncrypt(password, modulusHex, exponentHex) {
  // 1. 反转密码（ZJU 前端逻辑）
  const reversedPwd = password.split('').reverse().join('');

  // 2. 转为 charCode 数组
  const a = [];
  for (let i = 0; i < reversedPwd.length; i++) {
    a.push(reversedPwd.charCodeAt(i));
  }

  // 3. 构建 RSA key
  const m = new forge.jsbn.BigInteger(modulusHex, 16);
  const e = new forge.jsbn.BigInteger(exponentHex, 16);

  // chunkSize = 2 * biHighIndex(m) = 2 * (ceil(bitLength/16) - 1)
  const chunkSize = 2 * (Math.ceil(m.bitLength() / 16) - 1);

  // 4. 填充到 chunkSize 的整数倍
  while (a.length % chunkSize !== 0) {
    a.push(0);
  }

  // 5. 分块加密
  let result = '';
  for (let i = 0; i < a.length; i += chunkSize) {
    let blockHex = '';
    for (let k = i + chunkSize - 2; k >= i; k -= 2) {
      const val = a[k] + ((a[k + 1] || 0) << 8);
      blockHex += val.toString(16).padStart(4, '0');
    }
    const block = new forge.jsbn.BigInteger(blockHex || '0', 16);
    const crypt = block.modPow(e, m);
    result += crypt.toString(16) + ' ';
  }

  return result.substring(0, result.length - 1);
}

// ============= 浙大通行证验证 + 获取学生信息 =============
app.post('/api/zju-verify', async (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.status(400).json({ success: false, message: '学号和密码不能为空' });
  }

  try {
    const cookieJar = new CookieJar();
    const client = createClient(cookieJar);

    // --- 步骤1~5：CAS 登录 ---
    console.log('=== ZJU Verify: 步骤1 获取 CAS execution ===');
    const casGetResp = await client.get('https://zjuam.zju.edu.cn/cas/login');
    const html = casGetResp.data;
    const execution = (html.match(/name="execution" value="([^"]+)"/) || [])[1];
    if (!execution) throw new Error('无法获取 execution');

    console.log('=== 步骤2 获取 RSA 公钥 ===');
    const pubKeyResp = await client.get('https://zjuam.zju.edu.cn/cas/v2/getPubKey');
    const { modulus, exponent } = pubKeyResp.data;
    if (!modulus || !exponent) throw new Error('无法获取 RSA 公钥');

    console.log('=== 步骤3 RSA 加密密码 ===');
    const pwdEnc = zjuRSAEncrypt(password, modulus, exponent);

    console.log('=== 步骤4 提交 CAS 登录 ===');
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', pwdEnc);
    params.append('execution', execution);
    params.append('_eventId', 'submit');
    params.append('rememberMe', 'true');

    const loginResp = await client.post(
      'https://zjuam.zju.edu.cn/cas/login',
      params.toString(),
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Referer': 'https://zjuam.zju.edu.cn/cas/login',
          'Origin': 'https://zjuam.zju.edu.cn',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
      }
    );

    // 步骤5：提取 iPlanetDirectoryPro
    let cookies = await cookieJar.getCookies('https://zjuam.zju.edu.cn');
    const iPlanetCookie = cookies.find(c => c.key === 'iPlanetDirectoryPro');
    if (!iPlanetCookie) throw new Error('学号或密码错误');
    const iPlanetDirectoryPro = iPlanetCookie.value;
    console.log('iPlanetDirectoryPro 获取成功');

    // ========== 6. SSO 登录 ZDBK ==========
    console.log('=== 步骤6: ZDBK SSO 登录 ===');

    await cookieJar.setCookie(
      `iPlanetDirectoryPro=${iPlanetDirectoryPro}; Domain=.zju.edu.cn; Path=/`,
      'https://zjuam.zju.edu.cn'
    );

    const ssoUrl = 'https://zjuam.zju.edu.cn/cas/login?service=https%3A%2F%2Fzdbk.zju.edu.cn%2Fjwglxt%2Fxtgl%2Flogin_ssologin.html';
    
    let resp = await client.get(ssoUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
      }
    });

    console.log('SSO 状态码:', resp.status);
    console.log('SSO Location:', resp.headers.location);

    // 处理重定向链，从 URL 里提取 ;jsessionid=
    let location = resp.headers.location;
    let maxRedirects = 10;
    let foundJSESSIONID = false;

    while (location && maxRedirects > 0) {
      maxRedirects--;
      
      if (location.startsWith('http://')) location = location.replace('http://', 'https://');
      if (location.startsWith('/')) location = 'https://zjuam.zju.edu.cn' + location;
      
      console.log('跟随重定向到:', location);
      
      const jsidMatch = location.match(/;jsessionid=([A-F0-9]+)/i);
      if (jsidMatch) {
        const jsid = jsidMatch[1];
        console.log('从 URL 提取到 JSESSIONID:', jsid);
        await cookieJar.setCookie(
          `JSESSIONID=${jsid}; Domain=zdbk.zju.edu.cn; Path=/`,
          'https://zdbk.zju.edu.cn'
        );
        foundJSESSIONID = true;
      }

      resp = await client.get(location, {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
      });
      
      console.log('重定向后状态码:', resp.status);
      console.log('重定向后 Location:', resp.headers.location);
      
      location = resp.headers.location;
    }

    // 如果重定向里没提取到 JSESSIONID，访问首页兜底
    if (!foundJSESSIONID) {
      let zdbkCookies = await cookieJar.getCookies('https://zdbk.zju.edu.cn/jwglxt');
      let jsessionid = zdbkCookies.find(c => c.key === 'JSESSIONID');
      if (!jsessionid) {
        console.log('尝试直接访问 ZDBK 首页...');
        resp = await client.get('https://zdbk.zju.edu.cn/jwglxt/xtgl/index_initMenu.html', {
          headers: {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://zjuam.zju.edu.cn/'
          }
        });
        
        const zdbkCookies2 = await cookieJar.getCookies('https://zdbk.zju.edu.cn/jwglxt');
        jsessionid = zdbkCookies2.find(c => c.key === 'JSESSIONID');
        if (!jsessionid) {
          throw new Error('获取教务系统 JSESSIONID 失败');
        }
      }
    }

    // 访问首页，确保拿到 route、_csrf 等
    resp = await client.get('https://zdbk.zju.edu.cn/jwglxt/xtgl/index_initMenu.html?jsdm=06&_t=' + Date.now() + '&ignoreZoom=1', {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://zjuam.zju.edu.cn/'
      }
    });

    // ========== 7. 请求个人信息页面 ==========
    console.log('=== 步骤7: 获取个人信息页面 ===');

    const infoResp = await client.post(
      `https://zdbk.zju.edu.cn/jwglxt/xtgl/yhxx_cxYhxx.html?time=${Date.now()}&gnmkdm=index&su=${username}`,
      null,
      {
        headers: {
          'Accept': 'text/html, */*; q=0.01',
          'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache',
          'X-Requested-With': 'XMLHttpRequest',
          'Referer': 'https://zdbk.zju.edu.cn/jwglxt/xtgl/index_initMenu.html?jsdm=06&_t=' + Date.now() + '&ignoreZoom=1',
          'Origin': 'https://zdbk.zju.edu.cn',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
      }
    );

    console.log('个人信息响应状态码:', infoResp.status);
    const pageHtml = infoResp.data;

    // ========== 8. 从 HTML 中解析学生信息 ==========
    console.log('=== 步骤8: 解析学生信息 ===');

    // 根据实际 HTML 结构解析：
    // <th width="14%"><b>姓名</b></th><td width="14%">傅昱坚</td>
    // <th width="14%"><b>学院</b></th><td width="14%">竺可桢学院</td>
    // <th><b>当前所在级</b></th><td>2024</td>
    // <th><b>专业名称</b></th><td></td>

    let name = '', college = '', grade = '', major = '';

    // 解析姓名：<th...><b>姓名</b></th>...<td...>值</td>
    let match = pageHtml.match(/<th[^>]*><b>姓名<\/b><\/th>\s*<td[^>]*>([^<]+)<\/td>/);
    if (match) name = match[1].trim();

    // 解析学院：<th...><b>学院</b></th>...<td...>值</td>
    match = pageHtml.match(/<th[^>]*><b>学院<\/b><\/th>\s*<td[^>]*>([^<]+)<\/td>/);
    if (match) college = match[1].trim();

    // 解析当前所在级（年级）：<th...><b>当前所在级</b></th>...<td>值</td>
    match = pageHtml.match(/<th[^>]*><b>当前所在级<\/b><\/th>\s*<td[^>]*>([^<]+)<\/td>/);
    if (match) {
      const gradeYear = match[1].trim();
      // 将 "2024" 转换为 "2024级"
      grade = gradeYear + '级';
    }

    // 解析专业名称：<th...><b>专业名称</b></th>...<td>值</td>
    match = pageHtml.match(/<th[^>]*><b>专业名称<\/b><\/th>\s*<td[^>]*>([^<]*)<\/td>/);
    if (match) major = match[1].trim();

    console.log(`解析结果 -> 姓名:${name}, 学院:${college}, 年级:${grade}, 专业:${major}`);
    
    if (!name) {
      throw new Error('未能从个人信息页面解析到姓名，页面结构可能已变化');
    }

    res.json({
      success: true,
      student: {
        name: name,
        college: college || '未设置',
        grade: grade || '大一',
        major: major || '未设置'
      }
    });

  } catch (error) {
    console.error('验证失败:', error.message);
    console.error('错误堆栈:', error.stack);
    res.status(500).json({ success: false, message: error.message });
  }
});

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`后端服务已启动：http://localhost:${PORT}`);
});
