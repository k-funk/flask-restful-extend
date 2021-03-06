# -*- coding: utf-8 -*-
from flask.ext import restful


class ErrorHandledApi(restful.Api):
    def handle_error(self, e):
        """
        解决报错信息不会被输出到客户端的问题

        python 标准的 exception 格式为：
            message: error message

        werkzeug 的 HTTPException (包括 BadRequest 等)的格式为：
            code: http code
            name: str(e) 时输出的字符串
            description: error message

        flask_restful.abort (包括 flask_restful.reqparse.Argument.handle_validation_error) 抛出的格式为：
        (详情见 test/api_exceptions.py)
            code: http code
            description: predefined error message for this http code
            data: ｛
            　　　　message: error message
            ｝

        flask_restful 的 handle_error 函数支持的格式为：
            code: http code
            data: ｛
            　　　　message: error message
            ｝

        此函数能把 werkzeug 的 HTTPException 和带 code 属性的标准 python exception 以及其他包含 message 属性的 python exception
        改写成 flask_restful 能识别的形式
        """
        if not hasattr(e, 'data'):
            if hasattr(e, 'description'):
                e.data = dict(message=e.description)
            elif hasattr(e, 'message'):
                if not hasattr(e, 'code'):
                    e.code = 500
                e.data = dict(message=e.message)
        return super(ErrorHandledApi, self).handle_error(e)

    def unauthorized(self, response):
        """对于未授权的请求，只返回 403，不弹出登录对话框"""
        return response