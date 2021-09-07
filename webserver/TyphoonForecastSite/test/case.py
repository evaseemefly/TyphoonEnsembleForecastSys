# from task.tasks import my_task
from celery import Celery

celery: Celery = Celery()


def main():
    # my_task.delay("")
    # celery.send_task("rename_debug_test")
    task_name = 'surge_group_ty'
    params_obj = {'name': '123', 'age': 12}
    celery.send_task(task_name, args=[params_obj, '123', 19], kwargs={'age': 10})
    pass


if __name__ == '__main__':
    main()
