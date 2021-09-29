# 这是一个示例 Python 脚本。

# 按 Ctrl+F5 执行或将其替换为您的代码。
# 按 双击 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。
from loguru import logger
from util.log import Loggings
from util.customer_decorators import except_output

loggings = Loggings()


def case_log():
    loggings.info("测试分级-info")
    loggings.debug("测试分级-debug")
    loggings.warning("测试分级-warning")
    loggings.error("测试分级-error")

    # logger.info('If you are using Python {}, prefer {feature} of course!', 3.6, feature='f-strings')
    # n1 = "cool"
    # n2 = [1, 2, 3]
    # logger.info(f'If you are using Python {n1}, prefer {n2} of course!')


@except_output('异常')
def case_excetion():
    raise Exception('测试异常')


def print_hi(name):
    # 在下面的代码行中使用断点来调试脚本。
    print(f'Hi, {name}')  # 按 F9 切换断点。


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    case_log()
    # case_excetion()

    print_hi('PyCharm')

# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
