FROM node:20-alpine

WORKDIR /app

RUN addgroup -S app && adduser -S app -G app

COPY package.json .
RUN npm install

COPY . .

RUN chown -R app:app /app
USER app

EXPOSE 3000
CMD ["npm", "run", "dev"]