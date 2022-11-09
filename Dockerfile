# first stage - build sveltekit app
FROM node:16.18-alpine3.15 as build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install
COPY . .
RUN npm run build

# second stage - install http server, copy static files from first stage build
FROM nikolaik/python-nodejs:python3.11-nodejs16-alpine
RUN mkdir -p /dce-f/static/input
RUN mkdir /dce-f/static/data
WORKDIR /dce-f
RUN npm install http-server@^14.1.1 -g
COPY /preprocess/requirements.txt /dce-f/preprocess/requirements.txt
RUN python3 -m pip install -r ./preprocess/requirements.txt
COPY --from=build /app/build/ ./static/
COPY preprocess/ ./preprocess/
COPY server/build.sh ./build.sh
RUN chmod 777 /dce-f/build.sh
EXPOSE 21011
CMD /dce-f/build.sh