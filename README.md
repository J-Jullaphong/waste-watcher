# Waste Watcher

## Team Members
**Software and Knowledge Engineering, Kasetsart University**
- Jullaphong Jiamwatthanaloet 6510545314
- Phimnada Chirachotsuphaphat 6510545641

## Project Overview
This project aims to identify the relationship and impact of weather onto the waste production. We will use an ultrasonic sensor (HC-SR04) to measure the waste level in a bin, and integrate the gathered data with the weather data from the weather API. With these two sources of data, we will be able to see how the weather can affect the waste production, which can later be developed into solutions for the global waste problem.

## Features
1. **Real-time Waste Monitoring**: Retrieve bins and waste records along with weather conditions via API in real-time.
2. **Data Visualization**: Visualize waste records along with weather conditions using interactive charts.
3. **API Exploration with Swagger UI**: Explore the API endpoints easily and intuitively using Swagger UI.

## Required libraries and tools
- Python
- Django
- python-decouple
- djangorestframework
- mysqlclient
- Chart.js

## Installation Instruction
1. Clone the repository from GitHub.
```
git clone https://github.com/J-Jullaphong/waste-watcher.git
```
2. Change directory to waste-watcher.
```
cd waste-watcher
```
3. Import `data/data.sql` file to your SQL database hosting platform e.g. phpMyAdmin.
   >> Make sure to change the database name within this file before importing.
4. Create a virtual environment.
   ```
   python -m venv venv
   ```
   
5. Activate the virtual environment.
   - Linux and macOS
   ``` 
   source venv/bin/activate 
   ```
   - Windows
   ```  
   .\venv\Scripts\activate
   ```

6. Install Dependencies for required python modules.
   ```
   pip install -r requirements.txt
   ```
   
7. Create a .env file for externalized variables.
   - Linux and macOS
   ``` 
   cp sample.env .env 
   ```
   - Windows
   ```  
   copy sample.env .env
   ```
8. Use a text editor to edit the .env file according to your needs.
   >> For this project, you need to configure only the database related variables, while others can be ignored.
   ```
   - DB_NAME
   - DB_USER
   - DB_PASSWORD
   - DB_HOST
   - DB_PORT
   ```
9. Verify that the data is correctly imported to your database, and follow the `How to Run` instruction below to start the application.


## How to Run
1. Activate virtual environment
   - Linux and macOS
   ``` 
   source venv/bin/activate 
   ```
   - Windows
   ```  
   .\venv\Scripts\activate
   ```
2. Start the server. (If it doesn't work, please use `python3` instead of `python`)
   ```
   python manage.py runserver
   ```
3. To use this application, go to this link in your browser.
   ```
   http://localhost:8000
   ```

4. To close the running server, press `Ctrl+C` in your terminal or command prompt. 

5. After finish using the application, deactivate the virtual environment.
   ```
   deactivate
   ```
