# **Faculty Information System**

## **Project Description**
The Faculty Information System is designed to manage the details of faculty members, with a particular focus on their publications and journals. This system offers an easy-to-access user interface that allows users to gather insights about faculty publications and manage all related records efficiently.

## **Features**
- User-friendly interface
- Detailed insights about faculty publications
- Comprehensive management of faculty records

## **Installation Instructions**

### **Pre-Requisites**
- Install Git Version Control: [Git Download](https://git-scm.com/)
- Install Python Latest Version: [Python Download](https://www.python.org/downloads/)

### **Installation of Project**

1. Create a folder where you want to save the project.

2. Install Virtual Environment:
   ```bash
   pip install virtualenv
   ```

3. Create Virtual Environment:
   - For Windows:
     ```bash
     python -m venv venv
     ```
   - For Mac:
     ```bash
     python3 -m venv venv
     ```

4. Activate Virtual Environment:
   - For Windows:
     ```bash
     source venv/scripts/activate
     ```
   - For Mac:
     ```bash
     source venv/bin/activate
     ```

5. Clone this project:
   ```bash
   git clone https://github.com/abishek25s/Faculty-Information-System
   ```

6. Enter the project directory:
   ```bash
   cd Faculty-Information-System
   ```

7. Install Requirements from `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

8. Add the hosts:
   - Go to `settings.py` file.
   - On allowed hosts, add `['*']`.
     ```python
     ALLOWED_HOSTS = ['*']
     ```

9. Run the server:
   ```bash
   python manage.py runserver
   ```

### **Login Credentials**
- **Admin:**
  - Email: `admin@gmail.com`
  - Password: `admin`
- **Staff:**
  - Email: `staff1@gmail.com`
  - Password: `1234`

## **Contact Information**
For any questions or inquiries, please contact:
- Email: [abisheks2505@gmail.com](mailto:abisheks2505@gmail.com)
