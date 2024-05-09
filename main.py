from sqlalchemy import create_engine, URL, select
from sqlalchemy.orm import sessionmaker

from models import Dish

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

with Session() as session:
    movie = session.execute(select(Dish).where(Movie.id==5)).scalar_one()
    print(movie.rating)
