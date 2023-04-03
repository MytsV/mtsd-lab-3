FROM golang AS base

WORKDIR /usr/src/fizzbuzz-app

COPY go.mod go.sum ./
RUN go mod download && go mod verify

COPY . .
RUN go build -o /usr/local/bin/fizzbuzz

FROM gcr.io/distroless/base
WORKDIR /fizzbuzz-app
COPY --from=base /usr/local/bin/fizzbuzz ./
COPY --from=base /usr/src/fizzbuzz-app/templates ./templates

CMD ["./fizzbuzz", "completion", "zsh"]
