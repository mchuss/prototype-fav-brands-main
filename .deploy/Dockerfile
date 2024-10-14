FROM git.goldapple.ru:8443/cds/etl/prototype_fav_brands/python-base-image:latest

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . /app

CMD ["streamlit", "run", "streamlit_run.py"]
