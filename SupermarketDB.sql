create database supermarket_project2;
use supermarket_project2;
CREATE TABLE cust_details (
    c_id INT AUTO_INCREMENT PRIMARY KEY,
    c_name VARCHAR(100) NOT NULL,
    c_address VARCHAR(200),
    c_phone_number VARCHAR(15)
)AUTO_INCREMENT=1;
describe cust_details;
select * from cust_details;
INSERT INTO cust_details (c_name, c_address, c_phone_number)
VALUES 
("Sayan Parui", "Budge Budge", "8334020668"),
("Rahul Sen", "Kolkata", "9876543210"),
("Priya Das", "Howrah", "9123456780"); #Dummy purpose
#truncate table cust_details; ##not execute this 

CREATE TABLE inventory (
    p_id INT PRIMARY KEY AUTO_INCREMENT,
    p_name varchar(100) not null,
    p_price DECIMAL(5,2) NOT NULL,
    p_quantity INT NOT NULL
)AUTO_INCREMENT=1;
select * from inventory ;
#drop table inventory;
INSERT INTO inventory (p_name, p_price, p_quantity) VALUES
('Wheat Flour (Aata)', 45.00, 100),
('Rice (Regular)', 55.00, 80),
('Tur Dal', 110.00, 60),
('Moong Dal', 130.00, 50),
('Sugar', 44.00, 90),
('Salt (Iodized)', 20.00, 120),
('Refined Oil', 145.00, 40),
('Mustard Oil', 160.00, 35),
('Tea (Leaf)', 210.00, 30),
('Instant Coffee', 350.00, 20),
('Biscuits (Parle-G)', 10.00, 200),
('Bread (White)', 30.00, 50),
('Detergent Powder', 68.00, 45),
('Bath Soap (Lifebuoy)', 35.00, 100),
('Toothpaste', 55.00, 70),
('Shampoo Sachet', 2.00, 500),
('Packaged Water', 20.00, 60),
('Potato', 28.00, 100),
('Onion', 35.00, 90),
('Turmeric Powder', 90.00, 40),
('Red Chili Powder', 110.00, 35),
('Cumin Seeds (Jeera)', 180.00, 25),
('Jaggery (Gur)', 55.00, 50),
('Poha (Flattened Rice)', 48.00, 70),
('Vermicelli (Sevai)', 35.00, 60);




