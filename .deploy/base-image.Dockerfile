FROM python:3.9.19-slim

ENV VAULT_ADDR=https://ekb-vault.ga.loc:8443


RUN apt update && \
    apt install -yqq apt-transport-https curl wget

RUN curl -ss http://registry.ga.loc/ca/ga_chain2.pem>/usr/local/share/ca-certificates/ca_root_ga2.crt && \
    curl -ss http://registry.ga.loc/ca/ga_chain.pem>/usr/local/share/ca-certificates/ca_root_ga.crt && \
    update-ca-certificates

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

