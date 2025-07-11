# Message Broker Project Example.

## Objective

Show the implementation and benefits of implement a MessageBroker.

## How to run.

### Database configuration

You can use docker:

```sh
docker pull mysql:9
docker run --name local-db -e MYSQL_ROOT_PASSWORD=123456 -p 3306:3306 -d mysql:9
```

Then you can connect to database:

```sh
docker exec -it local-db mysql -u root -p
```

And create the database:

```sql
CREATE DATABASE IF NOT EXISTS vehicle_tax_db;
USE vehicle_tax_db;

-- Create states table
CREATE TABLE states (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(10) NOT NULL UNIQUE,
    tax_rate DECIMAL(5,4) NOT NULL DEFAULT 0.05,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create vehicles table
CREATE TABLE vehicles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    plate VARCHAR(20) NOT NULL,
    state_id INT NOT NULL,
    vehicle_type ENUM('car', 'truck', 'motorcycle', 'bus') NOT NULL,
    year INT NOT NULL,
    value DECIMAL(10,2) NOT NULL,
    owner_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (state_id) REFERENCES states(id),
    UNIQUE KEY unique_plate_state (plate, state_id)
);

-- Create tax_payments table
CREATE TABLE tax_payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id INT NOT NULL,
    payment_date DATE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    tax_year INT NOT NULL,
    payment_method ENUM('cash', 'credit_card', 'bank_transfer', 'check') NOT NULL,
    transaction_id VARCHAR(100) UNIQUE,
    status ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id),
    UNIQUE KEY unique_vehicle_tax_year (vehicle_id, tax_year)
);
```

Also you can populate with demo data.

```sql
-- Insert states
INSERT INTO states (name, code, tax_rate) VALUES
('California', 'CA', 0.0725),
('Texas', 'TX', 0.0625),
('New York', 'NY', 0.08),
('Florida', 'FL', 0.06),
('Illinois', 'IL', 0.0625);

-- Insert vehicles
INSERT INTO vehicles (plate, state_id, vehicle_type, year, value, owner_name) VALUES
('ABC123', 1, 'car', 2020, 25000.00, 'John Doe'),
('XYZ789', 1, 'truck', 2019, 45000.00, 'Jane Smith'),
('DEF456', 2, 'car', 2021, 30000.00, 'Bob Johnson'),
('GHI789', 2, 'motorcycle', 2022, 15000.00, 'Alice Brown'),
('JKL012', 3, 'car', 2018, 20000.00, 'Charlie Wilson'),
('MNO345', 3, 'bus', 2017, 80000.00, 'Transit Co'),
('PQR678', 4, 'car', 2023, 35000.00, 'David Lee'),
('STU901', 5, 'truck', 2020, 50000.00, 'Emma Davis');

-- Insert tax payments
INSERT INTO tax_payments (vehicle_id, payment_date, amount, tax_year, payment_method, transaction_id, status) VALUES
(1, '2024-01-15', 1812.50, 2024, 'credit_card', 'TXN001', 'completed'),
(2, '2024-02-20', 2812.50, 2024, 'bank_transfer', 'TXN002', 'completed'),
(3, '2024-01-10', 1875.00, 2024, 'cash', 'TXN003', 'completed'),
(4, '2024-03-05', 937.50, 2024, 'credit_card', 'TXN004', 'completed'),
(5, '2024-01-25', 1600.00, 2024, 'check', 'TXN005', 'completed'),
(1, '2023-01-15', 1812.50, 2023, 'credit_card', 'TXN006', 'completed'),
(3, '2023-02-10', 1875.00, 2023, 'bank_transfer', 'TXN007', 'completed');
```

### Running Python project


Ensure that you have `uv` installed  [see here](https://docs.astral.sh/uv/getting-started/installation/)

Then you can run the project with:

```sh
uv init
uv pip sync

```

## About setup.

The instructions for the creation of this project are in [the setup dodumentation](SETUP.mdnstructions for the creation of this project are in [the setup dodumentation](SETUP.md))