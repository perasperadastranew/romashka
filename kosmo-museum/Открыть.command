#!/bin/bash
# Двойной клик на Mac: поднимает локальный сервер и открывает презентацию в браузере.
cd "$(dirname "$0")"
PORT=8765
( sleep 1; open "http://localhost:$PORT/" ) &
echo "Музей в кармане: http://localhost:$PORT/  (закрыть — Ctrl+C или закрыть окно)"
python3 -m http.server $PORT
