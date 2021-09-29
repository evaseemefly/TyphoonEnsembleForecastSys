class IBaseError(Exception):
    def __init__(self, message, *args, **kwargs):
        self.message = message
        pass


class NoneError(Exception):
    """
        查询结果为None的错误
    """

    def __init__(self, message, *args, **kwargs):
        self.message = message
        pass


class QueryNoneError(NoneError):
    """
        空查询错误
    """

    def __init__(self, message=None, *args, **kwargs):
        customer_message: str = '查询结果为空' if message is None else message
        super(QueryNoneError, self).__init__(customer_message, *args, **kwargs)

    pass


class CalculateTimeOutError(IBaseError):
    """
        计算时间超时
    """
    def __init__(self, message=None, *args, **kwargs):
        customer_message: str = '超出计算时间约束' if message is None else message
        super(CalculateTimeOutError, self).__init__(customer_message, *args, **kwargs)

    pass