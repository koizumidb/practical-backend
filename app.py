from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
from db_control import crud, mymodels_MySQL
from db_control.create_tables_MySQL import init_db

app = FastAPI()

@app.on_event("startup")
def on_startup():
    try:
        init_db()
    except Exception as e:
        print("init_db failed:", repr(e))

class Customer(BaseModel):
    customer_id: str
    customer_name: str
    age: int
    gender: str

# CORS設定（Cookie認証していない前提）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://tech0-gen-11-step3-2-node-61.azurewebsites.net",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def index():
    return {"message": "FastAPI top page!"}

@app.post("/customers")
def create_customer(customer: Customer):
    try:
        values = customer.dict()
        crud.myinsert(mymodels_MySQL.Customers, values)
        result = crud.myselect(mymodels_MySQL.Customers, values.get("customer_id"))
        if result:
            result_obj = json.loads(result)
            return result_obj if result_obj else None
        return None
    except Exception as e:
        print("create_customer failed:", repr(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/customers")
def read_one_customer(customer_id: str = Query(...)):
    try:
        result = crud.myselect(mymodels_MySQL.Customers, customer_id)
        if not result:
            raise HTTPException(status_code=404, detail="Customer not found")
        result_obj = json.loads(result)
        return result_obj[0] if result_obj else None
    except HTTPException:
        raise
    except Exception as e:
        print("read_one_customer failed:", repr(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/allcustomers")
def read_all_customer():
    # DBが死んでてもフロントの動作確認を通すため、例外時は [] を返す
    try:
        result = crud.myselectAll(mymodels_MySQL.Customers)
        if not result:
            return []
        return json.loads(result)
    except Exception as e:
        print("read_all_customer failed:", repr(e))
        return []

@app.put("/customers")
def update_customer(customer: Customer):
    try:
        values = customer.dict()
        values_original = values.copy()
        crud.myupdate(mymodels_MySQL.Customers, values)
        result = crud.myselect(mymodels_MySQL.Customers, values_original.get("customer_id"))
        if not result:
            raise HTTPException(status_code=404, detail="Customer not found")
        result_obj = json.loads(result)
        return result_obj[0] if result_obj else None
    except HTTPException:
        raise
    except Exception as e:
        print("update_customer failed:", repr(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.delete("/customers")
def delete_customer(customer_id: str = Query(...)):
    try:
        result = crud.mydelete(mymodels_MySQL.Customers, customer_id)
        if not result:
            raise HTTPException(status_code=404, detail="Customer not found")
        return {"customer_id": customer_id, "status": "deleted"}
    except HTTPException:
        raise
    except Exception as e:
        print("delete_customer failed:", repr(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/fetchtest")
def fetchtest():
    response = requests.get("https://jsonplaceholder.typicode.com/users")
    return response.json()
