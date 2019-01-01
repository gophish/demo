#!/bin/sh

DATABASE=/usr/src/gophish/gophish.db

# Wait for the gophish.db file to exist
until [ -f $DATABASE ]; do
  >&2 echo "Waiting for database"
  sleep 1
done

# Wait for the table to be populated
until sqlite3 $DATABASE 'select api_key from users limit 1'; do
   >&2 echo "Waiting for database"
  sleep 1
done 

# Get the API key
export API_KEY=$(sqlite3 $DATABASE 'select api_key from users limit 1');

# Launch the demo
python create_demo.py --api-key=$API_KEY --num-members 30