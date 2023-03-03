# pull official base image
FROM python:3.11.8-slim-bookworm

# set work directory
WORKDIR /usr/src/backend

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# # create the appropriate directories
# ENV HOME=/home/agweather
# ENV APP_HOME=/home/agweather/backend
# RUN mkdir $APP_HOME
# RUN mkdir $APP_HOME/static
# WORKDIR $APP_HOME

# copy project
COPY . .