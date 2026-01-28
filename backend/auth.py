# JWT Authentication 
from new import app,CustomerData,PredictionResponse,predict
from fastapi.security import HTTPBearer
from jose import jwt
from fastapi import HTTPException, status



# Configurations
SECRET_KEY = 'Sample_key' # Will be changed in production 
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Security Scheme 
security = HTTPBearer()

from pydantic import BaseModel, Field
# User Authentication Models
class UserLogin(BaseModel):
    username : str
    password : str 

class UserRegister(BaseModel):
    username : str
    password : str

class TokenResponse(BaseModel):
    access_token : str
    token_type : str # Bearer 
    expires_in : int # minutes

fake_users_db = {
    'admin':{
        'username':'Om',
        'password':'Osama@69',
        'disabled':False
    },
    'user1':{
        'username':'user1',
        'password':'user1pass',
        'disabled':False
    }
}


# JWT Access Token 
from datetime import datetime, timedelta
from typing import Optional

def create_access_token(data: dict, expires_delta: Optional[timedelta]=None): # Expires_delta => Token expiration time 
    #1. We will create copy of data to avoid mutation
    
    to_encode = data.copy()
    
    #2. we will Check if expires_delta is provided otherwise we will make default expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else : 
        expire = datetime.utcnow() + timedelta(minutes=15)

    
    #3. Data -> Expiration time add karenge 
    to_encode.update({"exp": expire})

    
    #4. Encode copy data ,Secret key , Algorithm
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    
    
    # 5. return the encoded  token
    return encoded_jwt

class AuthenticatedPredictionRequest(BaseModel):
    customer : CustomerData

# Verification of Token
def verify_token(token: str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username : str = payload.get("sub")
    if username is None : 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Token")
    return username 

def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user or user['password'] != password:
        return None
    return user

# 1. end point for user Register 

@app.post('/register',response_model=TokenResponse)
async def register_user(user :UserRegister):   # async function manage the API's 
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Register User 
    fake_users_db[user.username] = {
        'username': user.username,
        'password': user.password,
        'disabled': False
    }

    # Create Token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username},expires_delta=access_token_expires)

    return {
        'access_token': access_token,
        'token_type':'Bearer',
        'expires_in': ACCESS_TOKEN_EXPIRE_MINUTES * 60 # in seconds
    }



# 2. endpoint for user Login

@app.post('/login',response_model=TokenResponse)
async def login_user(user: UserLogin):
    if authenticate_user(user.username, user.password) is None:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    # Create Token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username},expires_delta=access_token_expires)

    return {
        'access_token': access_token,
        'token_type':'Bearer',
        'expires_in': ACCESS_TOKEN_EXPIRE_MINUTES * 60 # in seconds
    }

# 3. Prediction Endpoint with JWT Authentication    
from fastapi import Depends     
from fastapi.security import HTTPAuthorizationCredentials
# # 1. post endpoint 
# @app.post('/predict/auth',response_model=PredictionResponse, dependencies=[Depends(security)]) # Extracts the authoriszation header , checks the format of the bearer token 

# # 2. response model 
# async def predict_auth(request:AuthenticatedPredictionRequest,credentials:HTTPAuthorizationCredentials=Depends(security)):

# # 3. Verify Token 
#     username = verify_token(credentials.credentials)
        
# # 4. log the authorized user
#     print(f"User : {username} Accessed the Prediction Endpoint")
    
# # 5. call the original prediction function 
#     return predict(request.customer) # We are extraction the customer data from the request from the function 

@app.post('/predict/auth', response_model=PredictionResponse)
async def predict_auth(
    request: AuthenticatedPredictionRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    username = verify_token(credentials.credentials)
    print(f"User {username} accessed prediction endpoint")
    return predict(request.customer)
