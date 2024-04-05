from fastapi import FastAPI, HTTPException, Path,Query
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId

app = FastAPI()

MONGO_URI = "mongodb+srv://anurag:anurag@cluster0.9aj2aqn.mongodb.net/test?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client["LibraryManagement"]
students_collection = db["students"]

class Address(BaseModel):
    city: str
    country: str

class Student(BaseModel):
    name: str
    age: int
    address: Address

class StudentInDB(Student):
    id: str

#POST
@app.post("/students", response_model=dict)
def create_student(student: Student):
    student_dict = student.dict()
    result = students_collection.insert_one(student_dict)
    return {"id": str(result.inserted_id)}


#GET
@app.get("/students", response_model=dict, status_code=200)
def list_students(country: str = Query(None, description="Filter students by country"),min_age: int = Query(None, description="Minimum age to filter students")):
    query = {}

    if country:
        query["address.country"] = country

    if min_age is not None:
        query["age"] = {"$gte": min_age}

    students = list(students_collection.find(query, {"_id": 0}))

    response_data = {"data": students}

    return response_data

#GET
@app.get("/students/{id}", response_model=Student)
def get_student(id: str = Path(...)):
    student = students_collection.find_one({"_id": ObjectId(id)})
    if student:
        student.pop("_id")
        return student
    else:
        raise HTTPException(status_code=404, detail="Student not found")
    
#PATCH
@app.patch("/students/{id}", response_model=dict)
def update_student(id: str = Path(...), student_data: Student = None): # type: ignore
    if student_data is None:
        raise HTTPException(status_code=400, detail="Invalid student data")

    student_dict = student_data.dict(exclude_unset=True)

    result = students_collection.update_one({"_id": ObjectId(id)}, {"$set": student_dict})

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")

    return {}

#DELETE
@app.delete("/students/{id}", response_model=dict)
def delete_student(id: str = Path(...)):
    result = students_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {}
