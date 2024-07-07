front:
    npm run dev

back:
    poetry run uvicorn justfiles:app --reload --port 5566

install:
    poetry install
    npm install


build:
    rm -fr dist
    npm run build
    poetry build
    cp ./node_modules/vue-picocss/css/pico.min.css dist/assets/

deploy: build
    scp -r dist/* gate.vpn:/srv/files/

