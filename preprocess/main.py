from Preprocess import Preprocess
import helpers

if helpers.is_compiled():
    print('Running compiled version of preprocess.py')

else:
    print('Running uncompiled version of preprocess.py')


def main():
    p = Preprocess('../static/input/')
    p.process()


if __name__ == '__main__':
    main()
