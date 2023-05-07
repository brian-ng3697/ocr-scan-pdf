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

## Run Apache Solr (file: docker-compose-solr.yml)
- docker-compose up -d

## Full-text search engine SRCHX (https://github.com/alash3al/srchx)
- Installation:
    1. Goto Releases Page
    2. Choose your platform based version
    3. Download it
    4. Copy/Rename it as ./srchx
    5. Run chmod +x ./srchx
- Run: 
    ./srchx -engine leveldb
- Help Info:
    1. Run ./srchx --help to see help info
        -engine string
            the engine to be used as a backend (default "boltdb")
        -listen string
                the restful server listen address (default ":2050")
        -storage string
                the storage path (default "data")
        -testdata test/fake
                this will generate a test/fake collection with fake data just for testing
        -workers int
                number of workers to be used (default 4)