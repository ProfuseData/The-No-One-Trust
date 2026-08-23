from fastapi 
import FastAPI app = FastAPI() 

button_count = 0 

@app.post("/increment") 
def increment(): 
  global button_count 
  button_count += 1 
  return {"count": button_count} 

@app.post("/decrement") 
def increment(): 
  global button_count 
  button_count -= 1 
  return {"count": button_count} 
  
@app.get("/count") 
def count(): 
  return {"count": button_count}
