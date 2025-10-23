show databases;
create database Python_First_project;
use Python_First_project;
create table customer_basic_table(
sl_no int primary key auto_increment not null,
full_name varchar(100) not null,
address varchar(200) not null,
phone_number varchar(12) not null,
user_ID varchar(10) not null,
user_password varchar(20) not null
)auto_increment=1;
insert into customer_basic_table
(full_name,address,phone_number,user_ID,user_password) 
values("Sayan Parui","Budge Budge","8334020668","Sayan@2001","Newuser@2025");
select * from customer_basic_table;
#truncate table customer_basic_table;