# 🚗 Vehicle Parking App - V2

A robust, multi-user parking management system designed specifically for 4-wheeler vehicles. This application features distinct roles for administrators and regular users, real-time parking status updates, and a suite of automated backend jobs for enhanced functionality and user engagement.

## Table of Contents

* [Introduction](#introduction)
* [Features](#features)
    * [Admin Dashboard](#admin-dashboard)
    * [User Dashboard](#user-dashboard)
    * [Backend Jobs](#backend-jobs)
    * [Performance & Caching](#performance--caching)
* [Technologies Used](#technologies-used)
* [Authentication](#authentication)
* [Database Schema (Conceptual)](#database-schema-conceptual)
* [Setup & Installation](#setup--installation)
* [Usage](#usage)
* [Screenshots & Demo Video](#screenshots--demo-video)
* [Contributing](#contributing)
* [License](#license)

## Introduction

The Vehicle Parking App - V2 aims to streamline the process of managing parking lots, individual parking spots, and parked vehicles. It provides a clear distinction between administrative controls and user functionalities, ensuring efficient operations and a seamless parking experience.

## Features

### Admin Dashboard

The administrator has comprehensive control over the parking system, allowing for efficient management of lots and monitoring of parking status.

* **Login & Registration:** Secure login for the administrator. The admin account is programmatically added upon initial database creation.
* **Parking Lot Management:**
    * Create, edit, and delete parking lots.
    * **Note:** Parking lots can only be deleted if all their associated parking spots are empty.
* **Automated Parking Spot Creation:** Parking spots are automatically generated based on the maximum number of spots defined for a lot, eliminating manual individual spot creation.
* **Real-time Status Monitoring:** View the current status of all parking spots (occupied/empty) and detailed information about parked vehicles when a spot is occupied.
* **User Management:** Access a list of all registered users within the system.
* **Summary Charts:** Visual summaries of parking lot and spot utilization for insightful decision-making.

**GIF Placeholder:** Admin Dashboard Overview (e.g., showing lot creation, spot status, and user list).
![Admin Dashboard Overview](https://placehold.co/600x400/000000/FFFFFF?text=Admin+Dashboard+Overview+GIF)

**GIF Placeholder:** Creating a Parking Lot (e.g., showing the form submission and new lot appearing).
![Creating a Parking Lot](https://placehold.co/600x400/000000/FFFFFF?text=Create+Parking+Lot+GIF)

### User Dashboard

Users can easily find and manage their parking needs with an intuitive interface.

* **Login & Registration:** Secure login and registration forms for new users.
* **Automated Parking Allocation:** Users select an available parking lot, and the system automatically allocates the first available parking spot. Users cannot manually select a specific spot.
* **Parking Status Management:**
    * Users can mark a parking spot as `occupied` once their vehicle is parked.
    * Users can mark a parking spot as `released` once their vehicle has moved out.
* **Timestamp Recording:** The application automatically records the `park-in` and `park-out` timestamps for each parking session.
* **Personal Parking Summary:** Users can view summary charts related to their own parking history and activity.

**GIF Placeholder:** User Parking Flow (e.g., showing selecting a lot, parking, and unparking).
![User Parking Flow](https://placehold.co/600x400/000000/FFFFFF?text=User+Parking+Flow+GIF)

**GIF Placeholder:** Viewing Personal Summary (e.g., showing the user's parking history charts).
![Viewing Personal Summary](https://placehold.co/600x400/000000/FFFFFF?text=Personal+Summary+GIF)

### Backend Jobs

The application leverages background jobs for various automated tasks, enhancing user engagement and providing valuable insights.

#### a. Scheduled Job - Daily Reminders

* **Purpose:** To remind users who haven't visited or to alert about newly created parking lots.
* **Trigger:** Runs daily (time configurable by students).
* **Logic:** Checks if a user has not visited the app recently or if new parking lots have been added by the admin.
* **Action:** Sends alerts asking users to book a parking spot if required.
* **Delivery:** Via Google Chat Webhooks, SMS, or email.

**GIF Placeholder:** Daily Reminder Notification Example (e.g., a mock Google Chat/SMS/Email notification).
![Daily Reminder Notification](https://placehold.co/600x400/000000/FFFFFF?text=Daily+Reminder+GIF)

#### b. Scheduled Job - Monthly Activity Report

* **Purpose:** To provide users with a comprehensive summary of their parking activity.
* **Trigger:** Runs on the first day of every month.
* **Content:** Generates an HTML report including:
    * Parking spots booked per month.
    * Most used parking lot by the user.
    * Amount spent on parking for the month.
    * Any other relevant user-specific parking information.
* **Delivery:** Sent as an email to the user.

**GIF Placeholder:** Monthly Report Email Example (e.g., a mock email showing the HTML report).
![Monthly Report Email](https://placehold.co/600x400/000000/FFFFFF?text=Monthly+Report+GIF)

#### c. User Triggered Async Job - Export as CSV

* **Purpose:** To allow users to download their historical parking details.
* **Trigger:** Initiated by the user from their dashboard.
* **Content:** Exports parking details in CSV format, including:
    * `slot_id`
    * `spot_id`
    * `timestamps` (park-in, park-out)
    * `cost`
    * `remarks`
    * And other relevant information.
* **Process:** Triggers a batch job in the background.
* **Notification:** Sends an alert to the user once the CSV export is complete and ready for download.

**GIF Placeholder:** CSV Export Trigger and Notification (e.g., showing the button click, a loading state, and a "download ready" notification).
![CSV Export Trigger](https://placehold.co/600x400/000000/FFFFFF?text=CSV+Export+GIF)

### Performance & Caching

* **Caching Strategy:** Implemented caching mechanisms using Redis to store frequently accessed data, significantly improving application response times.
* **Cache Expiry:** Configured cache expiry policies to ensure data freshness and efficient resource utilization.
* **API Performance:** Focus on optimizing API endpoints for quick and reliable data retrieval and submission.

## Technologies Used

This project is built upon a robust stack of mandatory frameworks and tools:

* **Backend:**
    * **[Flask](https://flask.palletsprojects.com/):** A lightweight Python web framework used for building the API.
    * **[SQLite](https://www.sqlite.org/):** A self-contained, high-reliability, embedded, full-featured, public-domain SQL database engine.
    * **[Redis](https://redis.io/):** An open-source, in-memory data structure store, used as a database, cache, and message broker.
    * **[Celery](https://docs.celeryq.dev/):** An asynchronous task queue/job queue based on distributed message passing, used for handling background jobs.
* **Frontend:**
    * **[Vue.js](https://vuejs.org/):** A progressive JavaScript framework for building user interfaces.
    * **[Bootstrap](https://getbootstrap.com/):** The world's most popular front-end open source toolkit, used for HTML generation and styling.
    * **[Jinja2](https://jinja.palletsprojects.com/):** A modern and designer-friendly templating language for Python, used only for the application's entry point (`index.html`).

## Authentication

The application implements a robust role-based access control system to differentiate between administrators and regular users. This is achieved using **JWT (JSON Web Token) based Token Authentication**, ensuring secure and stateless user sessions.

## Database Schema (Conceptual)

The application's data is structured across several key models to manage users, parking lots, spots, and vehicle parking events.

* `User`: Stores user credentials and roles.
    * `id` (Primary Key)
    * `username`
    * `password_hash`
    * `role` (e.g., 'admin', 'user')
    * `email`
* `ParkingLot`: Defines different parking areas.
    * `id` (Primary Key)
    * `name`
    * `location`
    * `total_spots`
* `ParkingSpot`: Represents individual parking spaces within a lot.
    * `id` (Primary Key)
    * `lot_id` (Foreign Key to `ParkingLot`)
    * `spot_number`
    * `status` (e.g., 'empty', 'occupied')
    * `vehicle_id` (Foreign Key to `ParkedVehicle` if occupied, nullable)
* `ParkedVehicle`: Records details of a vehicle currently or previously parked.
    * `id` (Primary Key)
    * `user_id` (Foreign Key to `User`)
    * `spot_id` (Foreign Key to `ParkingSpot`)
    * `vehicle_number`
    * `park_in_time` (Timestamp)
    * `park_out_time` (Timestamp, nullable)
    * `cost`
    * `remarks`

**Note:** The database must be created programmatically (via table creation or model code) or through a shell script. Manual database creation (e.g., using DB Browser for SQLite) is strictly prohibited.

## Setup & Installation

Follow these steps to get the Vehicle Parking App - V2 up and running on your local machine.

### Prerequisites

Before you begin, ensure you have the following installed:

* **Python 3.x**
* **Node.js** (LTS version recommended)
* **npm** or **Yarn** (package manager for Node.js)
* **Redis Server** (running locally or accessible)
* **Go** (for MailHog setup)

### 1. Clone the Repository

```bash
git clone <repository_url>
cd vehicle-parking-app-v2

### 2\. Backend Setup (Flask, SQLite, Redis, Celery) on WSL

**It is highly recommended to run the backend components (Flask, Redis, Celery) within a Windows Subsystem for Linux (WSL) environment due to dependencies and better compatibility.**

Navigate to the `backend` directory and set up the Python environment within your WSL terminal.

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Initialize and create the database (this will also add the default admin user):

```bash
# Assuming you have Flask-Migrate or similar setup, or a script for DB creation
flask db upgrade # Or run your custom database creation script
```

Start the Flask API server:

```bash
python3 app.py
# For production, consider Gunicorn or Waitress
```

Start the Redis server (if not already running on WSL):

```bash
sudo service redis-server start # Or your specific Redis start command
```

Start the Celery worker and beat for background jobs (in separate WSL terminals, after activating your venv):

```bash
# For worker
celery -A app.celery worker -l info
# For beat (scheduled tasks)
celery -A app.celery beat -l info
```

### 3\. Mail Service Setup (MailHog) on WSL

MailHog is used for catching emails during development. It requires Go to be installed.

1.  **Install Go on WSL:**
    ```bash
    sudo apt update
    sudo apt install golang-go
    ```
2.  **Install MailHog:**
    ```bash
    go install [github.com/mailhog/MailHog@latest](https://github.com/mailhog/MailHog@latest)
    ```
3.  **Run MailHog:**
    ```bash
    ~/go/bin/MailHog
    ```
    MailHog will typically run on `http://localhost:8025` for the web UI and `http://localhost:1025` for the SMTP server. Configure your Flask application to send emails to `localhost:1025`.

### 4\. Frontend Setup (Vue.js, Bootstrap)

Navigate to the `frontend` directory and install Node.js dependencies.

```bash
cd ../frontend
npm install # or yarn install
```

Start the Vue.js development server:

```bash
npm run serve # or yarn serve
```

The frontend application should now be accessible, typically at `http://localhost:8080`.

## Usage

  * **Admin Access:** Navigate to `/admin` (or the configured admin route) to log in as the administrator. From here, you can manage parking lots, view user details, and monitor the system.
  * **User Access:** Register a new user account or log in with existing credentials. Users can then find available parking, manage their parking sessions, and export their parking history.

## Screenshots & Demo Video

This section will contain screenshots of the application's key features and a demo video showcasing its functionality.

  * **Screenshot 1:** [Description of Screenshot 1]
  * **Screenshot 2:** [Description of Screenshot 2]
  * **Demo Video:** [Link to Demo Video]

## Contributing

Contributions are welcome\! Please fork the repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change. Read [CONTRIBUTING](CONTRIBUTING.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
