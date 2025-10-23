# EcommerceWebsite
An Ecommerce website created using Python.

## How to run the application
### 1) create & activate a virtual env
cd ecommerce
python -m venv venv  
  
Windows:  
venv\Scripts\activate  
macOS / Linux:  
source venv/bin/activate

### 2) install Django and Pillow (ImageField requires Pillow)
pip install django pillow

### 3) apply DB migrations
python manage.py migrate

### 4) (optional) create admin user
python manage.py createsuperuser

### 5) run the development server
python manage.py runserver
