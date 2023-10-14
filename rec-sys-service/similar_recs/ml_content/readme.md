## Project Structure

```
.
├── ...
├── configs/                  # Python configs to run training
├── examples/                 # Example scripts to get understanding how to use ml lib
├── content_based             # Python package with ML functionality 
│   ├── encoders              # Encoder classes
│   ├── feature_extractors    # Feature extractor classes
│   └── trainers              # Training loop classes
|   └── utils                 # Utils
└── train.py                  # Script to run training
```

## How to install

All ml-related logic is incorporated into python package `ml_content`, to install it in a dev mode, run

```
cd ml_recsys/content_based
pip install -r requirements.txt
pip install -e .
```

## How to run

To run training
```
cd ml_recsys/content_based
python train.py --config configs/basic_ae
```

See `examples/inference.py` to get understandning how to use `ml_content` package for inference.

## Training

![Screenshot 2023-07-18 at 3 05 50 PM](https://github.com/kitkat52/graduate_work/assets/23639048/137529a1-eb0c-480e-84a3-aeb1aec18879)


## Results

```
Movie: Star Trek IV: The Voyage Home. Recommened movies:
	1)  Star Trek VI: The Undiscovered Country
	2)  Star Trek: Insurrection
	3)  Star Wars: Knights of the Old Republic
	4)  Star Trek: Deep Space Nine

Movie: Five Star Final. Recommened movies:
	1)  The Star
	2)  Brightest Star
	3)  Lucky Star
	4)  Star Slammer

Movie: Star Trek: Legacy. Recommened movies:
	1)  Star Trek: Deep Space Nine
	2)  Rogue One: A Star Wars Story
	3)  Star Trek: Insurrection
	4)  Star Trek IV: The Voyage Home

Movie: The Star Chamber. Recommened movies:
	1)  Cloud Capped Star
	2)  Pop Star Puppy
	3)  My Lucky Star
	4)  2-Star

Movie: HGTV Design Star. Recommened movies:
	1)  Porn Star Zombies
	2)  Bad Girls All Star Battle
	3)  Star Portraits with Rolf Harris
	4)  The Making of a Rock Star
```

## Config management

The `config-as-code` approach is used. We define all training parameters and atomic components in the python config in `configs` directory which is later is loaded by python as a separate module.
