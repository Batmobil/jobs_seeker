FROM python:3.6.7

COPY linux_pip_requirements.txt /
RUN pip install -r /linux_pip_requirements.txt

RUN mkdir /myworkdir
WORKDIR /myworkdir
COPY ./ ./

EXPOSE 8050
CMD ["python", "./jobs_dashboard.py"]
