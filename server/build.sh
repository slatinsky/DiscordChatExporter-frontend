cd preprocess
python3 main.py
cd ..
http-server ./static --port 21011 -c-1 --silent -P "http://127.0.0.1:21011?"