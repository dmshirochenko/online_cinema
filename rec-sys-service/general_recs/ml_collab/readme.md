## Project Info

Minimal implementation of ALS collaborative filtering algorithm implemented by Apache Spark [link](https://spark.apache.org/docs/2.2.0/ml-collaborative-filtering.html). The routine is to load the matrix `[user_id, item_id, rating` and feed it into ALS algorithm. Upon training, make top K recommendations for all existing users and save it as pandas DataFrame.

__Project Structure__
```
.
├── ...
├── ml_collab                 # Python package with ML functionality 
│   ├── data_loaders          # Data loaders classes
│   └── models                # RecSys models classes
└── train.py                  # Script to run training and inference
```

__Used ALS configuration__
```
max_iter: 5
reg_param: 0.09
rank: 25
cold_start_strategy: drop 
```

## How to install

All ml-related logic is incorporated into python package `ml_collab`, to install it in a dev mode, run

```
cd ml_recsys/collaborative_based
pip install -e .
```

## How to run

To run training and inference example
```
cd ml_recsys/collaborative_based
python train.py
```

To get dataset userd in example `MusicalInstrumentsDataLoader` use:
```
curl http://snap.stanford.edu/data/amazon/productGraph/categoryFiles/reviews_Musical_Instruments_5.json.gz --output Musical_Instruments_5.json.gz
```

# Future Features
- [ ] Config management
- [ ] Batched inference
