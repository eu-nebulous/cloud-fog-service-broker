# Step 1: Build Stage
FROM node:16 as build-stage

WORKDIR /app

COPY package.json package-lock.json ./

RUN npm install

COPY . .

RUN npm run build

# Step 2: Nginx Stage
FROM docker.io/nginx:alpine

COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY .env.production /usr/share/nginx/html/.env

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
