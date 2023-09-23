# Install
```sh
pip3 install --upgrade pip setuptools wheel
pip3 install -r requirements.txt
```

# Run
```sh
python3 main.py
```

# Benchmark
* `KO`: Problem during the mining
* `US`: Unsupported

Protocol utilisé : `mining_edtude_fr.md`

## NVIDIA

___KAWPOW___

| Software | T-REX | PICKMINER | BZMINER | GMINER | NBMINER | SRBMINER |
|:--------:|:-----:|:---------:|:-------:|:------:|:-------:|:--------:|
|   MH/S   | 25.43 |   25.49   |  20.89  | 24.48  |  22.94  |    22    |


___AUTOLYKOS V2___

| Software | T-REX  | PICKMINER | BZMINER | GMINER | NBMINER | SRBMINER |
|:--------:|:------:|:---------:|:-------:|:------:|:-------:|:--------:|
|   MH/S   | 143.75 |  132.34   |  SOON   | 143.32 | 142.43  |  65.74   |


___ETHASH___

| Software | T-REX | PICKMINER | BZMINER | GMINER | NBMINER | SRBMINER | LOLMINER |
|:--------:|:-----:|:---------:|:-------:|:------:|:-------:|:--------:|:--------:|
|   MH/S   | 49.70 |   45.78   |  SOON   | 51.41  |  SOON   |   SOON   |   SOON   |


___ETCHASH___

| Software | T-REX | PICKMINER | BZMINER | GMINER | NBMINER | SRBMINER | ETCMINER | LOLMINER |
|:--------:|:-----:|:---------:|:-------:|:------:|:-------:|:--------:|:--------:|:--------:|
|   MH/S   | 51.39 |   46.75   |  SOON   | 51.44  |  SOON   |   SOON   |  49.67   |   SOON   |

## AMD

___KAWPOW___

| Software | TEAMREDMINER | PICKMINER | BZMINER | GMINER | NBMINER | SRBMINER |
|:--------:|:------------:|:---------:|:-------:|:------:|:-------:|:--------:|
|   MH/S   |     SOON     |   18.47   |  SOON   | 17.28  |  SOON   |  17.98   |

___AUTOLYKOS V2___

| Software | TEAMREDMINER | PICKMINER | BZMINER | GMINER | NBMINER | SRBMINER | LOLMINER |
|:--------:|:------------:|:---------:|:-------:|:------:|:-------:|:--------:|:--------:|
|   MH/S   |    101.00    |   80.59   |  SOON   |   KO   |  SOON   |  98.50   |  97.57   |

*GMINER : `ASUS AMD Radeon RX 5700 8GB [0000:05:00.0]: Device not supported for this algorithm`<br>


___ETHASH___

| Software | TEAMREDMINER | PICKMINER | BZMINER | GMINER | NBMINER | SRBMINER | LOLMINER |
|:--------:|:------------:|:---------:|:-------:|:------:|:-------:|:--------:|:--------:|
|   MH/S   |     SOON     |   SOON    |  SOON   |  50.1  |  SOON   |   SOON   |  48.78   |


___ETCHASH___

| Software | TEAMREDMINER | PICKMINER | BZMINER | GMINER | NBMINER | SRBMINER | ETCMINER | LOLMINER |
|:--------:|:------------:|:---------:|:-------:|:------:|:-------:|:--------:|:--------:|:--------:|
|   MH/S   |     SOON     |   SOON    |  SOON   |  SOON  |  SOON   |   SOON   |   SOON   |   SOON   |