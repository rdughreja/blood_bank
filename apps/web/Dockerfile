# Config only — NOT verified (Docker ignored per owner instruction).
FROM node:24-alpine
WORKDIR /app
COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci
COPY apps/web/ ./
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
