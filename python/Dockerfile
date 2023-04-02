FROM python:3.10-bullseye

WORKDIR /usr/src/spaceship-app

COPY . .

RUN pip install --no-cache-dir -r ./requirements/lock.txt

CMD [ "uvicorn", "spaceship.main:app", "--host=0.0.0.0", "--port=8080" ]
