FROM node:22
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
RUN npm build
EXPOSE 4000
CMD ["npm", "start"]