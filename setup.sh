pyinstaller --onefile main.py &&
 mv dist gpu_benchmark_mining &&
 cp jobs -rf gpu_benchmark_mining/ &&
 cp miners.json gpu_benchmark_mining/ &&
 tar czvf gpu_benchmark_mining.tar.gz gpu_benchmark_mining &&
 rm -rf gpu_benchmark_mining &&
 rm main.spec