# start from an official message
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set work directory
WORKDIR /todolist

# install dependencies

#COPY requirements.txt .
#RUN pip install --upgrade pip
#RUN pip install -r requirements.txt

# Copy only requirements to cache them in docker layer

RUN pip install "poetry==1.3.1"
COPY poetry.lock pyproject.toml /todolist/
# Project initialization:
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi --no-root

# Creating folders, and files for a project:
COPY . .

EXPOSE 8000
# define the command to run when starting the container
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
