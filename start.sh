#!/bin/sh

CMD="python yt_dlp_server.py"

if [ "$HOST" ]; then
  CMD="$CMD --host $HOST"
fi

if [ "$DIR" ]; then
  CMD="$CMD -d $DIR"  # 注意这里从 --dir 改为 -d
fi

if [ "$PORT" ]; then
  CMD="$CMD --port $PORT"
fi

exec $CMD
