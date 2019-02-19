# Base Image
FROM python:3.7-slim-stretch as base

COPY requirements.txt requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt && pip3 install gunicorn gevent aiohttp

# STAGE: Build
FROM base as build


COPY . /code
WORKDIR /code

RUN python setup.py build sdist

# STAGE: final
FROM base as final

COPY --from=build /code/dist/blockworkr*.tar.gz /
COPY gunicorn.cfg /gunicorn.cfg


RUN python -m pip install --no-cache-dir /blockworkr*.tar.gz \
  && rm -rf /blockworkr*.tar.gz \
  && mkdir /etc/blockworkr

HEALTHCHECK --interval=15s --timeout=5s \
  CMD curl -f http://localhost/healthz || exit 1

EXPOSE 80

CMD ["gunicorn", "--config", "/gunicorn.cfg", "-b", "0.0.0.0:80", "blockworkr.webservice:app"]