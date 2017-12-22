FROM python:3
COPY . /hangman
WORKDIR /hangman
EXPOSE 5000
RUN pip install -r requirements.txt
ENV FLASK_APP app.py
CMD ["flask", "run", "--host=0.0.0.0"]
