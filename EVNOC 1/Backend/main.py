from fastapi import BackgroundTasks, Depends, FastAPI
import uvicorn
from dependencies import get_query_token, get_token_header
#from internals import admin
from routers import evCharger, items
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()#dependencies=[Depends(get_query_token)])

origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(evCharger.router)
app.include_router(items.router)
# app.include_router(
#     admin.router,
#     prefix="/admin",
#     tags=["admin"],
#     dependencies=[Depends(get_token_header)],
#     responses={418: {"description": "I'm a teapot"}},
# )


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}


if __name__ == "__main__":
    # print('Application start on')
    uvicorn.run("main:app", host="0.0.0.0", port=3099, reload=True, log_level="info")    
