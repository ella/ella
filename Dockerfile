# Really simple dockerfile, the idea is to make any changes that the testing makes to the filesystem ephemeral and to make sure we don't persist anything between tests
FROM python:2.7
COPY . /app
WORKDIR /app