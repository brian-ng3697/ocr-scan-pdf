FROM python:3.8.13-slim
WORKDIR /usr/src/app
RUN apt update && apt install --fix-broken -y \
        build-essential \
        make \
        gcc \
        tk ffmpeg libgl1 libsm6 libxext6 libmagic1 git

# Required original library
RUN apt install -y \
        tesseract-ocr-all \
        imagemagick

COPY . .
RUN pip install -r direct-requirements.txt
RUN apt clean && apt autoremove && rm -rf /var/lib/apt/lists/*

EXPOSE 8000
CMD ["gunicorn", "-w", "4", "main:app", "-k", "uvicorn.workers.UvicornWorker"]