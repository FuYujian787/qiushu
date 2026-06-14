"""密码、邮箱、手机号强度验证"""
import re

# 临时邮箱域名黑名单
TEMP_EMAIL_DOMAINS = {
    'mailinator.com', 'tempmail.com', '10minutemail.com', 'guerrillamail.com',
    'throwaway.email', 'sharklasers.com', 'yopmail.com', 'trashmail.com',
}


def validate_password_strength(password: str) -> tuple:
    """
    密码规则：
    - 最少 8 个字符
    - 必须包含至少 1 个大写字母
    - 必须包含至少 1 个小写字母
    - 必须包含至少 1 个数字
    - 必须包含至少 1 个特殊字符 (!@#$%^&*)
    """
    if len(password) < 8:
        return False, '密码长度不能少于 8 位'
    if not re.search(r'[A-Z]', password):
        return False, '密码必须包含至少一个大写字母'
    if not re.search(r'[a-z]', password):
        return False, '密码必须包含至少一个小写字母'
    if not re.search(r'[0-9]', password):
        return False, '密码必须包含至少一个数字'
    if not re.search(r'[!@#$%^&*]', password):
        return False, '密码必须包含至少一个特殊字符 (!@#$%^&*)'
    return True, '密码强度合格'


def validate_email(email: str) -> tuple:
    """验证邮箱格式并检查临时邮箱黑名单"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, '邮箱格式不正确，请输入有效的邮箱地址'
    domain = email.split('@')[1].lower()
    if domain in TEMP_EMAIL_DOMAINS:
        return False, '请使用有效的个人邮箱，不支持临时邮箱'
    return True, ''


def validate_phone(phone: str) -> tuple:
    """验证中国大陆手机号"""
    if not re.match(r'^1[3-9]\d{9}$', phone):
        return False, '手机号格式不正确，请输入 11 位中国大陆手机号'
    return True, ''
