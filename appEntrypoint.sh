#!/bin/bash

# Start the first process
python /code/manage.py run_huey &
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start Huey: $status"
  exit $status
fi

# Start the second process
gunicorn --workers=2 --bind=0.0.0.0:8000 puzzlehunt_server.wsgi:application &
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start Gunicorn: $status"
  exit $status
fi

while sleep 60; do
  ps aux |grep gunicorn |grep -q -v grep
  PROCESS_1_STATUS=$?
  ps aux |grep huey |grep -q -v grep
  PROCESS_2_STATUS=$?
  # If the greps above find anything, they exit with 0 status
  # If they are not both 0, then something is wrong
  if [ $PROCESS_1_STATUS -ne 0 -o $PROCESS_2_STATUS -ne 0 ]; then
    echo "One of the processes has already exited."
    exit 1
  fi
done
