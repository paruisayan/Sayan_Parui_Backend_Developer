# import numpy as np
# # # lst1=[1,2,3]
# # # # my_array=np.array(lst)
# # # # print(type(my_array))
# # # # print(my_array)
# # # lst2=[2,4,3]
# # # lst3=[3,4,5]
# # # lst4=[100,2,4]
# # # my_array=np.array([lst1,lst2,lst3,lst4])
# # # print(my_array.shape)
# # # print(my_array.reshape(12,1))
# # # print(np.arange(1,11,1).reshape(5,2))
# # list=[1,2,3,4]
# # print(id(list))
# # list[0]=2
# # print(id(list))
# # even=[x for x in range(1,10) if x%2==0]
# # for i in even:
# #     print(i,end=" ")
# #
# # dict={
# #     "Name":"Sayan Parui",
# #     "Class":"class XII",
# #     "Branch":"Pure Science",
# #     "Roll": 1
# #
# # }
# #print(dict.items())
# # print(dict["Name"])
# # print(dict['Class'])
# # print(dict['Branch'])
# # dict["Class"]="Class XI"
# # print(dict)
# # dict["Post"]="Sports Secretory"
# # print(dict)
# #for i in dict:
# # t={1,2,3}
# # q={2,3,4}
# # t.add(5)
# # t.add(4)
# # print(t)
from fastapi import FastAPI
from pydantic import BaseModel
app=FastAPI()
@app.get("/")
def Homepage():
    return {"message": "Welcome to home page"}

@app.get("/employee/{employee_id}")
def get_employee_number(employee_id: int):
    return {"message": f"{employee_id}Welcome to my homepage" ,"employee_id": employee_id}
@app.get("/employee/{employee_id}/{employee_name}")
def get_employee_number(employee_id: int, employee_name: str):
    return {"message": f"{employee_id}Welcome to employee info" ,"employee_id": employee_id , "employee_name": employee_name}
class Employee(BaseModel):
    employee_id: int
    employee_name: str
    employee_age: int
@app.post("/employee")
def create_employee(employee: Employee):
    return {
        "massage": f"{employee.employee_id}Welcome to my homepage",
        "data_received": "User added successfully"
    }

@app.get("/search")
def search(employee_name: str = None, employee_id: int = None):
    # Let's assume we have a small database (a Python list)
    employees = [
        {"employee_id": 101, "employee_name": "Sayan"},
        {"employee_id": 102, "employee_name": "Ravi"}
    ]

    # check if user found
    for emp in employees:
        if emp["employee_name"] == employee_name or emp["employee_id"] == employee_id:
            return {"message": "User found", "employee": emp}

    # if not found
    return {"message": "User not found"}

