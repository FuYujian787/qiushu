"""AI 对话助手上下文管理"""
from models import UserCourse, Course


def get_user_context(user_id: str) -> str:
    """获取用户上下文信息（课程、专业等）"""
    try:
        user = __import__('models', fromlist=['User']).User.query.get(user_id)
        if not user:
            return ''

        context_parts = []
        if user.major:
            context_parts.append(f'专业: {user.major}')
        if user.college:
            context_parts.append(f'学院: {user.college}')
        if user.grade:
            context_parts.append(f'年级: {user.grade}')

        # 获取用户课程
        user_courses = UserCourse.query.filter_by(user_id=user_id).all()
        if user_courses:
            course_names = []
            for uc in user_courses:
                course = Course.query.get(uc.course_id)
                if course:
                    course_names.append(course.name)
            if course_names:
                context_parts.append(f'课程: {", ".join(course_names)}')

        return '；'.join(context_parts) if context_parts else ''
    except Exception:
        return ''
