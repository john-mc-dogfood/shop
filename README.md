# E-commerce Monolith

A simple e-commerce backend built with **FastAPI** demonstrating monolithic architecture. The application provides a complete set of RESTful APIs for managing users, products, orders, inventory, and generating business reports.

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Domain Modules](#domain-modules)
- [Database Models](#database-models)
- [API Reference](#api-reference)
  - [Root](#root)
  - [Users](#users)
  - [Categories](#categories)
  - [Products](#products)
  - [Orders](#orders)
  - [Inventory](#inventory)
  - [Reports](#reports)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Server](#running-the-server)
- [Usage Examples](#usage-examples)
- [Development](#development)

## Overview

This is a monolithic FastAPI application organized into five domain modules:

| Module | Description |
|--------|-------------|
| **Users** | User registration and account management |
| **Products** | Product catalog with category support |
| **Orders** | Order creation with multi-item support and inventory reservation |
| **Inventory** | Stock tracking, quantity updates, and reservation management |
| **Reports** | Business intelligence reports (sales, inventory, product/category performance, user activity) |

All modules share a single SQLite database and a unified set of SQLModel/SQLAlchemy models, communicating through direct database access.

## Tech Stack

| Technology | Purpose |
|-----------|---------|
| [FastAPI](https://fastapi.tiangolo.com/) 0.115 | Async web framework |
| [SQLModel](https://sqlmodel.tiangolo.com/) 0.0.22 | ORM combining SQLAlchemy and Pydantic |
| [SQLAlchemy](https://www.sqlalchemy.org/) (async) | Async database engine |
| [aiosqlite](https://github.com/omnilib/aiosqlite) 0.22 | Async SQLite driver |
| [Uvicorn](https://www.uvicorn.org/) 0.32 | ASGI server |
| [python-multipart](https://github.com/Kludex/python-multipart) 0.0.12 | Form data parsing |

## Project Structure

```
shop/
├── README.md
├── requirements.txt          # Python dependencies
├── run_local.py              # Development server entry point
└── src/
    └── ecommerce/
        ├── __init__.py
        ├── main.py           # FastAPI app, lifespan, router registration
        ├── database.py       # Async engine, session management, DB init
        ├── models.py         # All SQLModel table definitions
        ├── users/
        │   ├── __init__.py
        │   └── api.py        # User CRUD endpoints
        ├── products/
        │   ├── __init__.py
        │   └── api.py        # Product & category endpoints
        ├── orders/
        │   ├── __init__.py
        │   └── api.py        # Order creation & retrieval endpoints
        ├── inventory/
        │   ├── __init__.py
        │   └── api.py        # Inventory query, update & reservation endpoints
        └── reports/
            ├── __init__.py
            └── api.py        # Reporting & analytics endpoints
```

## Domain Modules

### Users

Handles user registration and retrieval. Each user has an email (unique), name, and creation timestamp.

### Products

Manages the product catalog. Products belong to categories and have a name, description, price, and creation timestamp. Creating a product automatically initializes an inventory record with zero stock.

### Orders

Supports creating orders with multiple line items. During order creation the system validates that the user exists, all products exist, and sufficient inventory is available. Inventory is automatically reserved for each order item. Orders track status (`pending`, `confirmed`, `shipped`, `delivered`) and total amount.

### Inventory

Provides direct control over product stock levels. Supports querying current inventory, setting absolute quantity, and reserving units. Each inventory record tracks total quantity, reserved quantity, and a last-updated timestamp.

### Reports

Generates read-only business intelligence reports that aggregate data across all other domains:

- **Sales report** -- total revenue, order count, average order value, and counts by status.
- **Inventory report** -- total stock, reserved/available breakdown, and low-stock product count (configurable threshold).
- **Product performance** -- per-product units sold, revenue, and current stock (sorted by revenue).
- **Category performance** -- per-category product count, units sold, and revenue (sorted by revenue).
- **User activity** -- per-user order count and total spend (sorted by spend).

## Database Models

The application uses a single shared SQLite database (`ecommerce.db`) with the following tables:

| Table | Key Columns | Description |
|-------|-------------|-------------|
| `users` | `id`, `email` (unique), `name`, `created_at` | User accounts |
| `categories` | `id`, `name` (unique), `description` | Product categories |
| `products` | `id`, `name`, `description`, `price`, `category_id` (FK), `created_at` | Product catalog |
| `inventory` | `product_id` (PK, FK), `quantity`, `reserved`, `last_updated` | Stock tracking (one row per product) |
| `orders` | `id`, `user_id` (FK), `status`, `total`, `created_at` | Customer orders |
| `order_items` | `id`, `order_id` (FK), `product_id` (FK), `quantity`, `price` | Line items within an order |

**Entity relationships:**

```
User 1──* Order 1──* OrderItem *──1 Product *──1 Category
                                    Product 1──1 Inventory
```

Tables are created automatically on application startup via the `lifespan` handler which calls `SQLModel.metadata.create_all`.

## API Reference

All endpoints return JSON. The interactive API documentation is available at `/docs` (Swagger UI) and `/redoc` (ReDoc) when the server is running.

### Root

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Health check -- returns `{"status": "healthy", "service": "ecommerce-monolith"}` |

### Users

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/users` | Create a new user (returns `400` if email already registered) |
| `GET` | `/users/{user_id}` | Get a user by ID |
| `GET` | `/users` | List all users |

### Categories

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/categories` | Create a new category |
| `GET` | `/categories` | List all categories |

### Products

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/products` | Create a new product (auto-creates inventory record; validates category if provided) |
| `GET` | `/products/{product_id}` | Get a product by ID |
| `GET` | `/products` | List all products |

### Orders

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/orders` | Create an order with line items (validates user, products, and inventory availability; reserves stock) |
| `GET` | `/orders/{order_id}` | Get order details including line items and user info |
| `GET` | `/orders` | List all orders |

### Inventory

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/inventory/{product_id}` | Get inventory for a product |
| `PUT` | `/inventory/{product_id}` | Set inventory quantity |
| `POST` | `/inventory/{product_id}/reserve` | Reserve inventory units (returns `400` if insufficient stock) |

### Reports

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/reports/sales` | Sales summary (revenue, order count, averages, status breakdown) |
| `GET` | `/reports/inventory?low_stock_threshold=10` | Inventory summary (stock totals, low-stock count) |
| `GET` | `/reports/products` | Product performance (units sold, revenue, stock per product) |
| `GET` | `/reports/categories` | Category performance (product count, revenue per category) |
| `GET` | `/reports/users` | User activity (order count, total spend per user) |

## Getting Started

### Prerequisites

- Python 3.10+

### Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd shop
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux / macOS
   venv\Scripts\activate      # Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

### Running the Server

Start the development server with auto-reload:

```bash
python run_local.py
```

The server starts on **http://0.0.0.0:8000**. The SQLite database file (`ecommerce.db`) is created automatically on first startup.

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Usage Examples

Below are example `curl` commands to exercise the API end-to-end.

### Create a user

```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "name": "Alice"}'
```

### Create a category

```bash
curl -X POST http://localhost:8000/categories \
  -H "Content-Type: application/json" \
  -d '{"name": "Electronics", "description": "Electronic devices and accessories"}'
```

### Create a product

```bash
curl -X POST http://localhost:8000/products \
  -H "Content-Type: application/json" \
  -d '{"name": "Wireless Mouse", "description": "Ergonomic wireless mouse", "price": 29.99, "category_id": 1}'
```

### Set inventory stock

```bash
curl -X PUT http://localhost:8000/inventory/1 \
  -H "Content-Type: application/json" \
  -d '{"quantity": 100}'
```

### Place an order

```bash
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "items": [{"product_id": 1, "quantity": 2}]}'
```

### Check inventory

```bash
curl http://localhost:8000/inventory/1
```

### Get sales report

```bash
curl http://localhost:8000/reports/sales
```

### Get product performance

```bash
curl http://localhost:8000/reports/products
```

## Development

- **Entry point:** `run_local.py` starts Uvicorn with `--reload` for live reloading during development.
- **Database:** SQLite is used by default (`ecommerce.db` in the working directory). The database schema is managed by SQLModel and created on startup; no migrations are required.
- **Adding endpoints:** Create a new module under `src/ecommerce/`, define an `APIRouter`, and register it in `src/ecommerce/main.py` via `app.include_router()`.
- **Models:** All database models live in `src/ecommerce/models.py` to maintain a single source of truth and simplify cross-domain joins.
