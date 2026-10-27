FROM node:22-alpine AS build
WORKDIR /app
COPY services/Slammer/package.json services/Slammer/package-lock.json ./
RUN npm ci
COPY services/Slammer/ .
RUN npm run build

FROM nginx:1.27.3-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY services/Slammer/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
