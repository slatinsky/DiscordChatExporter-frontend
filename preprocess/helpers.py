import os

def is_compiled():
    if os.path.exists(__file__):
        return False
    elif os.path.exists('preprocess.exe'):
        return True
    else:
        raise Exception('Cannot determine if compiled or not')

def pad_id(id):
    return str(id).zfill(24)
    # return str(id).rjust(24, '0')