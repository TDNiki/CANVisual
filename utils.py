update_interval = 0.1  # Интервал обновления по умолчанию в секундах

def set_update_interval(value=None):
    global update_interval
    if value is not None:
        update_interval = float(value)
    return update_interval
