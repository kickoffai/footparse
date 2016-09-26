import os.path


DATA_ROOT = os.path.join(os.path.dirname(__file__), 'data')


def data_path(fname=None):
    if fname is not None:
        return os.path.join(DATA_ROOT, fname)
    return DATA_ROOT
