# Worker for find similar moveis id
***
### Description:
The worker independently downloads all available records from the **embedded** database and starts the process of generating recommendations for each object. The results are saved in the process of work in a separate database under the conditional name **SimilarMovies**
***
### Before using:
1. Check config in `docker-compose.yaml`
2. Save embeddings in **DB_embeddings**

***

### Run:
`python main.py`

or

`docker compose build`\
`docker compose up`
***

### Data format in DB:
####DB_embeddings (MongoDB):

```
[
    {
        "id": "UUID",
        "emb": [
            -28662626.35017638,
            -59580826.46745331,
            29172404.67239903,
            -9706568.260395601,
            -11725121.706544265,
            ...
        ]
    },
    ...
]
```

####DB_similar (Redis):
```
[
    {
        key: "UUID",
        value: [
            "UUID",
            "UUID",
            ....
        ]
    },
    ...
] 
```

***