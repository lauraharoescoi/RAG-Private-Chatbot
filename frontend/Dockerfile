FROM node:18-alpine

WORKDIR /app

EXPOSE 4200

COPY package.json package-lock.json ./

RUN npm install --legacy-peer-deps

COPY . ./

CMD npm run ng serve -- --host 0.0.0.0
