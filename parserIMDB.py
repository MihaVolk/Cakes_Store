from bs4 import BeautifulSoup
import requests


from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker

from models import Movie

url = URL.create(
    drivername="postgresql+psycopg2",
    username="postgres",
    password="root",
    host="localhost",
    database="3sem_goiteens",
    port=5432,
)

engine = create_engine(url, echo=False)

Session = sessionmaker(engine)

movies_url = "https://kinogo.biz/"

r = requests.get(movies_url)

soup = BeautifulSoup(r.text, "html.parser")

movies_div = soup.find("div", attrs={"id": "dle-content"})
movies_list = movies_div.find_all("div", attrs={"class": "shortstory"})

for movie_div in movies_list:
    movie_name = (
        movie_div.find("div", attrs={"class": "shortstory__title"})
        .find("a")
        .find("h2")
        .text
    )

    movie_desk = (
       movie_div.find("div", attrs={"class": "shortstory__body"})
       .find("div", attrs={"class": "shortstory__info"})
       .find("div", attrs={"class": "excerpt"})   
    )
       
    movie_raiting = movie_div.find("span", attrs={"class": "rating__results"}).text[:3]
    print(movie_name)
    
    # with Session() as session:
    #     movie_db = Movie(name=movie_name, description=movie_desk, year=1000)
    #     session.add(movie_db)
    #     session.commit()