#!/bin/sh
python --version
which python

# python --version
# which python
PR="[run.sh]"
NAME="hyundai_wallpad"

SHARE_DIR="/share/$NAME"
echo "$PR Start To run.sh"
echo "$PR Container DIR => $SHARE_DIR"

mkdir -p $SHARE_DIR
echo "$PR CREATED $SHARE_DIR"

# 호스트머신이랑 공유 할 거 있을 때
# if [ ! -f $SHARE_DIR/kocom.conf ]; then
# 	mv /kocom.conf $SHARE_DIR
# fi

echo "[Info] Run $NAME"
python /src/run.py