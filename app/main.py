from fastapi import FastAPI
from .routers import users, auth, polls


app = FastAPI()

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(polls.router)


@app.get("/")
def root():
    return {"massage": "Home page"}
