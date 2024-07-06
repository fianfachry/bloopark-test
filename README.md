# Odoo Custom Addons Docker Setup

This repository contains the necessary files to set up an Odoo environment with custom addons using Docker Compose. The custom addons are located in the `real_estate_x_complaint` folder.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- Docker
- Docker Compose

## Installation Instructions

### 1. Clone the Repository

Clone this repository to your local machine:

```bash
git clone https://github.com/fianfachry/bloopark-test.git
cd bloopark-test
```

### 2. Start the Docker Compose Services

Run the following command to start the Odoo and PostgreSQL services:

```bash
docker-compose up -d
```

This command will:
- Start the services defined in the `docker-compose.yml` file in detached mode (`-d`).

### 3. Access Odoo

Open your web browser and navigate to `http://localhost:8069`. You should see the Odoo login screen.

### 4. Install Custom Addons

Log in to your Odoo instance and go to the Apps menu. Click on the `Update Apps List` menu item. You should see your custom addon `real_estate_x_complaint` listed. Install the addon as you would any other Odoo app.

## Troubleshooting

If you encounter any issues, here are some common troubleshooting steps:

- **Check Container Logs**: You can check the logs of the running containers with:
  ```bash
  docker-compose logs
  ```

- **Shell Access to Container**: If you need to access the shell inside the Odoo container for debugging, run:
  ```bash
  docker-compose exec odoo bash
  ```

- **Restart Services**: If you need to restart the services, run:
  ```bash
  docker-compose restart
  ```

- **Remove and Rebuild Services**: If you need to remove the containers and start over, run:
  ```bash
  docker-compose down
  docker-compose up -d --build
  ```
