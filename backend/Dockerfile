FROM node:22
WORKDIR /app
COPY package.json package-lock.json ./ 
RUN npm install --production
COPY . .
RUN npm run build
EXPOSE 4000
CMD ["node", "dist/src/server.js"]