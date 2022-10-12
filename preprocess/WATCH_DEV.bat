pushd "%~dp0"
nodemon --exec py --ext py --ignore "temp/" "preprocess.py"