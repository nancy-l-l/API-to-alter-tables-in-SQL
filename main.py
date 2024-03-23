from typing import Any, Dict

import pymysql
# Simple starter project to test installation and environment.
# Based on https://fastapi.tiangolo.com/tutorial/first-steps/
from fastapi import FastAPI, Response, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
# Explicitly included uvicorn to enable starting within main program.
# Starting within main program is a simple way to enable running
# the code within the PyCharm debugger
import uvicorn

from db import DB

# Type definitions
KV = Dict[str, Any]  # Key-value pairs

app = FastAPI()

# NOTE: In a prod environment, never put this information in code!
# There are design patterns for passing confidential information to
# application.
# TODO: You may need to change the password
db = DB(
	host="localhost",
	port=3306,
	user="root",
	password="L2d3q1l2d3q1",
	database="s24_hw2",
)

@app.get("/")
async def healthcheck():
	return HTMLResponse(content="<h1>Heartbeat</h1>", status_code=status.HTTP_200_OK)


# TODO: all methods below

# --- STUDENTS ---

@app.get("/students")
async def get_students(req: Request):
	"""Gets all students that satisfy the specified query parameters.

	For instance,
		GET http://0.0.0.0:8002/students
	should return all attributes for all students.

	For instance,
		GET http://0.0.0.0:8002/students?first_name=John&last_name=Doe
	should return all attributes for students whose first name is John and last name is Doe.

	You must implement a special query parameter, `fields`. You can assume
	`fields` is a comma-separated list of attribute names. For instance,
		GET http://0.0.0.0:8002/students?first_name=John&fields=first_name,email
	should return the first name and email for students whose first name is John.
	Not every request will have a `fields` parameter.

	You can assume the query parameters are valid attribute names in the student table
	(except `fields`).

	:param req: The request that optionally contains query parameters
	:returns: A list of dicts representing students. The HTTP status should be set to 200 OK.
	"""

	# Use `dict(req.query_params)` to access query parameters
	param = dict(req.query_params)
	if len(param) > 0:
		fields = param.get('fields')
		param.pop('fields')
		rows = fields.split(",")
	else:
		rows = list()

	query1 = db.select("student", rows, param)
	return query1


@app.get("/students/{student_id}")
async def get_student(student_id: int):
	"""Gets a student by ID.

	For instance,
		GET http://0.0.0.0:8002/students/1
	should return the student with student ID 1. The returned value should
	be a dict-like object, not a list.

	If the student ID doesn't exist, the HTTP status should be set to 404 Not Found.

	:param student_id: The ID to be matched
	:returns: If the student ID exists, a dict representing the student with HTTP status set to 200 OK.
				If the student ID doesn't exist, the HTTP status should be set to 404 Not Found.
	"""
	existing_student = db.select("student", [], {"student_id": student_id})
	if existing_student:
		return JSONResponse(content=existing_student[0], status_code=status.HTTP_200_OK)
	else:
		return HTMLResponse(status_code=status.HTTP_404_NOT_FOUND)


@app.post("/students")
async def post_student(req: Request):
	"""Creates a student.

	You can assume the body of the POST request is a JSON object that represents a student.
	You can assume the request body contains only attributes found in the student table and does not
	attempt to set `student_id`.

	For instance,
		POST http://0.0.0.0:8002/students
		{
			"first_name": "John",
			"last_name": "Doe",
			...
		}
	should create a student with the attributes specified in the request body.

	If the email is not specified in the request body, the HTTP status should be set to 400 Bad Request.
	If the email already exists in the student table, the HTTP status should be set to 400 Bad Request.
	If the enrollment year is not valid, the HTTP status should be set to 400 Bad Request.

	:param req: The request, which contains a student JSON in its body
	:returns: If the request is valid, the HTTP status should be set to 201 Created.
				If the request is not valid, the HTTP status should be set to 400 Bad Request.
	"""

	# Use `await req.json()` to access the request body
	data = await req.json()
	if data["enrollment_year"] > 2023 or data["enrollment_year"] < 2016:
		return HTMLResponse(status_code=status.HTTP_400_BAD_REQUEST)

	if "email" not in data.keys():
		return HTMLResponse(status_code=status.HTTP_400_BAD_REQUEST)
	existing_student = db.select("student", [], {"email": data["email"]})
	if existing_student:
		return HTMLResponse(content="Email already exists", status_code=status.HTTP_400_BAD_REQUEST)
	if "middle_name" not in data.keys():
		data['middle_name'] = None
	try:
		db.insert("student", data)
		return HTMLResponse(status_code=status.HTTP_201_CREATED)

	except pymysql.Error as e:
		return HTMLResponse(status_code=status.HTTP_400_BAD_REQUEST)

@app.put("/students/{student_id}")
async def put_student(student_id: int, req: Request):
	"""Updates a student.

	You can assume the body of the PUT request is a JSON object that represents a student.
	You can assume the request body contains only attributes found in the student table and does not
	attempt to update `student_id`.

	For instance,
		PUT http://0.0.0.0:8002/students/1
		{
			"first_name": "Joe"
		}
	should update the student with student ID 1's first name to Joe.

	If the student does not exist, the HTTP status should be set to 404 Not Found.
	If the email is set to null in the request body, the HTTP status should be set to 400 Bad Request.
	If the email already exists in the student table, the HTTP status should be set to 400 Bad Request.
	If the enrollment year is not valid, the HTTP status should be set to 400 Bad Request.

	:param student_id: The ID of the student to be updated
	:param req: The request, which contains a student JSON in its body
	:returns: If the request is valid, the HTTP status should be set to 200 OK.
				If the request is not valid, the HTTP status should be set to the appropriate error code.
	"""

	# Use `await req.json()` to access the request body
	data = await req.json()
	if "email" in data and data["email"] is None:
		print("null email")
		return JSONResponse(content="null", status_code=status.HTTP_400_BAD_REQUEST)
	existing_student = db.select("student", [], {"student_id": student_id})
	if not existing_student:
		print("not ecisiting student")
		return JSONResponse(content="wrong", status_code=status.HTTP_404_NOT_FOUND)

	if "email" in data:
		print("email in data")
		students_email = db.select("student", [], {"email": data["email"]})
		if any(student["student_id"] != student_id for student in students_email):
			print("dupe email")
			return JSONResponse(content="email dupe", status_code=status.HTTP_400_BAD_REQUEST)

	if "year" in data:
		try:
			years = int(data["year"])
			if years > 2023 or years < 2016:
				print("inval year")
				return JSONResponse(content="invalid year", status_code=status.HTTP_400_BAD_REQUEST)
		except ValueError:
			print("year not int")
			return JSONResponse(content="year not int", status_code=status.HTTP_400_BAD_REQUEST)

	try:
		count = db.update("student", data, {"student_id": student_id})
		return JSONResponse(content="success", status_code=status.HTTP_200_OK)

	except Exception as e:
		print("error")
		return JSONResponse(content="error", status_code=status.HTTP_400_BAD_REQUEST)


@app.delete("/students/{student_id}")
async def delete_student(student_id: int):
	"""Deletes a student.

	For instance,
		DELETE http://0.0.0.0:8002/students/1
	should delete the student with student ID 1.

	If the student does not exist, the HTTP status should be set to 404 Not Found.

	:param student_id: The ID of the student to be deleted
	:returns: If the request is valid, the HTTP status should be set to 200 OK.
				If the request is not valid, the HTTP status should be set to 404 Not Found.
	"""
	existing_student = db.select("student", [], {"student_id": student_id})
	if not existing_student:
		print("not ecisiting student")
		return JSONResponse(content="wrong", status_code=status.HTTP_404_NOT_FOUND)

	try:
		count = db.delete("student", {"student_id": student_id})
		return JSONResponse(content="success", status_code=status.HTTP_200_OK)

	except Exception as e:
		print("error")
		return JSONResponse(content="error", status_code=status.HTTP_404_NOT_FOUND)


# --- EMPLOYEES ---

@app.get("/employees")
async def get_employees(req: Request):
	"""Gets all employees that satisfy the specified query parameters.

	For instance,
		GET http://0.0.0.0:8002/employees
	should return all attributes for all employees.

	For instance,
		GET http://0.0.0.0:8002/employees?first_name=Don&last_name=Ferguson
	should return all attributes for employees whose first name is Don and last name is Ferguson.

	You must implement a special query parameter, `fields`. You can assume
	`fields` is a comma-separated list of attribute names. For instance,
		GET http://0.0.0.0:8002/employees?first_name=Don&fields=first_name,email
	should return the first name and email for employees whose first name is Don.
	Not every request will have a `fields` parameter.

	You can assume the query parameters are valid attribute names in the employee table
	(except `fields`).

	:param req: The request that optionally contains query parameters
	:returns: A list of dicts representing employees. The HTTP status should be set to 200 OK.
	"""

	# Use `dict(req.query_params)` to access query parameters
	param = dict(req.query_params)
	print(param)
	if len(param) > 0:
		fields = param.get('fields')
		param.pop('fields')
		rows = fields.split(",")
	else:
		rows = list()

	query1 = db.select("employee", rows, param)
	return query1

@app.get("/employees/{employee_id}")
async def get_employee(employee_id: int):
	"""Gets an employee by ID.

	For instance,
		GET http://0.0.0.0:8002/employees/1
	should return the employee with employee ID 1. The returned value should
	be a dict-like object, not a list.

	If the employee ID doesn't exist, the HTTP status should be set to 404 Not Found.

	:param employee_id: The ID to be matched
	:returns: If the employee ID exists, a dict representing the employee with HTTP status set to 200 OK.
				If the employee ID doesn't exist, the HTTP status should be set to 404 Not Found.
	"""
	existing_emp = db.select("employee", [], {"employee_id": employee_id})
	if existing_emp:
		return JSONResponse(content=existing_emp[0], status_code=status.HTTP_200_OK)
	else:
		print("here")
		return HTMLResponse(status_code=status.HTTP_404_NOT_FOUND)


@app.post("/employees")
async def post_employee(req: Request):
	"""Creates an employee.

	You can assume the body of the POST request is a JSON object that represents an employee.
	You can assume the request body contains only attributes found in the employee table and does not
	attempt to set `employee_id`.

	For instance,
		POST http://0.0.0.0:8002/employees
		{
			"first_name": "Don",
			"last_name": "Ferguson",
			...
		}
	should create an employee with the attributes specified in the request body.

	If the email is not specified in the request body, the HTTP status should be set to 400 Bad Request.
	If the email already exists in the employee table, the HTTP status should be set to 400 Bad Request.
	If the employee type is not valid, the HTTP status should be set to 400 Bad Request.

	:param req: The request, which contains an employee JSON in its body
	:returns: If the request is valid, the HTTP status should be set to 201 Created.
				If the request is not valid, the HTTP status should be set to 400 Bad Request.
	"""

	# Use `await req.json()` to access the request body
	data = await req.json()
	employment = data['employee_type'].lower()
	types = ['professor', 'lecturer', 'staff']
	if employment not in types:
		return HTMLResponse(status_code=status.HTTP_400_BAD_REQUEST)

	if "email" not in data.keys():
		return HTMLResponse(status_code=status.HTTP_400_BAD_REQUEST)
	existing_emp = db.select("employee", [], {"email": data["email"]})
	if existing_emp:
		print("are we here")
		return HTMLResponse(content="Email already exists", status_code=status.HTTP_400_BAD_REQUEST)
	if "middle_name" not in data.keys():
		data['middle_name'] = None
	try:
		db.insert("employee", data)
		return HTMLResponse(status_code=status.HTTP_201_CREATED)

	except pymysql.Error as e:

		return HTMLResponse(status_code=status.HTTP_400_BAD_REQUEST)

@app.put("/employees/{employee_id}")
async def put_employee(employee_id: int, req: Request):
	"""Updates an employee.

	You can assume the body of the PUT request is a JSON object that represents an employee.
	You can assume the request body contains only attributes found in the employee table and does not
	attempt to update `employee_id`.

	For instance,
		PUT http://0.0.0.0:8002/employees/1
		{
			"first_name": "Donald"
		}
	should update the employee with employee ID 1's first name to Donald.

	If the employee does not exist, the HTTP status should be set to 404 Not Found.
	If the email is set to null in the request body, the HTTP status should be set to 400 Bad Request.
	If the email already exists in the employee table, the HTTP status should be set to 400 Bad Request.
	If the employee type is not valid, the HTTP status should be set to 400 Bad Request.

	:param employee_id: The ID of the employee to be updated
	:param req: The request, which contains an employee JSON in its body
	:returns: If the request is valid, the HTTP status should be set to 200 OK.
				If the request is not valid, the HTTP status should be set to the appropriate error code.
	"""

	# Use `await req.json()` to access the request body
	data = await req.json()
	if "email" in data and data["email"] is None:
		return JSONResponse(content="null", status_code=status.HTTP_400_BAD_REQUEST)
	existing_emp = db.select("employee", [], {"employee_id": employee_id})
	if not existing_emp:
		return JSONResponse(content="wrong", status_code=status.HTTP_404_NOT_FOUND)

	if "email" in data:
		print("email in data")
		emp_email = db.select("student", [], {"email": data["email"]})
		if any(emp["employee_id"] != employee_id for emp in emp_email):
			return JSONResponse(content="email dupe", status_code=status.HTTP_400_BAD_REQUEST)

	if "employee_type" in data:
		try:
			emp = str(data['employee_type']).lower()
			types = ['professor', 'lecturer', 'staff']
			if emp not in types:
				return JSONResponse(content="invalid year", status_code=status.HTTP_400_BAD_REQUEST)
		except ValueError:
			return JSONResponse(content="must be string", status_code=status.HTTP_400_BAD_REQUEST)

	try:
		count = db.update("employee", data, {"employee_id": employee_id})
		return JSONResponse(content="success", status_code=status.HTTP_200_OK)

	except Exception as e:
		return JSONResponse(content="error", status_code=status.HTTP_400_BAD_REQUEST)

@app.delete("/employees/{employee_id}")
async def delete_employee(employee_id: int):
	"""Deletes an employee.

	For instance,
		DELETE http://0.0.0.0:8002/employees/1
	should delete the employee with employee ID 1.

	If the employee does not exist, the HTTP status should be set to 404 Not Found.

	:param employee_id: The ID of the employee to be deleted
	:returns: If the request is valid, the HTTP status should be set to 200 OK.
				If the request is not valid, the HTTP status should be set to 404 Not Found.
	"""
	existing_emp = db.select("employee", [], {"employee_id": employee_id})
	if not existing_emp:
		return JSONResponse(content="wrong", status_code=status.HTTP_404_NOT_FOUND)

	try:
		count = db.delete("employee", {"employee_id": employee_id})
		return JSONResponse(content="success", status_code=status.HTTP_200_OK)

	except Exception as e:
		return JSONResponse(content="error", status_code=status.HTTP_404_NOT_FOUND)


if __name__ == "__main__":
	uvicorn.run(app, host="0.0.0.0", port=8002)
