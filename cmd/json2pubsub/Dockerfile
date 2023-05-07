FROM golang:1.20.4 as builder

# Create and change to the app directory.
WORKDIR /app

COPY go.* ./
RUN go mod download

COPY . ./

RUN CGO_ENABLED=0 GOOS=linux go build -mod=readonly -v -o json2pubsub

FROM alpine:3
RUN apk add --no-cache ca-certificates

# Copy the binary to the production image from the builder stage.
COPY --from=builder /app/json2pubsub /json2pubsub

# Run the web service on container startup.
CMD ["/json2pubsub"]