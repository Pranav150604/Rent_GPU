from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from typing import List

app = FastAPI()

# In-memory data for simplicity (replace with database in production)
fake_gpus = [
    {"id": 1, "name": "NVIDIA GeForce GTX 1080", "price_per_hour": 5.0, "availability": True},
    {"id": 2, "name": "AMD Radeon RX 5700 XT", "price_per_hour": 7.0, "availability": True},
]

fake_rentals = []

# Token authentication using OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Function to get the current user based on the token
def get_current_user(token: str = Depends(oauth2_scheme)):
    # In a real-world scenario, you would validate the token and retrieve user information
    return {"username": "example_user"}


# User authentication endpoint
@app.post("/token")
def login_for_access_token():
    # In a real-world scenario, you would validate the user's credentials and generate a token
    return {"access_token": "example_token", "token_type": "bearer"}


# Get available GPUs endpoint
@app.get("/gpus", response_model=List[dict])
def get_available_gpus():
    return [gpu for gpu in fake_gpus if gpu["availability"]]


# Rent GPU endpoint
@app.post("/gpus/{gpu_id}/rent")
def rent_gpu(gpu_id: int, duration_hours: int, current_user: dict = Depends(get_current_user)):
    gpu = next((g for g in fake_gpus if g["id"] == gpu_id), None)
    if gpu and gpu["availability"]:
        rental_details = {
            "gpu_id": gpu["id"],
            "duration_hours": duration_hours,
            "total_cost": duration_hours * gpu["price_per_hour"],
            "timestamp": datetime.utcnow(),
        }
        fake_rentals.append(rental_details)
        gpu["availability"] = False
        return {"success": True, "message": "GPU rented successfully", "rental_details": rental_details}
    else:
        raise HTTPException(status_code=400, detail="GPU not available for rent")


# Get rental history endpoint
@app.get("/rentals", response_model=List[dict])
def get_rental_history(current_user: dict = Depends(get_current_user)):
    user_rentals = [rental for rental in fake_rentals]
    return user_rentals


# Return GPU endpoint
@app.post("/gpus/{gpu_id}/return")
def return_gpu(gpu_id: int, current_user: dict = Depends(get_current_user)):
    gpu = next((g for g in fake_gpus if g["id"] == gpu_id), None)
    if gpu:
        gpu["availability"] = True
        return {"success": True, "message": "GPU returned successfully"}
    else:
        raise HTTPException(status_code=400, detail="GPU not found")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
