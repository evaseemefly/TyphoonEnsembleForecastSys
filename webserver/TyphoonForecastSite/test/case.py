from others.tasks import my_task


def main():
    my_task.delay("")
    pass


if __name__ == '__main__':
    main()
