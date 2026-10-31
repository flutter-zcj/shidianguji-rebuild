"""
识典古籍模块 - 用户鉴权依赖

古籍App接口允许游客访问部分内容（如书籍详情、分类、搜索），
登录态接口通过 JWT 或 X-User-Id 头识别用户。
"""

from typing import Annotated

from fastapi import Depends, Request
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from utils.jwt_util import JwtUtil
from utils.log_util import logger


class GujiUserModel(BaseModel):
    """
    古籍业务当前用户模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    user_id: int = Field(default=0, description='用户ID（0表示游客）')
    user_name: str | None = Field(default=None, description='用户名')
    nick_name: str | None = Field(default=None, description='昵称')
    has_logged_in: bool = Field(default=False, description='是否已登录')


class GujiAuthUtil:
    """
    古籍业务鉴权工具类
    """

    @classmethod
    def resolve_user(cls, request: Request) -> GujiUserModel:
        """
        解析当前请求对应的古籍用户

        优先使用X-User-Id调试头；其次解析Authorization/token中的JWT；
        均未命中时按游客处理（user_id=0）。

        :param request: 请求对象
        :return: 古籍用户模型
        """
        debug_user_id = request.headers.get('X-User-Id')
        if debug_user_id and debug_user_id.isdigit():
            return GujiUserModel(user_id=int(debug_user_id), has_logged_in=True)

        token = request.headers.get('Authorization') or request.headers.get('token') or ''
        token = token.replace('Bearer ', '').strip()
        if not token:
            return GujiUserModel()

        # 兼容形如 guji_1001 的简易令牌，便于联调
        if token.startswith('guji_') and token[len('guji_') :].isdigit():
            user_id = int(token[len('guji_') :])
            return GujiUserModel(user_id=user_id, has_logged_in=True)

        try:
            payload = JwtUtil.decode(token)
        except Exception as exc:  # noqa: BLE001
            logger.debug(f'古籍模块令牌解析失败，按游客处理: {exc}')
            return GujiUserModel()

        user_id = payload.get('user_id') or payload.get('userId') or payload.get('sub')
        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            return GujiUserModel()
        return GujiUserModel(
            user_id=user_id,
            user_name=payload.get('user_name') or payload.get('userName'),
            nick_name=payload.get('nick_name') or payload.get('nickName'),
            has_logged_in=True,
        )


async def get_current_guji_user(request: Request) -> GujiUserModel:
    """
    获取当前古籍用户（FastAPI依赖项）

    :param request: 请求对象
    :return: 古籍用户模型
    """
    return GujiAuthUtil.resolve_user(request)


CurrentGujiUserDependency = Annotated[GujiUserModel, Depends(get_current_guji_user)]
"""
古籍模块当前用户依赖项
"""
