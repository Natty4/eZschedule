
<div align="center">
  <img src="https://raw.githubusercontent.com/natty4/eZschedule/main/static/images/logo.png" alt="Logo" width="200" height="200">
  <h1>EasySchedule</h1>
</div>
    <p>A simple and easy-to-use appointment booking and payment solution.</p>
    <p>Built with Python and Django, EasySchedule is an open-source project that simplifies appointment management for businesses and their customers.</p>
    <p>Join us in building a scalable and extensible solution for appointment management.</p>
    <p>Contributors of all skill levels are welcome!</p>
    <p>Check out the <a href="https://ezgo-ekrp.onrender.com/">Demo</a>



# EasySchedule: Open-Source Appointment Booking and Payment Solution

EasySchedule is a robust, user-friendly web application designed to simplify appointment booking and payment handling for businesses and their customers. Built with Python and Django, it integrates seamlessly with external APIs like Chapa for secure payment processing. EasySchedule is open-source and licensed under the GNU General Public License v3.0, making it free to use, modify, and distribute. We welcome contributors of all skill levels to join us in building a scalable and extensible solution for appointment management.

---

## Table of Contents

- [Features](#-features)
2. [Installation Instructions](#-installation-instructions)
3. [Usage](#-usage)
4. [Contributing Guidelines](#-contributing-guidelines)
5. [License Information](#-license-information)
6. [Contact Information](#-contact-information)
7. [Acknowledgments](#-acknowledgments)
8. [Call to Action](#-call-to-action)
9. [Demo](#demo)

---

## Features

- **Appointment Booking**: A streamlined process for scheduling appointments with businesses and professionals.
- **Payment Integration**: Secure payment handling via Chapa and other payment gateways.
- **User Management**: Role-based access control for customers, business owners, and administrators.
- **Customizable Services**: Businesses can define services, durations, and pricing.
- **Dynamic Availability**: Real-time availability tracking for professionals and services.
- **QR Code Integration**: Generate QR codes for appointments for easy verification.
- **Scalable Architecture**: Built with Django, ensuring scalability and maintainability.
- **Cloud Storage**: Media and QR codes are stored securely using Cloudinary.
- **Logging and Debugging**: Advanced logging with color-coded output for easier debugging.

---

## Installation Instructions

### Prerequisites

- Python 3.8 or higher
- PostgreSQL or SQLite (for local development)
- Git

### Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/natty4/eZschedule.git
   cd easyschedule
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**:
   Create a .env file in the root directory and configure the following:
   ```env
   DJANGO_SECRET_KEY=your_secret_key
   DEBUG=True
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=your_db_name
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=localhost
   DB_PORT=5432
   CLOUDINARY_CLOUD_NAME=your_cloudinary_name
   CLOUDINARY_API_KEY=your_cloudinary_api_key
   CLOUDINARY_API_SECRET=your_cloudinary_api_secret
   ```

5. **Apply Migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Run the Development Server**:
   ```bash
   python manage.py runserver
   ```

7. **Access the Application**:
   Open your browser and navigate to `http://127.0.0.1:8000`.

---

## Usage

### Sample Commands

- **Create a Superuser**:
  ```bash
  python manage.py createsuperuser
  ```
- **Run Tests**:
  ```bash
  python manage.py test
  ```

### API Endpoints

- **List Businesses**: `GET /api/businesses/`
- **Book an Appointment**: `POST /api/reserve/slot/`
- **Confirm Payment & booking**: `POST /api/booking/confirm/`

### Frontend Workflows

1. Navigate to the homepage to browse businesses and services.
2. Select a service and choose an available time slot.
3. Complete the booking form and proceed to payment.
4. Receive a confirmation email with appointment details and a QR code.

---

## Contributing Guidelines

We welcome contributions from everyone! Here's how you can get involved:

1. **Fork the Repository**:
   Click the "Fork" button on GitHub to create your copy of the repository.

2. **Create a Feature Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Changes**:
   Follow the coding standards and document your code where necessary.

4. **Submit a Pull Request**:
   Push your changes to your fork and create a pull request on the main repository.

5. **Report Issues**:
   Use the GitHub Issues tab to report bugs or suggest features.

### Coding Standards

- Follow PEP 8 for Python code.
- Write clear and concise commit messages.
- Include tests for new features or bug fixes.

---

## License Information

This project is licensed under the **GNU General Public License v3.0**. This means:

- You are free to use, modify, and distribute the software.
- Any derivative work must also be open-source and licensed under the same terms.

For more details, see the LICENSE file.

---

## Contact Information

For questions or support, feel free to reach out:

- **Contact**: @Natty4
- **GitHub Issues**: [GitHub Issues](https://github.com/natty4/eZschedule/issues)

---

## Acknowledgments

- **Django**: The web framework that powers this application.
- **Chapa**: For seamless payment integration.
- **Cloudinary**: For secure media storage.
- **Contributors**: A heartfelt thanks to everyone who has contributed to this project ! (Currently, <a href="https://github.com/natty4/eZschedule/graphs/contributors">Me 🤓</a> is the sole contributor.)

---

## Call to Action

We believe in the power of open-source and the strength of community. Whether you're a seasoned developer or just starting out, your contributions are valuable. Join us in making EasySchedule the go-to solution for appointment booking and payment management. Together, we can build something extraordinary!

**Start contributing today!** 😊

---
Built with 💙   •
  <a href="https://github.com/natty4/eZschedule">GitHub</a> •
  <a href="https://ezgo-ekrp.onrender.com/">Demo</a> •
  <a href="#">Contact</a>
</div>