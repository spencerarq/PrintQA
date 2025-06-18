# frontend/dockerfile

# --- Estágio 1: Build (Construção) ---
# Usamos uma imagem Node.js para construir o projeto React
FROM node:20-alpine AS builder

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia os arquivos de definição de pacotes
COPY package.json package-lock.json ./

# Instala as dependências do projeto
RUN npm install

# Copia o restante do código-fonte da aplicação
COPY . .

# Executa o script de build do React para gerar os arquivos estáticos
RUN npm run build


# --- Estágio 2: Production (Produção) ---
# Usamos uma imagem Nginx super leve para servir os arquivos estáticos
FROM nginx:1.27-alpine

# Copia os arquivos estáticos gerados no estágio de build para a pasta padrão do Nginx
COPY --from=builder /app/build /usr/share/nginx/html

# Remove a configuração padrão do Nginx
RUN rm /etc/nginx/conf.d/default.conf

# Copia nosso arquivo de configuração personalizado (que criaremos no próximo passo)
COPY nginx.conf /etc/nginx/conf.d

# Expõe a porta 80, que é a porta padrão do Nginx
EXPOSE 80

# Comando para iniciar o servidor Nginx
CMD ["nginx", "-g", "daemon off;"]