# main.py
import uvicorn
import multiprocessing

if __name__ == "__main__":
	multiprocessing.freeze_support()  # for windows https://stackoverflow.com/a/67590514
	uvicorn.run("src.main:app", host="0.0.0.0", port=58000, reload=False, workers=4)