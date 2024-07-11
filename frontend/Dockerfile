# Etapa de construcción
FROM node:18-alpine as build

WORKDIR /app

# Instala las dependencias
COPY package.json package-lock.json ./
RUN npm install --legacy-peer-deps

# Copia el código fuente y construye la aplicación
COPY . ./
RUN npm run build -- --project material-dashboard-angular --configuration production

# Etapa de ejecución
FROM node:18-alpine

WORKDIR /app

# Instala http-server para servir los archivos estáticos
RUN npm install -g http-server

# Copia los archivos estáticos construidos desde la etapa de construcción
COPY --from=build /app/dist/material-dashboard-angular /app/dist

# Exponer el puerto 8080
EXPOSE 8080

# Comando para iniciar http-server
CMD ["http-server", "dist", "-p", "8080"]
