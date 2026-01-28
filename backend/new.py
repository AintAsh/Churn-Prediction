from fastapi import FastAPI , HTTPException
import os
import joblib
import pandas as pd

app = FastAPI(
    title='Customer Churn Prediction API',
    description='An API to predict customer churn using machine learning models.'
)

@app.get('/') # This is get method and root endpoint
def greet():
    return {'message': 'Welcome to the Customer Churn Prediction API!'}

MODEL_PATH = 'best_balanced_churn_model.pkl'  # This is an constant variable 

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f'Model file not found at {MODEL_PATH}')
model = joblib.load(MODEL_PATH)  # Load the model using joblib

# Input Schema for validation 
from pydantic import BaseModel , Field , field_validator 
from typing import Optional
# Pydantic Model 
class CustomerData(BaseModel):
    Gender: str = Field(..., example='Male') # ... -> mandatory field
    Age : int = Field(...,ge=18,le=100, example=45)
    Tenure : int = Field(...,ge=0,le=100, example=12)
    Services_Subscribed : int = Field(...,ge=0,le=10, example=3)
    Contract_Type: str = Field(..., example='Month-to-Month')
    MonthlyCharges : float = Field(...,gt=0, example=89.99)
    TotalCharges : float = Field(...,ge=0, example=1000.0)
    TechSupport : str = Field(..., example='Yes')
    OnlineSecurity : str = Field(..., example='Yes')
    InternetService : str = Field(..., example='Fiber optic')

    @field_validator('Gender')
    @classmethod
    def validate_gender(cls, value):
        allowed = {'Male','Female'}
        if value not in allowed:
            raise ValueError(f"Gender must be {allowed}")
        return value


    @field_validator('Contract_Type')
    @classmethod
    def validate_contract_type(cls, value):
        allowed = {'Month-to-Month','One year','Two year'}
        if value not in allowed:
            raise ValueError(f"Contract_Type must be {allowed}")
        return value
    

    @field_validator('TechSupport')
    @classmethod
    def validate_tech_support(cls, value):
        allowed = {'Yes','No'}
        if value not in allowed:
            raise ValueError(f"Field must be {allowed}")
        return value

    @field_validator('OnlineSecurity')
    @classmethod
    def validate_online_security(cls, value):
        allowed = {'Yes','No'}
        if value not in allowed:
            raise ValueError(f"Field must be {allowed}")
        return value
    
    @field_validator('InternetService')
    @classmethod
    def validate_internet_service(cls, value):
        allowed = {'DSL','Fiber optic','No'}
        if value not in allowed:
            raise ValueError(f"Field must be {allowed}")
        return value
    

# Output Schema
class PredictionResponse(BaseModel):
    churn_label : str 
    churn_probablity : Optional[float]
    churn_prediction : int  

# Prediction End Point 
@app.post('/predict_churn', response_model=PredictionResponse)
def predict(customer : CustomerData):
    try:

        # convert request to dataframe
        input_df = pd.DataFrame([customer.model_dump()])

        # Model Prediction
        prediction = model.predict(input_df)[0]
        
        # Probability
        probablity = None 
        if hasattr(model, 'predict_proba'):
            probablity = model.predict_proba(input_df)[0][1]  # Probability of churn class


        return PredictionResponse(
            churn_prediction=int(prediction),
            churn_label = 'Churn' if prediction ==1 else 'No Churn',
            churn_probablity=probablity
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))