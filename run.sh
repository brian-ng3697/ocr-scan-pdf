# For docker execution
. venv/bin/activate
gunicorn -w 4 main:app -k uvicorn.workers.UvicornWorker