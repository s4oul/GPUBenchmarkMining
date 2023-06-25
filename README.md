[![forthebadge](https://forthebadge.com/images/badges/built-by-developers.svg)](https://forthebadge.com)
[![forthebadge](https://forthebadge.com/images/badges/built-with-love.svg)](https://forthebadge.com)
[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com)

# Install
[![forthebadge](https://forthebadge.com/images/badges/works-on-my-machine.svg)](https://forthebadge.com)
```sh
pip3 install --upgrade pip setuptools wheel
pip3 install -r requirements.txt
```

# Run
```sh
python3 main.py
```

# Benchmark


## NVIDIA
---
OS: `LINUX`<br>
Algo: `KAWPOW`<br>
GPU: `NVIDIA RTX 3060`<br>
Duration: `10 minutes`<br>
Command: `main.exe --no_show_mining_output --mining_duration=10`<br>
Share found:
| T-REX | PICKMINER | BZMINER | SRBMINER | GMINER |
| :---: | :-------: | :-----: | :------: | :----: |
|   10  |   10      |   5     |   7      |  11    |
---
OS: `WINDOWS`<br>
Algo: `KAWPOW`<br>
GPU: `RTX 3060` + `GTX 1070`<br>
Duration: `20 minutes`<br>
Command: `main.exe --no_show_mining_output --mining_duration=20`<br>
Share found:
| T-REX | PICKMINER | BZMINER | SRBMINER | GMINER |
| :---: | :-------: | :-----: | :------: | :----: |
|   52  |   40      |   18    |   0      |  35    |

During this test `SRBMINER` does not work.
```
Detecting GPU devices...
[2023-06-23 13:05:50] Error CL_UNKNOWN_ERROR when getting number of OpenCL platforms
GPU mining disabled, issues with OpenCL
No devices available to mine with
```

## AMD
