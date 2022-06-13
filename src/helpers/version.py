import os


def get_version():
    f = open(os.path.join(
        '/'.join(os.path.realpath(__file__).split('/')[:-2]), 'data.json'))

    return f.read()
