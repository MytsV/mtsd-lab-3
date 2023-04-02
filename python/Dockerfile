FROM python:3.10-slim

WORKDIR /usr/src/spaceship-app

COPY ./requirements/lock.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "uvicorn", "spaceship.main:app", "--host=0.0.0.0", "--port=8080" ]
