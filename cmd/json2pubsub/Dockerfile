FROM golang:1.26.0 as builder

# Create and change to the app directory.
WORKDIR /app

COPY go.* ./
RUN go mod download

COPY . ./

RUN cd cmd && CGO_ENABLED=0 GOOS=linux go build -mod=readonly -v -o json2pubsub

FROM scratch

# Copy the binary to the production image from the builder stage.
COPY --from=builder /app/cmd/json2pubsub /json2pubsub

# Run the web service on container startup.
ENV FUNCTION_TARGET=Json2Pubsub
CMD ["/json2pubsub"]