from fastapi import FastAPI
from fastapi.requests import Request
import time

def register_middleware(app:FastAPI):
    
    @app.middleware('http')
    async def custom_login(request:Request,call_next):
      start_time = time.time()
      
      print('before',start_time)
      
      response = await call_next(request) 
      
      processing_time = time.time() - start_time
      print('processed after',processing_time)
      
      return response 
    
