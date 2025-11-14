# The Open Market
A Python-based full-stack e-commerce platform showcasing cart management, product listings, and secure checkout.

## How to run the application
### 1) create & activate a virtual env
cd ecommerce   
python -m venv venv  
  
*Windows:*  
venv\Scripts\activate  
*macOS / Linux:*  
source venv/bin/activate

### 2) install required dependencies
pip install -r requirements.txt

### 3) apply DB migrations
python manage.py migrate

### 4) (optional) create admin user
python manage.py createsuperuser

### 5) run the development server
python manage.py runserver

## Note
OS environment variables PAYPAL_CLIENT_ID and PAYPAL_SECRET need to be set for Paypal integration to function
