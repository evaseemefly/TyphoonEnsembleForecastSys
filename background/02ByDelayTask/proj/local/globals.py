import threading
from common.const import UNLESS_ID_STR

local_celery = threading.local()


def get_celery():
    """
        获取 线程唯一的 celery对象 可以访问 global_celery_id
    @return:
    """
    # local_celery = CeleryData()
    celery = CeleryData()
    return celery


class CeleryData:
    def __init__(self):
        # self._global_celery = threading.local()
        self._local_celery = local_celery
        # self._local_celery.celery_id = UNLESS_ID_STR
        # self._global_celery_id: str = UNLESS_ID_STR

    # def get_global_celery_id(self):
    #     return self._global_celery.celery_id
    #
    # def set_global_celery_id(self, value: str):
    #     if self._global_celery.celery_id == UNLESS_ID_STR:
    #         self._global_celery.celery_id = value

    # global_celery_id = property(get_global_celery_id, set_global_celery_id)

    @property
    def celery_id(self):
        if hasattr(self._local_celery, 'celery_id'):
            return self._local_celery.celery_id
        else:
            return UNLESS_ID_STR

    @celery_id.setter
    def celery_id(self, value: str):
        """

        @param value:
        @param cover: 是否强制覆盖 celery_id
        @return:
        """
        # TODO:[-] 21-11-27 注意此处赋值去掉了限制
        self._local_celery.celery_id = value
        # if cover:
        #     self._local_celery.celery_id = value
        # elif not hasattr(self._local_celery, 'celery_id'):

        # if self._local_celery.celery_id == UNLESS_ID_STR:
        #     self._local_celery.celery_id = value

# global_celery_id: str = UNLESS_ID_STR
