# Setting up a development environment on Windows

## Prerequisites
- Python 3.11
- Node.js 18.17.1
- pyinstaller 5.5 (installed globally from `pip`)
- nodemon (installed globally from `npm`)
- wt (windows terminal)

## Install dependencies

Install frontend dependencies:
```bash
cd frontend
npm install
cd ..
```

Install backend dependencies:
```bash
cd backend/preprocess
py -m pip install -r requirements.txt
cd ../..
```

```bash
cd backend/fastapi
py -m pip install -r requirements.txt
pip install uvicorn==0.20.0
cd ../..
```

```bash
cd backend/windows-runner
py -m pip install -r requirements.txt
cd ../..
```

## Start the development script

run `DEV.bat`

