# first stage build - build sveltekit app
FROM node:16.18-alpine3.15 as build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install
COPY . .
RUN npm run build

# second stage build - install http server, copy static files from first stage build
FROM nikolaik/python-nodejs:python3.11-nodejs16-alpine
RUN mkdir /dce-f
RUN mkdir /dce-f/static
RUN mkdir /dce-f/static/input
RUN mkdir /dce-f/static/data
WORKDIR /dce-f
RUN npm install http-server@^14.1.1 -g

COPY --from=build /app/build/ ./static/
EXPOSE 21011
COPY preprocess/ ./preprocess/
COPY server/build.sh ./build.sh
RUN python3 -m pip install -r ./preprocess/requirements.txt
WORKDIR /dce-f/preprocess
RUN python3 main.py
WORKDIR /dce-f

RUN ls -la static/input

RUN chmod 777 /dce-f/build.sh
CMD /dce-f/build.sh; sh