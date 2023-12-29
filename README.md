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

data loader script를 실행 시켜야 하므로, package와 dependency를 설치한다
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
