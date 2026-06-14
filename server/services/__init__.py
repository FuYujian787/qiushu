"""统一错误码体系"""
ERROR_CODES = {
    # 认证相关
    'AUTH_INVALID_CREDENTIALS': '学号或密码错误',
    'AUTH_WEAK_PASSWORD': '密码强度不足，需包含大小写字母+数字+特殊字符且不少于8位',
    'AUTH_EMAIL_INVALID': '邮箱格式不正确',
    'AUTH_PHONE_INVALID': '手机号格式不正确',
    'AUTH_DUPLICATE_USER': '该用户已注册',
    'AUTH_TOKEN_EXPIRED': '登录已过期，请重新登录',
    'AUTH_TOKEN_INVALID': '无效的登录凭证',
    'AUTH_TOKEN_MISSING': '请先登录',
    'AUTH_PERMISSION_DENIED': '权限不足',
    'AUTH_CAS_CAPTCHA': 'CAS 登录需要验证码，请在浏览器中先登录一次浙大通行证',
    'AUTH_CAS_LOCKED': 'CAS 账号已被临时锁定，请稍后重试',
    'AUTH_CAS_UNAVAILABLE': 'CAS 认证服务暂时不可用',
    'AUTH_CAS_ERROR': 'CAS 认证失败',
    'AUTH_CAS_TIMEOUT': 'CAS 认证超时，请稍后重试',

    # 资源相关
    'BOOK_NOT_FOUND': '书籍不存在或已下架',
    'BOOK_PERMISSION_DENIED': '只能操作自己发布的书籍',
    'ORDER_NOT_FOUND': '订单不存在',
    'ORDER_STATUS_INVALID': '当前订单状态不允许此操作',
    'USER_NOT_FOUND': '用户不存在',

    # 上传相关
    'UPLOAD_SIZE_EXCEEDED': '图片大小不能超过 2MB',
    'UPLOAD_FORMAT_INVALID': '仅支持 JPG、PNG、WebP 格式图片',
}
