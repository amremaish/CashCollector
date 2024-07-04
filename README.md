# Cash Collector Application

## Overview

This project is a Cash Collection application with a RESTful backend and mobile and web frontends.
It manages tasks for Cash Collectors who collect cash from customers and deliver it to Managers. The project includes
features to ensure that Cash Collectors do not abuse the system.

## Features

1. **Database Models**:
    - `User`: Custom user model extending `AbstractUser` with roles for Cash Collectors and Managers.
    - `Customer`: Model to store customer details.
    - `Task`: Model to store tasks related to cash collection, including customer, amount due, collection status, and
      timestamps.

2. **Admin Interface**:
    - Manage users, customers, and tasks.
    - View status of tasks and Cash Collectors' freeze status.

3. **RESTful API**:
    - Endpoints to manage tasks, including creation, collection, delivery, and status checks.
    - JWT authentication for secure access.
    - API to generate CSV reports for tasks.

4. **CSV Output**:
    - Generate CSV reports for tasks with filters for completed, assigned, and delivered tasks.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/amremaish/CashCollector
    cd cash-collector
    ```
2. Create and activate a virtual environment:
   ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```
5. Create a superuser:
   ```bash
    python manage.py createsuperuser
   ```
6. Run the development server:
   ```bash
    python manage.py runserver
   ```

## Postman Collection
> You can view it from [here](/res/Cash%20Collector.postman_collection.json).
## Database Models

![alt text](/res/diagram.png)

# Authentication Endpoints

## Login

**Description**: Authenticate a user and obtain a token.  
**Method**: POST  
**Endpoint**: `/api/users/login`

```sh
curl -X POST http://localhost:8000/api/users/login \
-H "Content-Type: application/json" \
-d '{
  "username": "cash_collector",
  "password": "123456"
}'
```

## Current User

**Description**: Retrieve the current authenticated user’s details.  
**Method**: GET  
**Endpoint**: `/api/users/me`

```sh
curl -X GET http://localhost:8000/api/users/me \
-H "Authorization: Bearer <TOKEN>"
```

## Cash Collector status

**Description**: Retrieve Cash Collector status whether frozen or not 
**Method**: GET  
**Endpoint**: `/api/users/status`

```sh
curl -X GET 'http://localhost:8000/api/users/status' \
-H "Authorization: Bearer <TOKEN>"
```

## Add Cash Collector

**Description**: Add a new cash collector user.  
**Method**: PUT  
**Endpoint**: `/api/users/add/cash-collector`

```sh
curl -X PUT http://localhost:8000/api/users/add/cash-collector \
-H "Authorization: Bearer <TOKEN>" \
-H "Content-Type: application/json" \
-d '{
  "username": "cash_collector",
  "email": "cash_collector@test.com",
  "first_name": "Amr",
  "last_name": "Emaish",
  "password": "123456"
}'
```

## Sign Up Manager

**Description**: Sign up a new manager user.  
**Method**: PUT  
**Endpoint**: `/api/users/manager/signup`

```sh
curl -X PUT http://localhost:8000/api/users/manager/signup \
-H "Content-Type: application/json" \
-d '{
  "username": "manager",
  "email": "manager@test.com",
  "first_name": "Amr",
  "last_name": "Emaish",
  "password": "123456"
}'
```

# Customer Endpoints

## Add Customer

**Description**: Add a new customer.  
**Method**: PUT  
**Endpoint**: `/api/users/add/customer`

```sh
curl -X PUT http://localhost:8000/api/users/add/customer \
-H "Authorization: Bearer <TOKEN>" \
-H "Content-Type: application/json" \
-d '{
  "name": "test customer",
  "address": "Cairo / Egypt"
}'
```

## Get Customers

**Description**: Retrieve a list of customers with pagination.  
**Method**: GET  
**Endpoint**: `/api/users/customers?page=2&page_size=5`

```sh
curl -X GET http://localhost:8000/api/users/customers?page=2&page_size=5 \
-H "Authorization: Bearer <TOKEN>"
```

# Task Endpoints

## Add Task

**Description**: Add a new task for a customer.  
**Method**: PUT  
**Endpoint**: `/api/tasks/create`

```sh
curl -X PUT http://localhost:8000/api/tasks/create \
-H "Authorization: Bearer <TOKEN>" \
-H "Content-Type: application/json" \
-d '{
  "customer": 4
}'

```

## Get Tasks

**Description**: Retrieve a list of tasks with pagination.  
**Method**: GET  
**Endpoint**: `/api/tasks?page=1&page_size=5`

```sh
curl -X GET http://localhost:8000/api/tasks?page=1&page_size=5 \
-H "Authorization: Bearer <TOKEN>"
```

## Next Task

**Description**: Retrieve the next task.  
**Method**: GET  
**Endpoint**: `/api/tasks/next_task`

```sh
curl -X GET http://localhost:8000/api/tasks/next_task \
-H "Authorization: Bearer <TOKEN>"
```

## Collect Task

**Description**: Collect payment for a task.  
**Method**: POST  
**Endpoint**: `/api/tasks/19/collect`

```sh
curl -X POST http://localhost:8000/api/tasks/19/collect \
-H "Authorization: Bearer <TOKEN>" \
-H "Content-Type: application/json" \
-d '{
  "amount_due": 3000
}'
```

## Deliver Task

**Description**: Mark a task as delivered.  
**Method**: POST  
**Endpoint**: `/api/tasks/16/deliver`

```sh
curl -X POST http://localhost:8000/api/tasks/16/deliver \
-H "Authorization: Bearer <TOKEN>"
```

## Generate Tasks CSV

**Description**: Generate a CSV file for tasks.  
**Method**: GET  
**Endpoint**: `/api/tasks/generate_csv?assigned=1&delivered=1`

```sh
curl -X GET http://localhost:8000/api/tasks/generate_csv?assigned=1&delivered=1 \
-H "Authorization: Bearer <TOKEN>"
```

## Admin screenshots
![alt text](/res/admin1.png)
![alt text](/res/admin2.png)
![alt text](/res/admin3.png)



