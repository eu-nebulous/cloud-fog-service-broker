#
FROM python:3.10

#
WORKDIR /flask_app

#
COPY ./requirements.txt /flask_app/requirements.txt

#
RUN pip install --no-cache-dir --upgrade -r /flask_app/requirements.txt

#
COPY ./ /flask_app

#
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port", "8001"]