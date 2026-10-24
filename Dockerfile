# build using (linux):
# docker build -t dcef .
# ----------------------

# build sveltekit static app
FROM node:24.22.1-alpine3.24 as build
RUN mkdir -p /app/dcef/frontend
WORKDIR /app/dcef/frontend
COPY src/dcef/frontend/package.json src/dcef/frontend/package-lock.json ./
RUN npm install
COPY src/dcef/frontend/ .
RUN npm run build

# main image
FROM mongo:9.0.4-resolute
WORKDIR /dcef
RUN apt-get update && apt-get install python3 python3-venv nginx -y
# Ubuntu doesn't allow pip to install into the system Python, use a virtual environment
RUN python3 -m venv /dcef/venv
ENV PATH="/dcef/venv/bin:$PATH"
RUN mkdir -p /dcef/exports/
COPY release/exports/ /dcef/exports/
COPY src/dcef/backend/preprocess/requirements.txt /dcef/backend/preprocess/requirements.txt
COPY src/dcef/backend/fastapi/requirements.txt /dcef/backend/fastapi/requirements.txt
COPY src/dcef/backend/configurator/requirements.txt /dcef/backend/configurator/requirements.txt
RUN pip install -r /dcef/backend/preprocess/requirements.txt
RUN pip install -r /dcef/backend/fastapi/requirements.txt
RUN pip install -r /dcef/backend/configurator/requirements.txt
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