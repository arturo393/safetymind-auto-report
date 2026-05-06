FROM golang:1.21-bullseye AS builder
WORKDIR /build
COPY jira-api/go.mod ./
RUN go get github.com/gin-gonic/gin@v1.9.1 && \
    go get gopkg.in/yaml.v3@v3.0.1
COPY jira-api/main.go ./
RUN go build -o jira-api .

# Final Stage
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y --no-install-recommends \
    wkhtmltopdf \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /build/jira-api .
COPY jira-api/config/ ./config/
COPY jira-api/templates/ ./templates/
COPY .env .env

RUN mkdir -p /app/reports

EXPOSE 8080
ENV PORT=8080
CMD ["/app/jira-api"]
