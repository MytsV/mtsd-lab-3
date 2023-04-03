FROM golang:1.17-alpine

WORKDIR /usr/src/fizzbuzz-app

COPY go.mod go.sum ./
RUN go mod download && go mod verify

COPY . .
RUN go build -v -o /usr/local/bin/fizzbuzz

CMD ["fizzbuzz", "serve"]