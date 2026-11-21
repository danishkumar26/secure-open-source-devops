FROM node:26-alpine
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev
COPY . .
RUN npm run build
ENV NEXT_PUBLIC_API_URL=http://localhost:8000
EXPOSE 3000
CMD ["npm", "start"]
