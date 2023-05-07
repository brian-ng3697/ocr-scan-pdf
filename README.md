## Setup
- Requires Python 3.8
- Run `pip install -r direct-requirements.txt`
- Do not overwrite `direct-requirements.txt` by `pip freeze`
- Run OPA: 
    - with docker `docker run -it --rm -p 8181:8181 openpolicyagent/opa run --server --addr :8181` or 
    - or by command `opa run --server` (require install OPA first)

## Run Local
- uvicorn main:app --host 0.0.0.0 --port 8000 --reload

## Run Local jobs 
- rq worker --with-scheduler