FROM python:3.9-slim
WORKDIR /usr/src/app
RUN apt-get -y update
RUN apt-get -y upgrade

COPY . .

RUN pip install -r requirements.txt

EXPOSE 3030
CMD ["python3", "./manage.py"]