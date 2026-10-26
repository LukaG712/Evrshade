FROM node:20-alpine AS build

WORKDIR /app

COPY services/Slammer/package.json ./
RUN npm install

COPY services/Slammer/ ./
RUN npx vite build

FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY services/Slammer/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
