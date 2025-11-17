
# Client Management API 🚀

This project provides a comprehensive solution for managing client data, including creating, updating, deleting, and tracking client transactions. It features a FastAPI backend, a Vue.js frontend, and a PostgreSQL database, all orchestrated using Docker Compose for easy deployment and management. The API includes authentication, client management, and movement tracking functionalities.

## 🌟 Key Features

- **User Authentication:** Secure user registration and login using JWT tokens.
- **Client Management:** Create, read, update, and delete client records.
- **Transaction Tracking:** Record client transactions and update balances automatically.
- **API Endpoints:** Well-defined API endpoints for all client management operations.
- **Frontend Interface:** A Vue.js frontend for interacting with the API.
- **Database Persistence:** PostgreSQL database for persistent data storage.
- **Dockerized Deployment:** Easy deployment and management using Docker Compose.
- **Input Validation:** Robust data validation using Pydantic schemas.
- **Asynchronous Operations:** Utilizes FastAPI's asynchronous capabilities for efficient handling of requests.

## 🛠️ Tech Stack

- **Frontend:**
    - Vue.js
    - HTML
    - JavaScript
- **Backend:**
    - FastAPI
    - Python 3.12
    - Uvicorn
- **Database:**
    - PostgreSQL
    - Psycopg
- **API:**
    - Pydantic (for data validation)
- **Build & Deployment:**
    - Docker
    - Docker Compose
    - setuptools
- **Security:**
    - bcrypt (for password hashing)
    - OAuth2 (for authentication)
- **Other:**
    - python-dotenv (for environment variable management)
    - logging (for application logging)

## 📦 Getting Started

### Prerequisites

- Docker: [Install Docker](https://docs.docker.com/get-docker/)
- Docker Compose: [Install Docker Compose](https://docs.docker.com/compose/install/)
- Python 3.12

### Installation

1.  Clone the repository:

    ```bash
    git clone https://github.com/zuri3lc/client_mg
    cd client_mg
    ```

2.  Create a `.env` file in the root directory with the following variables:

    ```
    DB_NAME=<database_name>
    DB_USER=<database_user>
    DB_PASSWORD=<database_password>
    DB_HOST=db
    DB_PORT=5432
    SECRET_KEY=<your_secret_key>
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    ```

3.  Build and run the application using Docker Compose:

    ```bash
    docker-compose up --build
    ```

### Running Locally (Without Docker)

1.  Navigate to the project directory:

    ```bash
    cd <repository_directory>
    ```

2.  Create a virtual environment:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  Install the dependencies:

    ```bash
    pip install -r requirements.txt
    pip install -e .
    ```

4.  Set environment variables (either in `.env` file and load them, or directly in your shell):

    ```bash
    export DB_NAME=<database_name>
    export DB_USER=<database_user>
    export DB_PASSWORD=<database_password>
    export DB_HOST=localhost
    export DB_PORT=5432
    export SECRET_KEY=<your_secret_key>
    export ALGORITHM=HS256
    export ACCESS_TOKEN_EXPIRE_MINUTES=30
    ```

5.  Run the FastAPI application:

    ```bash
    uvicorn app.api_server:app --reload
    ```

6.  Run the Vue.js frontend (if applicable, assuming a standard Vue CLI project):

    ```bash
    cd frontend
    npm install # or yarn install
    npm run serve # or yarn serve
    ```

## 💻 Usage

1.  **API Endpoints:**

    -   `GET /`: Welcome message to verify server functionality.
    -   `POST /auth/login`: User login.
    -   `POST /auth/register`: User registration.
    -   `GET /clients/`: Retrieve all clients for the current user.
    -   `POST /clients/`: Create a new client.
    -   `GET /clients/{client_id}`: Retrieve a specific client's details.
    -   `PUT /clients/{client_id}`: Update an existing client.
    -   `PATCH /clients/{client_id}`: Update the status of an existing client.
    -   `DELETE /clients/{client_id}`: Delete a client.
    -   `POST /clients/{client_id}/movimientos`: Register a new transaction for a client.
    -   `POST /movs/all`: Synchronize all movements for the current user.

2.  **Frontend:**

    -   Access the frontend application in your browser at `http://localhost:8099` (or the port configured in `docker-compose.yml`).

## 📂 Project Structure

```
.
├── app
│   ├── api
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── clients.py
│   │   ├── movs.py
│   │   └── schemas.py
│   ├── __init__.py
│   ├── api_server.py
│   ├── auth.py
│   ├── client_management.py
│   ├── database.py
│   ├── main.py
│   ├── security.py
│   ├── user_interface.py
│   └── utils.py
├── docker-compose.yml
├── Dockerfile
├── frontend
│   ├── index.html
│   ├── ... (Vue.js project files)
├── README.md
├── requirements.txt
└── setup.py
```

## 📸 Screenshots

(Add screenshots of the application here)

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and commit them with descriptive messages.
4.  Submit a pull request.

## 📝 License

This project is licensed under the [MIT License](LICENSE).
