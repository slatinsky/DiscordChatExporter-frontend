from Preprocess import Preprocess
import helpers

if helpers.is_compiled():
    print('Running compiled version of preprocess.py')

else:
    print('Running uncompiled version of preprocess.py')


def main():
    p = Preprocess('../static/input/')
    p.process()
    print('Open http://127.0.0.1:21011/ in your browser to view GUI')


if __name__ == '__main__':
    main()
