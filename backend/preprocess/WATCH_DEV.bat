pushd "%~dp0"
nodemon --exec py --ext py --ignore "temp/" "main.py" "../../exports/" "temp/"