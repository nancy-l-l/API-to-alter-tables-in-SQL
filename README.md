main.py declares our API and defines paths for it
The @app decorator above each method describes the HTTP method and the path associated with that method
Implements the ten endpoints in main.py: get_students, get_student, post_student, put_student, delete_student, get_employees, get_employee, post_employee, put_employee, and delete_employee

dp.py implements eight methods that are used to interact with a database in SQL: build_select_query, select, build_insert_query, insert, build_update_query, update, build_delete_query, and delete

