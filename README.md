
# ASMS - ASMA Management System

![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![Django](https://img.shields.io/badge/Django-5.2.16-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Language](https://img.shields.io/badge/Language-English%20%7C%20中文-blue.svg)

A modern, feature-rich management system built with Django, featuring internationalization support, a beautiful admin interface, and responsive design.

---

## 📋 Table of Contents  
  
- [About](#about)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Git Setup](#git-setup)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Internationalization](#internationalization)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## 🎯 About

ASMS (ASMA Management System) is a comprehensive management platform designed to provide a robust foundation for building business applications. It includes a modern frontend with Tailwind CSS, a powerful admin interface powered by Jazzmin, and built-in internationalization support for English and Simplified Chinese.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🌐 **Internationalization** | Full support for English and Simplified Chinese with dynamic language switching |
| 🎨 **Modern UI** | Beautiful responsive design using Tailwind CSS |
| 🛠️ **Admin Interface** | Feature-rich admin panel powered by Jazzmin |
| 📱 **Mobile Friendly** | Responsive layout optimized for all screen sizes |
| 🚀 **Fast Performance** | Optimized Django backend for high-speed performance |
| 🔒 **Security** | Built-in CSRF protection and password validation |
| 📝 **Logging** | Comprehensive logging system for debugging |
| 📊 **Product Management** | After-sales record management with Excel import/export |
| 📋 **Trial Management** | Trial item tracking with automatic expiration calculation |

---

## 🛠️ Tech Stack

### Backend
- **Framework**: Django 5.2.16
- **Database**: SQLite (default), supports PostgreSQL
- **Admin**: Django Jazzmin 3.0.5
- **Extensions**: Django Extensions 4.1
- **Excel**: openpyxl 3.1.5

### Frontend
- **CSS**: Tailwind CSS 3.x
- **JavaScript**: Alpine.js 3.x
- **Icons**: SVG Icons

### Development Tools
- **Debugger**: Werkzeug 3.1.8
- **Translation**: Django i18n

---

## 📦 Installation

### Prerequisites
- Python 3.10+
- pip (Python package manager)
- Virtual environment (recommended)

### Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ASMS
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv myenv
   ```

3. **Activate the virtual environment**
   - Windows: `myenv\Scripts\activate`
   - macOS/Linux: `source myenv/bin/activate`

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Create local settings**
   ```bash
   cp examples/local_settings.example ASMS/local_settings.py
   ```

6. **Edit local settings**
   ```bash
   # Update ASMS/local_settings.py with your configuration
   ```

7. **Run migrations**
   ```bash
   python manage.py migrate
   ```

8. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

---

## 🔗 Git Setup

### Configure Remote Repository
```bash
git remote set-url origin git@github.com:Pyxis-lab/ASMS.git
git remote -v
```

### Push to Branch
```bash
git push origin test
```

---

## 🚀 Usage

### Development Server
```bash
python manage.py runserver 0.0.0.0:8000
```

Visit `http://localhost:8000` in your browser.

### Admin Interface
Visit `http://localhost:8000/admin` and log in with your superuser credentials.

### Language Switching
Use the dropdown menu in the navigation bar to switch between English and Simplified Chinese.

---

## 📁 Project Structure

```
ASMS/
├── ASMS/                    # Main Django project
│   ├── __init__.py
│   ├── asgi.py              # ASGI configuration
│   ├── settings.py          # Django settings
│   ├── urls.py              # URL routing
│   ├── wsgi.py              # WSGI configuration
│   ├── logging.py           # Logging configuration
│   └── templatetags/        # Custom template tags
│       └── language_switcher.py
├── Home/                    # Home application
│   ├── __init__.py
│   ├── admin.py             # Admin configuration
│   ├── apps.py              # App configuration
│   ├── models.py            # Database models
│   ├── tests.py             # Test cases
│   ├── urls.py              # App URLs
│   ├── views.py             # View functions
│   └── templates/           # HTML templates
│       ├── Home/
│       │   ├── home.html
│       │   ├── about.html
│       │   └── login.html
│       └── base.html        # Base template
├── product/                 # After-sales management application
│   ├── __init__.py
│   ├── admin.py             # Admin configuration
│   ├── apps.py              # App configuration
│   ├── models.py            # AfterSalesRecord model
│   ├── tests.py             # Test cases
│   ├── urls.py              # App URLs
│   ├── views.py             # View functions (CRUD + Import/Export)
│   └── templates/           # HTML templates
│       └── product/
│           ├── aftersales_list.html
│           ├── aftersales_detail.html
│           ├── aftersales_form.html
│           ├── aftersales_import.html
│           ├── aftersales_confirm_delete.html
│           └── sort_icon.html
│   └── templatetags/        # Custom template tags
│       └── product_filters.py
├── TrialItem/               # Trial item management application
│   ├── __init__.py
│   ├── admin.py             # Admin configuration
│   ├── apps.py              # App configuration
│   ├── models.py            # TrialItem model
│   ├── tests.py             # Test cases
│   ├── views.py             # View functions
│   └── migrations/          # Database migrations
├── Accounts/                # User accounts application
│   ├── __init__.py
│   ├── admin.py             # Admin configuration
│   ├── apps.py              # App configuration
│   ├── models.py            # Account models
│   └── views.py             # View functions
├── locale/                  # Translation files
│   └── zh_Hans/
│       └── LC_MESSAGES/
│           ├── django.po    # Portable object file
│           └── django.mo    # Machine object file
├── examples/                # Configuration examples
│   ├── local_settings.example
│   ├── nginx.example
│   ├── service.example
│   └── uwsgi.example
├── staticfiles/             # Static files
│   └── images/
├── manage.py                # Django management script
├── requirements.txt         # Project dependencies
├── original.xlsx            # Sample Excel template
├── tailwind.config.js       # Tailwind CSS configuration
└── README.md                # This file
```

---

## 🌐 Internationalization

### Adding Translations

1. **Extract translation strings**
   ```bash
   python manage.py makemessages -l zh_Hans
   ```

2. **Edit the translation file**
   ```bash
   # Open locale/zh_Hans/LC_MESSAGES/django.po
   # Fill in the msgstr fields with Chinese translations
   ```

3. **Compile translations**
   ```bash
   python manage.py compilemessages
   ```

4. **Restart the server**
   ```bash
   python manage.py runserver
   ```

### Supported Languages
- English (`en`)
- Simplified Chinese (`zh-hans`)

---

## ⚙️ Configuration

### Local Settings

The `local_settings.py` file contains sensitive configuration:

```python
import os
from pathlib import Path
from django.core.management.utils import get_random_secret_key

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATICFILES_DIR = os.path.join(BASE_DIR, "staticfiles")
STATIC_DIR = os.path.join(BASE_DIR, "static")
MEDIA_DIR = os.path.join(BASE_DIR, "media")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_random_secret_key()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

# Database configuration (SQLite - default)
DB_CONFIG = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': 'db.sqlite3',
}

# Database configuration (PostgreSQL - uncomment to use)
# DB_CONFIG = {
#     'ENGINE': 'django.db.backends.postgresql',
#     'HOST': '127.0.0.1',
#     'PORT': 5432,
#     'NAME': '<database_name>',
#     'USER': '<db_user>',
#     'PASSWORD': '<db_password>'
# }
```

---

## 📤 Deployment

### Using uWSGI and Nginx

1. **Install uWSGI**
   ```bash
   pip install uwsgi
   ```

2. **Configure uWSGI**
   ```bash
   # Copy and modify examples/uwsgi.example
   ```

3. **Configure Nginx**
   ```bash
   # Copy and modify examples/nginx.example
   ```

4. **Create systemd service**
   ```bash
   # Copy and modify examples/service.example
   ```

### Environment Variables

You can override settings using environment variables:

| Variable | Description |
|----------|-------------|
| `TEMPLATES_DIR` | Templates directory |
| `STATICFILES_DIR` | Static files directory |
| `STATIC_DIR` | Static root directory |
| `MEDIA_DIR` | Media files directory |
| `LOGS_DIR` | Logs directory |
| `DISABLE_LOGGING` | Disable logging (for CI/CD) |

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
4. **Run tests**
   ```bash
   python manage.py test
   ```

5. **Commit your changes**
   ```bash
   git commit -m "Add your feature description"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**

### Code Guidelines
- Follow PEP 8 for Python code
- Use Django best practices
- Write meaningful commit messages
- Include tests for new features

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📧 Contact

For questions, suggestions, or support:

- **Email**: 2020tanvir1971@gmail.com
- **Project Link**: `https://github.com/pyxis-asms/asms`

---

## 🙏 Acknowledgments

- `https://www.djangoproject.com/` - The web framework for perfectionists with deadlines
- `https://tailwindcss.com/` - Utility-first CSS framework
- `https://django-jazzmin.readthedocs.io/` - Beautiful Django admin interface
- `https://alpinejs.dev/` - Lightweight JavaScript framework

---

*Built with ❤️ by Pyxis ASMA*
```

The **Git Setup** section has been added between **Installation** and **Usage**, and the Table of Contents includes the new entry.