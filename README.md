# Cognitive Load Task Manager API

![Python](https://img.shields.io/badge/python-3.14-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.128-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

## Overview

A RESTful Task Management API built with FastAPI, designed with scalability in mind.

This project is built around the concept of **cognitive load**: the idea that productivity is limited not by the number of tasks, but by how they are mentally structured.

Instead of treating tasks as isolated items, this system models:

- Cognitive Load Modeling: Tasks are rated on a scale (1-3) to reflect mental effort.
- Task Fragmentation: Tasks may be marked as fragmentable.
- Explicit task states: (Pending, Active, Completed, Paused).

## Features

- User Authentication: Secure registration and JWT-based login.
- Task Management: CRUD foundation defined.
- Relational Modeling: 1:n relationship between Users and Tasks.
- Validation: Strict data validation using Pydantic V2.

## Endpoints

### User Authentication

- `POST /auth/register`: Register a new user.
- `POST /auth/login`: Login to obtain JWT token.

### Task Management (Authenticated)

- `POST /task`: Create a new task.
- `GET /tasks`: Retrieve all tasks (with pagination).
- `GET /tasks/{id}`: Get details of a specific task.
- `PATCH /tasks/{id}`: Update an existing task.
- `DELETE /tasks/{id}`: Delete a task.

## Getting Started

### Prerequisites

- Python 3.14+
- pip / virtualenv
- PostgreSQL (or any other database)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/brumalio/cognitive-task-api.git
   cd cognitive-task-api
   ```

2. Set up the environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configure environment variables:

   Copy the example file and update the values with your own:

   ```bash
   cp .env.example .env
   ```

4. Run the application:
   ```bash
   fastapi dev app/main.py
   ```

The interactive documentation will be at: `http://127.0.0.1:8000/docs`.

By default, the application runs in development mode. In development mode, database tables are created automatically on startup.

## Technical Focus

- RESTful API design
- Schema and relational modeling
- Authentication and authorization
- Clean architecture and separation of concerns
- Object-oriented programming (OOP) best practices

## Contributing

Contributions are welcome. If you'd like to improve this project or report issues, please submit a pull request or open an issue.
