#!/bin/bash

if [ -f .env ]; then
  set -o allexport
  source .env
  set +o allexport
else
  echo ".env file is not found!"
  exit 1
fi

mkdir -p "$PWD/logs"
ngrok http "$TELEGRAM_BOT_PORT" > "$PWD"/logs/ngrok.log 2>&1 &
NGROK_PID=$!

sleep 2
if ! kill -0 $NGROK_PID > /dev/null 2>&1; then
  echo "Ngrok startup error. Exiting the script."
  exit 1
fi

python src/main.py

kill $NGROK_PID
