import os
import sys
from Preprocess import Preprocess
import helpers


# if command line argument is not given, print usage





def main(input_dir, output_dir):
    p = Preprocess(input_dir, output_dir)
    p.process()
    if helpers.is_compiled():
        print('Open http://127.0.0.1:21011/ in your browser to view GUI')



if __name__ == '__main__':
    if helpers.is_compiled():
        print('Running compiled version of preprocess.py')
    else:
        print('Running uncompiled version of preprocess.py')
    if len(sys.argv) < 3:
        print('Usage: python preprocess.py [path_to_exports] [cache_dir]')
    else:
        input_dir = sys.argv[1]
        output_dir = sys.argv[2]
        main(input_dir, output_dir)