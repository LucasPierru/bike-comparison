FROM node:22
WORKDIR /app
COPY . .
RUN npm install --omit=dev
RUN npm run build
EXPOSE 4000
CMD ["node", "dist/src/server.js"]