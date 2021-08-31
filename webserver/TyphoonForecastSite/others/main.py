# from others.tasks import app
from others.my_celery import app

if __name__ == '__main__':
    app.start()
