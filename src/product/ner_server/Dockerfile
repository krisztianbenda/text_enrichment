FROM python:3.6-slim 

COPY . /app
WORKDIR /app
ENV PYTHONPATH /

RUN mkdir -p /var/www \
&& apt-get update \
&& apt-get install -y \
build-essential \
python-dev \
git \ 
python3-pip \ 
&& pip3 install -U pip

RUN pip3 install -U jieba \ 
ipython \ 
numpy \ 
pandas \ 
requests \ 
chardet \ 
simplejson \
flask \
&& pip3 install -U spacy \ 
&& python -m spacy download en_core_web_lg

CMD python server.py

EXPOSE 5001
