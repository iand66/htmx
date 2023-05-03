import colorama, uvicorn
from typing import Optional
from fastapi import FastAPI, Request, Header, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import Base, Film

Base.metadata.create_all(bind=engine)
app = FastAPI()
templates = Jinja2Templates(directory='templates')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def populate_db():
    db = SessionLocal()
    num_films = db.query(Film).count()
    if num_films == 0:
        films = [
            {'name':'Blade Runner','director':'Ridley Scott'},
            {'name':'Pulp Fiction','director':'Quentin Tarantino'},
            {'name':'Mulholland Drive','director':'David Lynch'},
            {'name':'Jurassic Park','director':'Steven Spielberg'},
            {'name':'Tokyo Story','director':'Yasujiro Ozu'},
            {'name':'Chungking Express','director':'Kar-Wai Wong'}
        ]
    
        for film in films:
            db.add(Film(**film))
            db.commit()
            db.close()
    else:
        print(f'There are {num_films} films filed in the database')

@app.get('/index', response_class=HTMLResponse)
def movielist(
    request: Request, 
    hx_request: Optional[str] = Header(None),
    db: Session = Depends(get_db),
    page: int = 1
    ):
    
    N = 2
    OFFSET = (page - 1) * N
    films = db.query(Film).offset(OFFSET).limit(N)
    context = {'request' : request, 'films':films, "page": page}
    if hx_request:
        return templates.TemplateResponse('table.html', context)
    return templates.TemplateResponse('index.html', context)

if __name__ == '__main__':
    colorama.init()
    config = uvicorn.Config('main:app', port=8000, log_level='info')
    server = uvicorn.Server(config)
    server.run()
