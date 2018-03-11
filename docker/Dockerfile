FROM python:3.6

ENV PYTHONUNBUFFERED 1
RUN groupadd -g 1001 -r django \
    && useradd -m -u 1001 -r -g django django

RUN apt-get update
RUN apt-get install -y vim-nox telnet strace mysql-client less
COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt && rm requirements.txt

COPY . /opt/project

RUN chown -R django /opt/project


USER django
WORKDIR /opt/project

CMD "/opt/project/entrypoint.sh"
