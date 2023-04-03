FROM golang:1.17-alpine AS base

WORKDIR /usr/src/fizzbuzz-app

COPY go.mod go.sum ./
RUN go mod download && go mod verify

COPY . .
RUN CGO_ENABLED=0 go build -v -o /usr/local/bin/fizzbuzz

FROM scratch
WORKDIR /root/
COPY --from=base /usr/local/bin/fizzbuzz ./
COPY --from=base /usr/src/fizzbuzz-app/templates ./templates

CMD ["./fizzbuzz", "serve"]
