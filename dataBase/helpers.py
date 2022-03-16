from datetime import datetime


def fecha():
    today = datetime.now()
    todaySTR = today.strftime("%Y-%m-%d %H:%M:%S")
    return datetime.strptime(todaySTR, '%Y-%m-%d %H:%M:%S')
