from typing import List


class StationTreeMidModel:
    """
        + 22-09-08 海洋站树形节点数据 model
    """

    def __init__(self, id: int, name: str, code: str, is_abs: bool, sort: int, children):
        self.id = id
        self.name = name
        self.code = code
        self.is_abs = is_abs
        self.sort = sort
        self.children = children
