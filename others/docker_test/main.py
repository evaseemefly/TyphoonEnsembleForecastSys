import pathlib


# 这是一个示例 Python 脚本。

# 按 Ctrl+F5 执行或将其替换为您的代码。
# 按 Double Shift 在所有地方搜索类、文件、工具窗口、操作和设置。

def todo_docker_shared_dir(dir: str):
    '''
        测试一下 docker 与 宿主机的共享目录
    :return:
    '''
    # 在 docker 中将 /my_data 与宿主机的 E:/01data/01docker-data/99shared-data 进行映射
    target_path = pathlib.Path(dir)
    for file_temp in target_path.iterdir():
        print(file_temp)
    pass


def print_hi(name):
    # 在下面的代码行中使用断点来调试脚本。
    print(f'Hi, {name}')  # 按 F9 切换断点。
    todo_docker_shared_dir('/my_shared_data')


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    print_hi('PyCharm')

# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
