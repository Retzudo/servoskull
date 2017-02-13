FROM python

COPY . /servoskull
WORKDIR /servoskull

RUN apt-get update && apt-get install libffi-dev
RUN pip install -r requirements.txt

CMD python -m servoskull.client
