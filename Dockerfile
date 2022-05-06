FROM python:alpine

COPY --from=golang:alpine /usr/local/go/ /usr/local/go/
 
ENV PATH="/usr/local/go/bin:${PATH}"

RUN apk add --no-cache \
  ffmpeg \
  tzdata

ENV GOPATH=/lux

RUN go install github.com/iawia002/lux@latest

ENV PATH="/lux/bin:${PATH}"

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN apk --update-cache add --virtual build-dependencies gcc libc-dev make \
  && pip install --no-cache-dir -r requirements.txt \
  && apk del build-dependencies

COPY . /usr/src/app

EXPOSE 8080

VOLUME ["/downloads"]

CMD [ "python", "-u", "./lux.py" ]
