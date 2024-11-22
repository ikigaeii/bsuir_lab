from fastapi import FastAPI, Request


async def get_db(request: Request):
    return request.app.state.db
