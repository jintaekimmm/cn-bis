# cn-bis

지역 버스 정류장, 버스 노선 정보 등을 활용하여 이용자에게 관련 정보를 제공한다

## Tech Stack

- poetry
- Python 3.11
- FastAPI
- MySQL 8.0.27

## Architecture
![architecture](https://github.com/jintaekimmm/cn-bis/assets/31076511/a84b1ce2-7f31-4bcf-87d0-affe1a48752e)


## Virtual Environment

이 프로젝트는 [poetry](https://python-poetry.org/docs/)를 사용하여 package와 dependency를 관리한다

- [poetry install](https://python-poetry.org/docs/#installation)

data loader script를 실행 시켜야 하므로, virtual environment 환경에서 package와 dependency를 설치한다
```shell
# package and dependencies install
$ poetry install
```


## Local Environment Running

### .env.example

.env.local 파일을 아래 예와 같이 작성하여 `project` 디렉터리 하위에 저장한다

`project/.env.local `

```shell
# DATABASE
DB_HOST=x.x.x.x
DB_PORT=3306
DB_NAME=bis
DB_USER=example
DB_PASSWORD=example
```

### running docker compose

docker compose를 실행하여 서비스를 동작시킨다

```shell
# running usage docker compose
$ docker compose -p cn-bis -f docker/docker-compose.local.yaml --env-file ./project/.env.local up -d --build

# read running logs
$ docker compose -p cn-bis -f docker/docker-compose.local.yaml --env-file ./project/.env.local logs -f
```

### data load

API에서 사용하는 데이터는 다음과 같다
- [서울시 버스 운행 노선 정보(서울 열린 데이터 광장)](https://data.seoul.go.kr/dataList/OA-1095/F/1/datasetView.do)
- [전국 버스 정류장 위치 정보(공공 데이터 포털)](https://www.data.go.kr/data/15067528/fileData.do)

두 데이터를 탐색 및 전처리하여 load 할 수 있는 데이터로 만들어두었다. 행정구 데이터의 경우에는 모든 지역을 처리하지 않고, '서울'의 '구' 지역만 사용하였다
- [cn-bis-preprocess: 정류장 및 운행 노선 데이터 탐색 및 전처리](https://github.com/jintaekimmm/cn-bis-preprocess/blob/main/bus/bus.ipynb)
- [cn-bis-preprocess: 행정구 데이터 전처리](https://github.com/jintaekimmm/cn-bis-preprocess/blob/main/geo/address.ipynb)


서비스 실행 후, data를 database에 load 시킨다

```shell
data load를 위해서는 .env.local 파일에 DB_HOST로 로컬 PC가 접속할 수 있어야 한다
만약 .env.local 파일에 docker compose links로 연결하여 'DB_HOST=db' 와 같이 되어있다면, loader script를 실행할 때에는
'DB_HOST=' 에는 로컬 PC가 접속할 수 있는 주소(IP)를 설정하고 실행해야 한다
````

load 되는 데이터 종류는

 - bus station 정보
 - bus route 정보
 - 행정구 위치(Polygon) 정보

```shell
$ export PYTHONPATH=${PWD}/project
$ export ENV=local;
$ python project/script/loader.py
```

## API Docs

Swagger를 통해 API를 호출할 수 있다

```shell
Swagger URL : http://localhost:8000/docs
```
