FROM python:3.12.6

WORKDIR /secrag


COPY ./requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

# RUN cd client
# RUN npm run build
# RUN cd ..

EXPOSE 8000-9001

CMD ["/bin/bash","-c","cd client; npm run build; cd ..; gunicorn -w 2 --bind 0.0.0.0:8000 wsgi:app"]