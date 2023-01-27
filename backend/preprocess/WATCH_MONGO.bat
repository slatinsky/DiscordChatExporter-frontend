pushd "%~dp0"
nodemon --exec py --ext py --ignore "temp/" "main_mongo.py" "../../exports/" "temp/"