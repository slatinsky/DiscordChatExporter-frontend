# first stage - build sveltekit app
FROM node:16.18-alpine3.15 as build
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# second stage - install http server, copy static files from first stage build
FROM nikolaik/python-nodejs:python3.11-nodejs16-alpine
RUN apk add --no-cache nginx
# RUN mkdir -p /dcef/exports
# RUN mkdir /dcef/static/data
WORKDIR /dcef
COPY /preprocess/requirements.txt /dcef/backend/preprocess/requirements.txt
RUN python3 -m pip install -r ./backend/preprocess/requirements.txt
RUN mkdir -p /dcef/backend/nginx/logs/
COPY /backend/nginx/conf/mime.types /dcef/backend/nginx/conf/mime.types
COPY /backend/nginx/conf/nginx-docker.conf /dcef/backend/nginx/conf/nginx-docker.conf
COPY --from=build /app/build/ ./static/
COPY backend/preprocess/ ./backend/preprocess/
COPY backend/docker/run_container.sh ./run_container.sh
RUN chmod 777 /dcef/run_container.sh
EXPOSE 21011
CMD /dcef/run_container.sh