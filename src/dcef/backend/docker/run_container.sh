#!/bin/bash
mkdir -p /dcef/cache/preprocess

# MongoDB can't open a database created by an older major version (it needs a step-by-step upgrade),
# so the database is rebuilt from the exports when MongoDB's major version changes
db_rebuilt_warning() {
	echo "############################################################"
	echo "# WARNING: the database was created by an older MongoDB version, so it was deleted"
	echo "# and is being rebuilt from your exports. This takes as long as the first import."
	echo "# Settings saved with configurator.py (allowlisted guilds, denylisted users) were reset."
	echo "# Re-apply them with: docker exec -it dcef python /dcef/configurator.py"
	echo "############################################################"
}
mongo_major_version=$(mongod --version | sed -n 's/^db version v\([0-9]*\)\..*/\1/p')
db_rebuilt=false
if [ -n "$mongo_major_version" ]; then
	if [ -n "$(ls -A /dcef/cache/db 2>/dev/null)" ] && [ "$(cat /dcef/cache/db-mongodb-major-version 2>/dev/null)" != "$mongo_major_version" ]; then
		db_rebuilt=true
		db_rebuilt_warning
		rm -rf /dcef/cache/db
	fi
	echo "$mongo_major_version" > /dcef/cache/db-mongodb-major-version
fi
mkdir -p /dcef/cache/db

mongod --dbpath "/dcef/cache/db/" --wiredTigerCacheSizeGB 1.5 &
cd /dcef/backend/preprocess
python main_mongo.py docker
cd /dcef/backend/fastapi
python prod.py &
if [ "$db_rebuilt" = true ]; then
	db_rebuilt_warning
fi
echo "############################################################"
echo "# Open http://127.0.0.1:21011/ in your browser to view GUI #"
echo "############################################################"
nginx -c /dcef/backend/nginx/conf/nginx-docker.conf