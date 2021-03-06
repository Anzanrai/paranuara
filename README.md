## setup the environment
- clone the repo
    - `git clone git@github.com:Anzanrai/paranuara.git`
- I prefer setting up a separate virtual environment for every project I work on. So, install virtaulenv.
    - `sudo apt-get update`
    - `sudo apt-get install virtualenv`
- create a new virtual environment with python3 as default
    - command: `virtualenv -p python3 <environment_name>`
- activate the virtual environment
    - command: `source <path_to_virtual_env>/<environment_name>/bin/activate`
- change the directory to project root directory, and install the requirements with the help of requirements file.
    - command: `pip3 install -r requirements.txt`
- for this app, postgres database was used and settings of the django project has been updated accordingly
    - for postgres installation and database setup, please follow the steps from 
        #### Install the Components from the Ubuntu Repositories
        - `sudo apt-get update`
        - `sudo apt-get install python-pip python-dev libpq-dev postgresql postgresql-contrib`
        
        #### Create a Database and Database User
        - `sudo su - postgres`
        - `psql`
        - `CREATE database paranuadb`;
        - `CREATE USER paranuauser with password 'admin'`;
        - `ALTER ROLE paranuauser SET client_encoding TO 'utf8'`;
        - `ALTER ROLE paranuauser SET default_transaction_isolation TO 'read committed'`;
        - `ALTER ROLE paranuauser SET timezone TO 'UTC'`;
        - `ALTER ROLE paranuauser CREATEDB;<br/`>
    The last step provides permission to the user to createdb. This is required for the purpose of test db creation.
- change directory to project root folder and execute following command to make migrations
    - python3 manage.py makemigrations
    - python3 manage.py migrate

- initialize database with initial data:
    - `python3 manage.py initialize_db`
    - a command script has been written for the db initialization purpose located at api/management/commands, and 
    data in json format is located at api/management/commands/data/ folder.
    
- run server with the command  `python3 manage.py runserver` 


## api endpoints

### http://localhost:8000/api/employees/?company=<company_id>
Given a company, the API needs to return all their employees. Provide the appropriate solution if the company does not 
have any employees.

### http://localhost:8000/api/common-friends/?employee_one=<employee_one_id>&employee_two=<employee_two_id>
Given 2 people, provide their information (Name, Age, Address, phone) and the list of their friends in common which 
have brown eyes and are still alive.

### http://localhost:8000/api/employees/?employee=<index>/
Given 1 people, provide a list of fruits and vegetables they like. This endpoint must respect this interface for the 
output: `{"username": "Ahi", "age": "30", "fruits": ["banana", "apple"], "vegetables": ["beetroot", "lettuce"]}`

## test execution
- run the command `python3 manage.py test`