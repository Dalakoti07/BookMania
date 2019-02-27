import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# realpython 
#SQLALCHEMY_DATABASE_URI = os.environ['postgres://wxwjtpitggoati:8dfb1487bafbda798870df37a4691bf46afd7162e0d8f3932e7ae20854cd4f89@ec2-54-75-230-41.eu-west-1.compute.amazonaws.com:5432/d50618rt42i32c']

#We have to create the engine first ,which takes the argument of the database on the heroku site
engine = create_engine("postgres://wxwjtpitggoati:8dfb1487bafbda798870df37a4691bf46afd7162e0d8f3932e7ae20854cd4f89@ec2-54-75-230-41.eu-west-1.compute.amazonaws.com:5432/d50618rt42i32c")
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author,year in reader:
        db.execute("INSERT INTO book_record (id, title, author,year) VALUES (:id, :title, :author,:year)",
                    {"id": isbn, "title": title, "author": author,"year":year})
        print(f"Added book of number {isbn} whose title is {title} and author is {author} and published in year{year}")
    db.commit()

if __name__ == "__main__":
    main()
