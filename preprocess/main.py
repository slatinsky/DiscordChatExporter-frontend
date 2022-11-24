from Preprocess import Preprocess
import helpers




def main():
    if helpers.is_compiled():
        print('Running compiled version of preprocess.py')
        p = Preprocess('../../exports/', '../cache/')
    else:
        print('Running uncompiled version of preprocess.py')
        p = Preprocess('../releases/exports/', '../releases/dcef/cache/')
    p.process()
    print('Open http://127.0.0.1:21011/ in your browser to view GUI')


if __name__ == '__main__':
    main()
