use supermarket_project2;
CREATE TABLE analytics_table (
    sale_id int primary key auto_increment,
    c_id INT NOT NULL,
    c_name VARCHAR(255) NOT NULL,
    total_bill_amount DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)auto_increment=1;
select * from analytics_table ;
#truncate table analytics_table; NOT RUN THIS 

INSERT INTO analytics_table (c_id, c_name, total_bill_amount) #TESTING DATA
VALUES 
(101, 'Alice Johnson', 145.75),
(102, 'Sayan Parui', 12.99);