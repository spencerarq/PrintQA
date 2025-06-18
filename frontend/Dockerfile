# frontend/dockerfile

# --- Estágio 1: Build (Construção) ---

FROM node:20.12-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./

RUN npm install

COPY . .

RUN npm run build

# --- Estágio 2: Production (Produção) ---
FROM nginx:1.27-alpine

COPY --from=builder /app/build /usr/share/nginx/html

RUN rm /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/conf.d

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]