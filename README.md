# ISE Lab 2: CI/CD Moon Group
GCP-deloyment Link: https://hat-plug-64058716019.us-central1.run.app/

A Streamlit-based web application demonstrating CI/CD practices
including automated testing, containerization, and deployment using
GitHub Actions. This project was developed as part of the CodePath Tech
Exchange Integrated Software Engineering (ISE) Lab 2.

------------------------------------------------------------------------

## Overview

This project showcases modern software development practices including
continuous integration, continuous deployment, automated testing, and
containerization. The application provides a Streamlit web interface
supported by modular backend components and a CI/CD pipeline.

------------------------------------------------------------------------

## Features

-   **Streamlit Web Interface** -- Interactive frontend for displaying
    application data\
-   **Data Fetching Module** -- Handles data retrieval and processing\
-   **Automated Testing** -- Test suites written using pytest\
-   **Docker Containerization** -- Docker configuration for consistent
    environments\
-   **CI/CD Pipeline** -- GitHub Actions used for automated testing and
    deployment\
-   **Modular Architecture** -- Organized project structure separating
    frontend, backend, and utilities

------------------------------------------------------------------------

## Project Structure

    ise-lab2-cicd-moongroup/
    ├── app.py                 # Main Streamlit application
    ├── data_fetcher.py        # Data fetching and processing module
    ├── modules.py             # Core business logic and utilities
    ├── internals.py           # Internal helper functions
    ├── Dockerfile             # Docker container configuration
    ├── requirements.txt       # Python dependencies
    ├── setup.sh               # Environment setup script
    ├── manual-deploy.sh       # Manual deployment script
    ├── run-streamlit.sh       # Script to run Streamlit app
    ├── data_fetcher_test.py   # Tests for data_fetcher module
    ├── modules_test.py        # Tests for modules
    ├── .github/               # GitHub Actions workflows
    ├── .streamlit/            # Streamlit configuration
    ├── assets/                # Static assets (images, etc.)
    ├── custom_components/     # Custom Streamlit components
    ├── mockups/               # UI mockups and design sketches
    ├── SETUP.md               # Setup documentation
    └── LICENSE                # MIT License

------------------------------------------------------------------------

## Tech Stack

-   Python 3.x
-   Streamlit
-   Docker
-   GitHub Actions
-   pytest
-   Git

------------------------------------------------------------------------

## Prerequisites

-   Python 3.7 or higher
-   Docker (optional for containerized deployment)
-   Git
-   pip (Python package manager)

------------------------------------------------------------------------

## Installation

### Clone the Repository

``` bash
git clone https://github.com/CodePath-Tech-Exchange-CTEx/ise-lab2-cicd-moongroup.git
cd ise-lab2-cicd-moongroup
```

### Run Setup Script

``` bash
bash setup.sh
```

### Install Dependencies

``` bash
pip install -r requirements.txt
```

------------------------------------------------------------------------

## Running the Application

Start the Streamlit application with:

``` bash
streamlit run app.py
```

Or run the provided script:

``` bash
bash run-streamlit.sh
```

The application will be available at:

http://localhost:8501

------------------------------------------------------------------------

## Running Tests

Run individual tests:

``` bash
python -m pytest data_fetcher_test.py -v
python -m pytest modules_test.py -v
```

Run all tests:

``` bash
python -m pytest -v
```

------------------------------------------------------------------------

## Deployment

### Manual Deployment

``` bash
bash manual-deploy.sh
```

### Docker Deployment

Build the container:

``` bash
docker build -t ise-lab2-cicd .
```

Run the container:

``` bash
docker run -p 8501:8501 ise-lab2-cicd
```

------------------------------------------------------------------------

## CI/CD Pipeline

The project uses GitHub Actions to automate development workflows. The
pipeline automatically:

-   Runs tests when code is pushed
-   Validates pull requests
-   Builds the application environment
-   Supports containerized deployment

Workflow configuration files are located in:

.github/workflows/

------------------------------------------------------------------------

## Project Modules

### app.py

Main Streamlit application responsible for the user interface.

### data_fetcher.py

Handles data retrieval, validation, and transformation.

### modules.py

Contains core business logic and utility functions.

### internals.py

Internal helper functions used across modules.

------------------------------------------------------------------------

## Configuration

Streamlit configuration files are located in the `.streamlit/`
directory.

Additional setup instructions and environment configuration details can
be found in:

SETUP.md

------------------------------------------------------------------------

## Development Workflow

Team members developed features using separate branches and merged
changes into the main branch after testing. GitHub Actions automatically
ran tests and validation checks on each update.

------------------------------------------------------------------------

## Team

Moon Group -- CodePath Tech Exchange\
Integrated Software Engineering Lab 2

------------------------------------------------------------------------

## License

This project is licensed under the MIT License. See the LICENSE file for
details.

------------------------------------------------------------------------

**Project:** CodePath Tech Exchange -- Integrated Software Engineering
Lab 2\
**Last Updated:** March 2026
