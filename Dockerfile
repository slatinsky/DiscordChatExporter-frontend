# build sveltekit static app
FROM node:16.18-alpine3.15 as build
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# first stage
FROM mongo:6.0.5-jammy
WORKDIR /dcef
RUN apt-get update && apt-get install python3.11 python3-pip nginx -y
RUN mkdir -p /dcef/exports/
COPY /release/exports/ /dcef/exports/
COPY /backend/preprocess/requirements.txt /dcef/backend/preprocess/requirements.txt
COPY /backend/fastapi/requirements.txt /dcef/backend/fastapi/requirements.txt
RUN python3.11 -m pip install -r ./backend/preprocess/requirements.txt
RUN python3.11 -m pip install -r ./backend/fastapi/requirements.txt
RUN mkdir -p /dcef/backend/nginx/logs/
COPY /backend/nginx/conf/mime.types /dcef/backend/nginx/conf/mime.types
COPY /backend/nginx/conf/nginx-docker.conf /dcef/backend/nginx/conf/nginx-docker.conf
COPY --from=build /app/build/ ./frontend/
COPY backend/preprocess/ ./backend/preprocess/
COPY backend/fastapi/ ./backend/fastapi/
COPY backend/docker/run_container.sh ./run_container.sh
RUN chmod 777 /dcef/run_container.sh
EXPOSE 21011
CMD /dcef/run_container.sh