# Gym Web Application

This is a Flask-based Gym Management Application with a PostgreSQL backend.

## Prerequisites

Before running the application, ensure you have the following installed on your machine:

1.  **Python 3.x**: [Download Python](https://www.python.org/downloads/)
2.  **PostgreSQL**: [Download PostgreSQL](https://www.postgresql.org/download/)
    *   Make sure the PostgreSQL service is running.
    *   Create a user named `postgres` (default) or update `setup_postgres.py` and `main.py` with your credentials.

## Installation

1.  **Unzip the project** to a folder.
2.  **Open a terminal** in that folder.
3.  **Create a virtual environment**:
    ```bash
    python3 -m venv .venv
    ```
4.  **Activate the virtual environment**:
    *   Mac/Linux:
        ```bash
        source .venv/bin/activate
        ```
    *   Windows:
        ```bash
        .venv\Scripts\activate
        ```
5.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Database Setup

1.  **Run the setup script** to create the database (`gym_db`) and populate it with sample data:
    ```bash
    python3 setup_postgres.py
    ```
    *   *Note: This will create tables for Users, Trainers, Lessons, Articles, BMI Records, and Reservations.*

## Running the Application

1.  **Start the Flask server**:
    ```bash
    python3 main.py
    ```
2.  **Open your browser** and go to:
    [http://127.0.0.1:5001](http://127.0.0.1:5001)

## Features

*   **User Authentication**: Register and Login.
*   **BMI Calculator**: Calculate and save your BMI history.
*   **User Dashboard**: View your weight progress chart.
*   **Interactive Map**: Find clubs near you.
*   **Group Lessons**: View schedule and make reservations.
