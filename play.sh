#!/bin/bash

# Run the first Python script in the background
python3 server.py &

sleep 0.3
# Run the second Python script in the background
python3 student.py &

# Run the third Python script in the background
python3 viewer.py &

# Wait for all background processes to finish
wait
