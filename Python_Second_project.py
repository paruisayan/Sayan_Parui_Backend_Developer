#Database connection details
import mysql.connector
import Scanner_OpenCV
#Code Push to Git by Sayan Parui for Testing 

conn_obj=mysql.connector.connect(
    host="localhost",
    user="root",
    password="Newuser@2025",
    database="supermarket_project2")
cur_obj=conn_obj.cursor()

#Define function data_entry_sql
def data_entry_sql(c_name,c_address,c_phone_number):

    # Build the query with user-provided name using LIKE operator
    sql = "INSERT INTO cust_details (c_name,c_address,c_phone_number) VALUES (%s, %s, %s)"
    data = (c_name,c_address,c_phone_number)

    try:
        cur_obj.execute(sql, data)
        print("Custom Details Inserted")
        conn_obj.commit()
    except mysql.connector.Error as e:
        print("Error retrieving data from MySQL:", e)
        conn_obj.rollback()
def data_entry_analytics(c_id, c_name, total_bill_amount):

    # Build the query with user-provided name using LIKE operator
    sql = "INSERT INTO analytics_table (c_id, c_name, total_bill_amount) VALUES (%s, %s, %s)"
    data = (c_id, c_name, total_bill_amount)

    try:
        cur_obj.execute(sql, data)
        print("Sales Data Inserted")
        conn_obj.commit()
    except mysql.connector.Error as e:
        print("Error retrieving data from MySQL:", e)
        conn_obj.rollback()

#Define function data_retrieve
def data_retrieve(cust_phone_number):
    # Build the query with user-provided name using LIKE operator
    #select * from cust_details WHERE c_phone_number='something';
    query = f"select * from cust_details WHERE c_phone_number=\'{cust_phone_number}\'"

    try:
        cur_obj.execute(query)
        result = cur_obj.fetchone()
        conn_obj.commit()
    except mysql.connector.Error as e:
        print("Error retrieving data from MySQL:", e)
        conn_obj.rollback()
    return result
def retrieve_from_inventory(p_id_from_casher):
    # Build the query with user-provided name using LIKE operator
    #select * from cust_details WHERE c_phone_number='something';
    query = f"select * from inventory WHERE p_id={p_id_from_casher}"

    try:
        cur_obj.execute(query)
        result = cur_obj.fetchone()
        conn_obj.commit()
    except mysql.connector.Error as e:
        print("Error retrieving data from MySQL:", e)
        conn_obj.rollback()
    return result
cust_phone_number=input("Please enter your phone number:")
result_from_DB= data_retrieve(cust_phone_number)
if result_from_DB:
    total_bill=0
    while True:
        #p_id_from_casher=0
        #p_id_from_casher=int(input("Please enter product ID:"))
        output_from_casher=Scanner_OpenCV.qr_code_scanner()
        p_id_from_casher=output_from_casher.split("-")[0]
        #print(p_id_from_casher)
        details_from_inventory=retrieve_from_inventory(p_id_from_casher)
        product_price=details_from_inventory[2]
        P_quantity_from_casher=int(input("Please enter product quantity:"))
        bill_amout=product_price*P_quantity_from_casher
        total_bill = total_bill + bill_amout
        responce =input("Do you want to continue?(y/n)")
        if responce =="n":
            break
    print("Total_bill_amout is:",total_bill)
    data_entry_analytics(result_from_DB[0],result_from_DB[1],total_bill)

else:
    c_name=input("Please enter your name:")
    c_address=input("Please enter your address:")
    data_entry_sql(c_name,c_address,cust_phone_number)

conn_obj.close()


