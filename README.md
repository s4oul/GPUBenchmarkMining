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
* `NV`: Not Verifiable, take hasrate from prompt software
* `SOON`: Did not tested actually

Protocol utilisé : `mining_edtude_fr.md`

## NVIDIA

`NVIDIA RTX 3070`

___KAWPOW___

| Software | T-REX | PICKMINER | BZMINER | GMINER | NBMINER | SRBMINER | LOLMINER | RIGEL |
|:--------:|:-----:|:---------:|:-------:|:------:|:-------:|:--------:|:--------:|:-----:|
|   MH/S   | 25.52 |   25.57   |  20.89  | 24.48  |  22.94  |    22    |    US    | 25.62 |


___AUTOLYKOS V2___

| Software | T-REX  | PICKMINER |  BZMINER  | GMINER | NBMINER | SRBMINER | LOLMINER |
|:--------:|:------:|:---------:|:---------:|:------:|:-------:|:--------:|:--------:|
|   MH/S   | 143.75 |  132.34   | 43.66(NV) | 143.32 | 142.43  |  65.74   |   SOON   |


___ETHASH___

| Software | T-REX | PICKMINER | BZMINER | GMINER | NBMINER | SRBMINER | LOLMINER |
|:--------:|:-----:|:---------:|:-------:|:------:|:-------:|:--------:|:--------:|
|   MH/S   | 49.70 |   45.78   |   KO    | 51.41  |  SOON   |   SOON   |    KO    |


___ETCHASH___

| Software | T-REX | PICKMINER | BZMINER | GMINER | NBMINER | SRBMINER | LOLMINER | ETCMINER |
|:--------:|:-----:|:---------:|:-------:|:------:|:-------:|:--------:|:--------:|:--------:|
|   MH/S   | 51.39 |   46.75   |  SOON   | 51.44  |  SOON   |   SOON   |   SOON   |  49.67   |

## AMD

`AMD RX 5700`

___KAWPOW___

| Software | TEAMREDMINER | PICKMINER | BZMINER | GMINER | NBMINER | SRBMINER  |
|:--------:|:------------:|:---------:|:-------:|:------:|:-------:|:---------:|
|   MH/S   |  24.73(NV)   |   18.81   |   KO    | 17.32  |  16.33  | 18.09(NV) |

___AUTOLYKOS V2___

| Software | TEAMREDMINER | PICKMINER |  BZMINER  | GMINER | NBMINER  |  SRBMINER  | LOLMINER |
|:--------:|:------------:|:---------:|:---------:|:------:|:--------:|:----------:|:--------:|
|   MH/S   |     99.1     |   80.87   | 43.68(NV) |   US   |  102.34  | 101.28(NV) |  97.33   |


___ETHASH___

| Software | TEAMREDMINER | PICKMINER | BZMINER | GMINER | NBMINER | SRBMINER | LOLMINER |
|:--------:|:------------:|:---------:|:-------:|:------:|:-------:|:--------:|:--------:|
|   MH/S   |      KO      |   45.48   |   KO    |  50.1  |  SOON   |   SOON   |  48.78   |


___ETCHASH___

| Software | TEAMREDMINER | PICKMINER | BZMINER | GMINER | NBMINER | SRBMINER | LOLMINER | ETCMINER |
|:--------:|:------------:|:---------:|:-------:|:------:|:-------:|:--------:|:--------:|:--------:|
|   MH/S   |     SOON     |   SOON    |  SOON   |  SOON  |  SOON   |   SOON   |   SOON   |   SOON   |