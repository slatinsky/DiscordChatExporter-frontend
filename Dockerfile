# build using (linux):
# docker build -t dcef .
# ----------------------

# build sveltekit static app
FROM node:22.6.0-alpine3.19 as build
RUN mkdir -p /app/dcef/frontend
WORKDIR /app/dcef/frontend
COPY src/dcef/frontend/package.json src/dcef/frontend/package-lock.json ./
RUN npm install
COPY src/dcef/frontend/ .
RUN npm run build

# main image
FROM mongo:6.0.5-jammy
WORKDIR /dcef
RUN apt-get update && apt-get install python3.11 python3-pip nginx wget -y
RUN mkdir -p /dcef/exports/
COPY release/exports/ /dcef/exports/
COPY src/dcef/backend/preprocess/requirements.txt /dcef/backend/preprocess/requirements.txt
COPY src/dcef/backend/fastapi/requirements.txt /dcef/backend/fastapi/requirements.txt
COPY src/dcef/backend/configurator/requirements.txt /dcef/backend/configurator/requirements.txt
RUN python3.11 -m pip install -r /dcef/backend/preprocess/requirements.txt
RUN python3.11 -m pip install -r /dcef/backend/fastapi/requirements.txt
RUN python3.11 -m pip install -r /dcef/backend/configurator/requirements.txt
RUN mkdir -p /dcef/backend/nginx/logs/
COPY src/dcef/backend/nginx/conf/mime.types /dcef/backend/nginx/conf/mime.types
COPY src/dcef/backend/nginx/conf/nginx-docker.conf /dcef/backend/nginx/conf/nginx-docker.conf
COPY --from=build /app/_temp/frontend/ ./frontend/
COPY src/dcef/backend/preprocess/ ./backend/preprocess/
COPY src/dcef/backend/fastapi/ ./backend/fastapi/
COPY src/dcef/backend/configurator/main.py ./configurator.py
COPY src/dcef/backend/docker/run_container.sh ./run_container.sh
RUN chmod 777 /dcef/run_container.sh
EXPOSE 21011
CMD /dcef/run_container.sh