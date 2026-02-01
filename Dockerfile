FROM python:3.12-slim-trixie

WORKDIR /usr/app

COPY requirements.txt ./
RUN python3 -m pip install -r requirements.txt

COPY update_lists.sh ./
COPY dns_resolvers.yml ./
COPY src ./src

ENTRYPOINT ["sh", "update_lists.sh"]
