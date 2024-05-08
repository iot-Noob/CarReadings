# OilChange API Documentation

## Installation and Setup

### Requirements
- Python 3.x
- FastAPI
- Uvicorn
- SQLite

### Installation Steps

1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Create and activate a new virtual environment using Conda or virtualenv.
4. Install the required dependencies from the `requirements.txt` file using pip.
`pip install -r requirements.txt`
5. Create a `.env` file in the project directory and add the following environment variables:
```env
DP_PATH=".\\OilData.db"
SECRET_KEY="your_secret_key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=44
SALT=""

```
### Starting the Project

1. Activate your virtual environment.
2. Run the provided batch script to start the server.
```batch
@echo off
call conda.bat activate network
timeout 10
call uvicorn main:app --host 192.168.1.12 --port 2024 --reload
timeout 90
cls
```
### Usage

- ***Login:*** Use the /login endpoint with a POST request to authenticate user credentials and obtain an access token.
- ***Signup:*** Use the /signup endpoint with a POST request to create a new user account.
- ***Delete Account:*** Send a DELETE request to /delete_account with the access token, password, and username to delete the user account.
- ***Update Profile:*** Send a PATCH request to /update_profile with the updated profile information and access token.
- ***Add Oil Info:*** Use the /AddOilInfo endpoint with a POST request to add basic oil information to the database.
- ***Update Oil Info:*** Send a PATCH request to /update_oil_info with the updated oil information and access token.
- ***Update License Number:*** Send a PATCH request to /update_license_number with the updated license information and access token.
- ***Get All Data:*** Access the /get_all endpoint with a GET request to retrieve all car data and oil-related information for the current user.
- ***Get Data by License Plate:*** Send a GET request to /get_by_licance with the license plate number and access token to retrieve oil data for the specified license plate.
 
### Security Features
- ***SECRET_KEY:*** Used for JWT token generation and should be kept secret.
- ***ALGORITHM:*** Algorithm used for JWT token encoding.
- ***ACCESS_TOKEN_EXPIRE_MINUTES***: Expiration time for access tokens.
- ***SALT:*** Salt value used for password hashing.
### Auto-Install Libraries

```
pip install -r requirements.txt
```

In this example, I've bolded the section titles, the section headings under "Usage", "Security Features", and "Auto-Install Libraries" for emphasis.

 created by IoT Noob talha@copyright 2024

