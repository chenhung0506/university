# Customized document

## Initial enviroment
pip install -r ./customized/module/requirements.txt

## Git struct
```
.
├── README.md
├── docker
│   ├── Dockerfile
│   ├── build.sh
│   ├── dev.env
│   ├── docker-compose.yaml
│   ├── run.sh
│   └── test.env
├── imgs
│   └── customized-b24bfb9-20201030190120.tar.gz
├── logs
└── module
    ├── const.py
    ├── controller.py
    ├── dao.py
    ├── data_for_KG
    ├── log.py
    ├── logs
    ├── requirements.txt
    ├── resource
    ├── server.py
    ├── service.py
    └── utils.py
```

## Deploy with run.sh
### step1:  customized*.tar.gz file
```gherkin=
tar zxvf customized-kgi-b785119-20201026.tar.gz
```
### step2: load image, and get image $tag
```gherkin=
docker load -i customized/imgs/customized-b785119-20201026193411.tar.gz
```
### step3: execute run.sh
```gherkin=
./customized/docker/run.sh 3
```
### step4: enter $tag
```gherkin=
Enter TAG: b785119
```

## Deploy with docker-compose.yaml

```gherkin=
export ENV=dev.env TAG=529d578 PORT=8330 && \
docker-compose up   
```

## Deploy with docker run
```gherkin=
export ENV=dev.env TAG=529d578 PORT=8330 && \
docker run -d --name customized -v ~/volumes/customized:/usr/src/app/logs -v ~/.ssh/known_hosts:/root/.ssh/known_hosts -v ~/etc/timezone:/etc/localtime:ro -m 5125m --restart always --net docker-compose-base_default -e TZ=Asia/Taipei -p ${PORT}:${PORT} --env-file ${ENV} chenhung0506/customized:${TAG}
```