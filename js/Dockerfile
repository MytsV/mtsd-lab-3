FROM node as builder
WORKDIR /app
COPY package.json package-lock.json index.js ./
RUN npm install --prod
RUN npm install -g esbuild
RUN npm install -g pkg
RUN npx esbuild index.js  --bundle --outfile=build.cjs --format=cjs --platform=node
RUN pkg .

FROM scratch
WORKDIR /app
COPY --from=builder /app/hello-world /app/
CMD ["./hello-world"]