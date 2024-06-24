import mysql.connector
import getpass
import time  
from datetime import datetime



connection = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root",
    database="bookstore"
)

cursor = connection.cursor()

def execute_query(connection, query, params):
    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
        return cursor.fetchall()  # Fetches all the rows of a query result, returns an empty list if no rows are available
    except mysql.connector.Error as e:
        print(f"The error '{e}' occurred")
        return []

def customer_exists(username,password):
    cursor.execute("start transaction;")
    cursor.execute("lock tables customer read;")
    connection.commit()
    cursor.execute("select * from customer;")
    customers = cursor.fetchall()
    for customer in customers:
        if (username == customer[4] and password == customer[5]):
            cursor.execute("unlock tables")
            cursor.execute("commit")
            connection.commit()
            return customer
    cursor.execute("unlock tables")
    cursor.execute("commit")
    connection.commit()
    return None

def admin_exists(username,password):
    cursor.execute("start transaction;")
    cursor.execute("lock tables admin read;")
    connection.commit()
    cursor.execute("select * from admin;")
    admins = cursor.fetchall()
    for admin in admins:
        if (username == admin[2] and password == admin[3]):
            cursor.execute("unlock tables")
            cursor.execute("commit")
            connection.commit()
            return admin
    cursor.execute("unlock tables")
    cursor.execute("commit")
    connection.commit()
    return None

def add_book(customer):
    cursor.execute("start transaction;")
    cursor.execute("lock tables inventory_book_details as ibd read, inventory as i read, customer as c read, cart write,books read;")
    connection.commit()
    customer_id = customer[0]
    cursor.execute(f"""
    SELECT DISTINCT ibd.BOOK_ID
    FROM INVENTORY_BOOK_DETAILS ibd
    JOIN INVENTORY i ON ibd.ADMIN_ID = i.ADMIN_ID
    JOIN CUSTOMER c ON i.PINCODE = c.PINCODE
    WHERE c.CUSTOMER_ID = {customer_id}
    """)
    book_ids = cursor.fetchall()
    book_details = []
    for book_id in book_ids:
        cursor.execute(f"""
            SELECT *
            FROM BOOKS
            WHERE BOOK_ID = {book_id[0]}
        """)
        book_detail = cursor.fetchone()
        book_details.append(book_detail)
    for i in book_details:
        print(i[0],i[3],i[6])
    input_book_id = int(input("Enter book id to add to cart"))
    flag = False
    for i in book_details:
        if (input_book_id == i[0]):
            cursor.execute(f'''select * from books where book_id = {input_book_id}''')
            book_price = cursor.fetchall()[0][6]
            print(book_price)
            flag = True
            price = i[6]
            cursor.execute(f'''select * from cart where customer_id = {customer_id}''')
            cart_details = cursor.fetchall()
            flag_book_present = False
            for j in cart_details:
                if j[2]==input_book_id:
                    print(j)
                    flag_book_present = True
                    new_quantity=j[3]+1
                    print(new_quantity)
                    final_price = j[1] + book_price
                    cursor.execute(f'''UPDATE cart SET quantity = {new_quantity}, TOTAL_COST = {final_price} WHERE customer_id = {customer_id} AND book_id = {input_book_id}''')
                    # cursor.execute(f'''UPDATE cart SET quantity = {initial_price + price} WHERE customer_id = {customer_id} AND book_id = {input_book_id}''')
                    break
            if (flag_book_present == False):
                cursor.execute(f'''INSERT INTO CART (CUSTOMER_ID, TOTAL_COST, BOOK_ID, QUANTITY) 
                                VALUES ({customer_id}, {price}, {input_book_id}, 1);''')
            

    if (flag == False):
        print("No such book found")
        cursor.execute("unlock tables;")
        cursor.execute("commit;")
        connection.commit()
        return
    cursor.execute
    cursor.execute("unlock tables;")
    cursor.execute("commit;")
    connection.commit()
  
def checkout(customer,cart_items,total_cost):
    cursor.execute("start transaction;")
    cursor.execute("lock tables inventory_book_details as ibd read, inventory_book_details read,inventory as i read,admin as a read, books as b read, customer as c read, orders write, order_details write")
    time.sleep(10)    
    connection.commit()
    flag = False
    for i in cart_items:
        cursor.execute(f"""SELECT ibd.QUANTITY 
                        FROM INVENTORY_BOOK_DETAILS ibd
                        INNER JOIN INVENTORY i ON ibd.ADMIN_ID = i.ADMIN_ID
                        INNER JOIN ADMIN a ON i.ADMIN_ID = a.ADMIN_ID
                        INNER JOIN BOOKS b ON ibd.BOOK_ID = b.BOOK_ID
                        INNER JOIN CUSTOMER c ON i.PINCODE = c.PINCODE
                        WHERE ibd.BOOK_ID = {i[2]} AND c.customer_id = {customer[0]};""")
        quantity = cursor.fetchone()[0]
        if (quantity < i[3]):
            print("Book ID : ",i[2],"needs to be removed due to less/no stock")
            flag = True
    if (flag):
        return
    # today's date
    today_date = datetime.today().strftime('%Y-%m-%d')    
    cursor.execute(f'''INSERT INTO orders (customer_id, delivery_status, date_ordered) VALUES
                   ({customer[0]}, 'Pending', '{today_date}')''')
    connection.commit()
    # cursor.execute(f'''delete from cart where customer_id={customer[0]}''')
    cursor.execute(f'''select * from orders where customer_id = {customer[0]}''')
    orders = cursor.fetchall()
    order_id = orders[len(orders)-1][0]
    for i in cart_items:
        cursor.execute(f'''insert into order_details values({order_id},{i[2]},{i[3]},{i[1]})''')
    # cursor.execute(f'delete from cart where customer_id = {customer[0]}')
    # connection.commit()
    cursor.execute("Unlock tables;")
    cursor.execute("commit;")
    connection.commit()

def remove_cart(customer,cart_items):
    cursor.execute("start transaction;")
    cursor.execute("lock tables cart write;")
    connection.commit()
    book_id = int(input("Enter book id to be removed : "))
    cursor.execute(f"""delete from cart where customer_id = {customer[0]} and book_id = {book_id}""")
    cursor.execute("unlock tables;")
    cursor.execute("commit;")
    connection.commit()
    

def show_cart(customer):
    cursor.execute("start transaction;")
    cursor.execute("lock tables cart read, books read")
    connection.commit()
    customer_id = customer[0]
    cursor.execute(f'''select * from cart where customer_id={customer_id}''')
    print(2)
    cart_items = cursor.fetchall()
    if (len(cart_items) == 0):
        print("There is nothing in the cart")
        cursor.execute("unlock tables;")
        cursor.execute("commit;")
        connection.commit()
        return
    for i in cart_items:
        print("Book ID : ",i[2])
        print('Quantity : ',i[3])
        print('Price : ',i[1])
        print()
    print()
    cursor.execute(f'''select sum(total_cost) from cart where customer_id = {customer_id}''')
    total_cost = cursor.fetchone()[0]
    print("Total Cost :",total_cost)
    print()
    while True:
        print("1. Checkout")
        print("2. Remove from cart")
        print("3. Back")
        cart_choice = input()
        if (cart_choice == "1"):
            checkout(customer,cart_items,total_cost)
            break
        elif (cart_choice == "2"):
            remove_cart(customer,cart_items)
            break
        elif (cart_choice == "3"):
            break
        else:
            continue
    cursor.execute("unlock tables;")
    cursor.execute("commit;")
    connection.commit()

def show_orders(customer):
    cursor.execute("start transaction;")
    cursor.execute("lock tables orders read, order_details read")
    connection.commit()
    customer_id = customer[0]
    cursor.execute(f'''select * from orders where customer_id = {customer_id}''')
    orders = cursor.fetchall()
    for order in orders:
        print("Order ID :",order[0])
        print("Delivery Status :",order[2])
        print("Date Ordered :",order[3])
        print("Date delivered :",order[4])
        print("Order Details : ")
        cursor.execute(f'''select * from order_details where order_id = {order[0]}''')
        order_details = cursor.fetchall()
        for i in order_details:
            print("Book ID :",i[1])
            print("Quantity :",i[2])
        print()
    cursor.execute("unlock tables;")
    cursor.execute("commit;")
    connection.commit()
        
def is_valid_email(email_str):
    if "@" in email_str and "." in email_str:
        username, domain = email_str.split("@")
        if domain.count(".") == 1 and len(username) > 0:
            return True
    return False

def is_gender(string):
    return string.lower() in ['male', 'female']

# Function to check if a string represents one of the 29 states of India
def is_indian_state(string):
    indian_states = [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa",
        "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh",
        "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan",
        "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
        "Jammu and Kashmir"
    ]
    return string.title() in indian_states

# Function to check if a string is all digits and has length 6
def is_six_digits(string):
    return string.isdigit() and len(string) == 6

def is_ten_digits(string):
    return string.isdigit() and len(string) == 10

def is_valid_date(date_str):
    if len(date_str) != 10:
        return False
    
    try:
        year, month, day = map(int, date_str.split('-'))
        if year < 1 or month < 1 or month > 12 or day < 1:
            return False
        
        max_days = 31
        if month in [4, 6, 9, 11]:
            max_days = 30
        elif month == 2:
            max_days = 29 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 28
        
        if day > max_days:
            return False
        
        return True
    except ValueError:
        return False
    
def all_alphabets(string):
    return all(char.isalpha() for char in string)
        
def sign_up():
    cursor.execute("start transaction;")
    cursor.execute("lock tables customer write;")
    cursor.execute('select * from customer')
    customers = cursor.fetchall()
    name = input("Enter your name : ")
    while True:
        if (not(all_alphabets(name))):
            print("Invalid name")
            name = input("Enter your name : ")
            continue
        break
    dob = input("Enter Date Of Birth(YYYY-MM-DD) : ")
    while True:    
        if (not(is_valid_date(dob))):
            print("Format of DOB is wrong")
            dob = input("Enter Valid DOB : ")
            continue
        break
    gender = input("Enter gender : ")
    while True:  
        if (not(is_gender(gender))):
            print("Gender input is wrong")
            gender = input("Enter gender : ")
            continue
        break   
    username = ""
    while True:
        username = input("Enter username : ")
        flag = False
        for customer in customers:
            if (customer[4] == username):
                flag = True
                print("This username is already used. Enter new username")
                break
        if (flag):
            continue    
        break    
    password = input("Enter password : ")
    while True:
        phone = input("Enter phone number : ")
        if (not(is_ten_digits(phone))) : 
            print("Invalid phone number")
            continue
        flag = False
        for customer in customers:
            if (customer[6] == phone):
                flag = True
                print("This phone number is already in use. Please enter your phone number")
                break
        if flag:
            continue
        break
    email = input("Enter email : ")
    while True:
        if (not(is_valid_email(email))):
            print("Wrong email id")
            email = input("Enter email : ")
            continue
        break
    state = input("Enter state : ")
    while True:
        if (not(is_indian_state(state))) : 
            print("Wrong state")
            state = input("Enter state : ")
            continue
        break
    location = input("Enter location : ")
    city = input("Enter city : ")
    pincode = input("Enter pincode : ")
    while True:
        if (not(is_six_digits(pincode))):
            print("Wrong pincode")
            pincode = input("Enter pincode : ")
            continue
        break
    c = input("Do you want to complete signing up(y/n) : ")
    if (c.lower() == 'y'):
        cursor.execute(f"""INSERT INTO CUSTOMER (NAME, DATE_OF_BIRTH, GENDER, USERNAME, PASSWORD, PHONE, EMAIL_ID, LOCATION, CITY, STATE, 
                   PINCODE) VALUES ('{name}','{dob}','{gender}','{username}','{password}','{phone}','{email}','{location}','{city}','{state}','{pincode}');""")
        connection.commit()
    cursor.execute("unlock tables;")
    cursor.execute("commit;")
    connection.commit()  
    
def update_price(admin_id):
    cursor.execute("start transaction;")
    cursor.execute("lock tables books write, cart write;")
    connection.commit()
    book_id = int(input("Enter book id whose price is to be updated : "))
    cursor.execute(f"""select * from books where book_id = {book_id}""")
    books = cursor.fetchall()    
    if (len(books) == 0):
        cursor.execute("unlock tables;")
        cursor.execute("commit;")
        connection.commit()
        print("No such book exists")
        return
    price = int(input("Enter new price : "))
    cursor.execute(f"""update books set price = {price} where book_id = {book_id}""")
    # cursor.execute(f"""select * from cart where book_id = {book_id}""")
    cursor.execute(f"""update cart set total_cost = quantity * {price} where book_id = {book_id}""")
    cursor.execute("unlock tables;")
    cursor.execute("commit;")
    connection.commit()
    
while True:
    print("----------WELCOME TO SensibleReads----------")
    print("1. Log in as customer")
    print("2. Sign up as customer")
    print("3. Log in as admin")
    print("4. Exit")
    choice = input("Enter your input : ")
    
    if choice == "1":
        username = input("Enter username : ")
        password = getpass.getpass("Enter password : ")
        # username = 'alice_user'
        # password = 'alice_password'
        customer = customer_exists(username,password)
        if (customer is None):
            print("Not found. Try again")
            continue
        while True:
            print("1. Add a book to cart")
            print("2. Show cart/Checkout")
            print("3. Show orders")
            print("4. Logout")
            customer_choice = input("Enter your choice : ")
            if (customer_choice == "1"):
                add_book(customer)
            elif (customer_choice == "2"):
                show_cart(customer)
            elif (customer_choice == "3"):
                show_orders(customer)
            elif (customer_choice == "4"):
                print("Thank You")
                break
            else:
                print("Wrong choice. Try again")
            connection.commit()
    elif choice == "2":
        sign_up()
    elif choice == "3":
        username = input("Enter username : ")
        password = getpass.getpass("Enter password : ")
        admin = admin_exists(username,password)
        if (admin is None):
            print("No admin exists with such credentials")
            continue
        while True:
            connection.commit()
            print("1. Check inventory status")
            print("2. Add book to inventory")
            print("3. Sales/Statistics")
            print("4. Update price")
            print("5. Logout")
            admin_name = admin[1]
            admin_id = admin[0]
            n = input()
            if(n=="1"):
                cursor.execute("start transaction;")
                cursor.execute("lock tables INVENTORY_BOOK_DETAILS as ib read, books as b read, author as a read;")
                connection.commit()
                print("--------"+admin_name + "--------")
                print("      Author       |         Book        |         Quantity       ")
                cursor.execute(f"""SELECT A.NAME AS Author_Name, B.TITLE AS Book_Name, 
                               IB.QUANTITY AS Quantity FROM INVENTORY_BOOK_DETAILS IB INNER JOIN BOOKS B ON IB.BOOK_ID = B.BOOK_ID 
                               INNER JOIN AUTHOR A ON B.AUTHOR_ID = A.AUTHOR_ID WHERE IB.ADMIN_ID = {admin_id}""")
                row = cursor.fetchall()
                for i in row:
                    print(str(i[0]) + "     "+ str(i[1]) + "      "+ str(i[2]))
                    print("\n")
                cursor.execute("unlock tables;")
                cursor.execute("commit;")
                connection.commit()
            elif(n=="2"):
                # cursor.execute("Select * from Books;")
                # rows = cursor.fetchall()
                # for i in rows:
                #     print("[BOOK ID], [AUTHOR ID], [PUBLISHER ID], '[BOOK TITLE]', '[GENRE]', '[SYNOPSIS]', [PRICE]")
                #     print(i)
                #     print("\n")
                # tell = input("Is the Book you want to add, already there in the table shown above?(y/n): ")
                # if(tell == "n"):
                #     isinauthor = False
                #     isinpublisher = False
                #     print("-------------------------------------")
                #     a = input("Enter the Title of the Book: ")
                #     b = input("Enter the author of the Book: ")
                #     c = int(input("Enter the price of the Book: "))
                #     d = input("Enter the genre of the Book: ")
                #     e = input("Enter the synopsis of the Book: ")
                #     f = input("Enter the publisher name: ")
                #     print("-------------------------------------")
                #     cursor.execute("Select name from author; ")
                #     row = cursor.fetchall()
                #     for i in row:
                #         if(i[0]==b):
                #             isinauthor=True
                #             break
                #     if(isinauthor==False):
                #         cursor.execute("INSERT INTO AUTHOR (NAME) VALUES (%s);",(b,))
                #     cursor.execute("Select name from publisher; ")
                #     row = cursor.fetchall()
                #     for i in row:
                #         if(i[0]==f):
                #             isinpublisher=True
                #             break
                #     if(isinpublisher==False):
                #         cursor.execute("INSERT INTO PUBLISHER (NAME) VALUES (%s);",(f,))
                #     queryy = "SELECT AUTHOR_ID FROM AUTHOR WHERE NAME = %s"
                #     cursor.execute(queryy,(b,))
                #     auth = cursor.fetchone()
                #     queryy2 = "SELECT PUBLISHER_ID FROM PUBLISHER WHERE NAME = %s"
                #     cursor.execute(queryy2,(f,))
                #     pub = cursor.fetchone()
                #     cursor.execute("select * from author")
                #     rows = cursor.fetchall()
                #     cursor.execute("INSERT INTO BOOKS (AUTHOR_ID, PUBLISHER_ID, TITLE, GENRE, SYNOPSIS, PRICE) VALUES (%s, %s, %s, %s, %s, %s);",(str(auth[0]),str(pub[0]),a,d,e,str(c)))
                #     cursor.execute("SELECT A.NAME AS Author_Name, B.TITLE AS Book_Name, IB.QUANTITY AS Quantity FROM INVENTORY_BOOK_DETAILS IB INNER JOIN BOOKS B ON IB.BOOK_ID = B.BOOK_ID INNER JOIN AUTHOR A ON B.AUTHOR_ID = A.AUTHOR_ID WHERE IB.ADMIN_ID = 1")
                #     row = cursor.fetchall()
                #     print("-----------------------")
                #     print("Below are the books available in your inventory: ")
                #     for i in row:
                #         print(str(i[0]) + "     "+ str(i[1]) + "      "+ str(i[2]))
                #         print("\n")
                #     print(f"How many copies of {a} are you adding to the inventory? ")
                #     copies = int(input())
                #     query3 = """INSERT INTO INVENTORY_BOOK_DETAILS (ADMIN_ID, BOOK_ID, QUANTITY) VALUES (%s, (SELECT BOOK_ID FROM BOOKS WHERE TITLE = %s), %s);"""
                #     cursor.execute(query3,(admin_id,a,copies))
                #     connection.commit()
                # if(tell=="y"):
                #     cursor.execute(f"""SELECT B.BOOK_ID as Book_ID,B.TITLE AS Book_Name, A.NAME AS Author_Name, IB.QUANTITY AS Quantity FROM INVENTORY_BOOK_DETAILS IB INNER JOIN BOOKS B ON IB.BOOK_ID = B.BOOK_ID INNER JOIN AUTHOR A ON B.AUTHOR_ID = A.AUTHOR_ID WHERE IB.ADMIN_ID = {admin_id}""")
                #     row = cursor.fetchall()
                #     print("-----------------------")
                #     print("Below are the books available in your inventory: ")
                #     for i in row:
                #         print(str(i[0]) + "     "+ str(i[1]) + "      "+ str(i[2]) + "     " + str(i[3]))
                #         print("\n")
                #     haikya = input("is the book in your inventory(y/n)? ")
                #     id_book = input("Enter the ID of the Book: ")
                #     print(f"How many copies of {id_book} are you adding to the inventory? ")
                #     copies = int(input())
                #     if(haikya == "y"):
                #         query4 = """
                #         UPDATE INVENTORY_BOOK_DETAILS
                #         SET QUANTITY = QUANTITY + %s
                #         WHERE BOOK_ID = %s AND ADMIN_ID = %s;
                #         """
                #         cursor.execute(query4,(copies,id_book,admin_id))
                #     else:
                #         query5 = """INSERT INTO INVENTORY_BOOK_DETAILS (ADMIN_ID, BOOK_ID, QUANTITY) VALUES (%s, %s, %s);"""
                #         cursor.execute(query5,(admin_id,id_book,copies))
                #         connection.commit()
                idd = input("Enter Book_ID: ")
                inbooks = False
                #checking if book_id is present in Books
                q1 = """SELECT COUNT(*) FROM Books WHERE book_id = %s """
                cursor.execute(q1,(idd,))
                count = cursor.fetchone()[0]
                if(count>0):
                    inbooks = True
                if(inbooks==False):
                    isinauthor = False
                    isinpublisher = False
                    print("-------------------------------------")
                    a = input("Enter the Title of the Book: ")
                    b = input("Enter the author of the Book: ")
                    c = int(input("Enter the price of the Book: "))
                    d = input("Enter the genre of the Book: ")
                    e = input("Enter the synopsis of the Book: ")
                    f = input("Enter the publisher name: ")
                    print("-------------------------------------")
                    cursor.execute("Select name from author; ")
                    row = cursor.fetchall()
                    for i in row:
                        if(i[0]==b):
                            isinauthor=True
                            break
                    if(isinauthor==False):
                        cursor.execute("INSERT INTO AUTHOR (NAME) VALUES (%s);",(b,))
                    cursor.execute("Select name from publisher; ")
                    row = cursor.fetchall()
                    for i in row:
                        if(i[0]==f):
                            isinpublisher=True
                            break
                    if(isinpublisher==False):
                        cursor.execute("INSERT INTO PUBLISHER (NAME) VALUES (%s);",(f,))
                    queryy = "SELECT AUTHOR_ID FROM AUTHOR WHERE NAME = %s"
                    cursor.execute(queryy,(b,))
                    auth = cursor.fetchone()
                    queryy2 = "SELECT PUBLISHER_ID FROM PUBLISHER WHERE NAME = %s"
                    cursor.execute(queryy2,(f,))
                    pub = cursor.fetchone()
                    connection.commit()
                    # cursor.execute("select * from author;")
                    # rows = cursor.fetchall()
                    cursor.execute("INSERT INTO BOOKS VALUES (%s, %s, %s, %s, %s, %s, %s);",(str(idd), str(auth[0]),str(pub[0]),a,d,e,str(c)))
                    connection.commit()
                    print(f"How many copies of {a} are you adding to the inventory? ")
                    copies = int(input())
                    query5 = """INSERT INTO INVENTORY_BOOK_DETAILS (ADMIN_ID, BOOK_ID, QUANTITY) VALUES (%s, %s, %s);"""
                    cursor.execute(query5,(admin_id,idd,copies))
                    connection.commit()
                else:
                    #check if the book is in the inventory of that admin
                    qq = """SELECT COUNT(*) AS book_count FROM INVENTORY_BOOK_DETAILS WHERE ADMIN_ID = %s AND BOOK_ID = %s;"""
                    cursor.execute(qq,(admin_id,idd))
                    counting = cursor.fetchone()[0]
                    copies = int(input(f"How many copies of {idd} do you want to add in the inventory: "))
                    if(counting==0):
                        #insert into inventory
                        qqq = """INSERT INTO INVENTORY_BOOK_DETAILS (ADMIN_ID, BOOK_ID, QUANTITY) VALUES (%s, %s, %s);"""
                        cursor.execute(qqq,(admin_id,idd,copies))
                        connection.commit()
                    else:
                        #update the book quantity
                        qqqq = """
                        UPDATE INVENTORY_BOOK_DETAILS
                        SET QUANTITY = QUANTITY + %s
                        WHERE BOOK_ID = %s AND ADMIN_ID = %s;
                        """
                        cursor.execute(qqqq,(copies,idd,admin_id))
                        connection.commit()


            elif(n=='3'):
                cursor.execute("start transaction;")
                cursor.execute("lock tables orders read, order_details read, books read, inventory read, INVENTORY_BOOK_DETAILS read, customer read")
                connection.commit()
                print("The Sales and Statistics are as follows:")
                sales_statistics_query = """
                SELECT CUSTOMER.NAME AS CustomerName, BOOKS.TITLE AS BookTitle, SUM(ORDER_DETAILS.QUANTITY * BOOKS.PRICE) AS TotalPurchasePrice
                FROM ORDERS
                JOIN CUSTOMER ON ORDERS.CUSTOMER_ID = CUSTOMER.CUSTOMER_ID
                JOIN ORDER_DETAILS ON ORDERS.ORDER_ID = ORDER_DETAILS.ORDER_ID
                JOIN BOOKS ON ORDER_DETAILS.BOOK_ID = BOOKS.BOOK_ID
                JOIN INVENTORY_BOOK_DETAILS ON BOOKS.BOOK_ID = INVENTORY_BOOK_DETAILS.BOOK_ID
                JOIN INVENTORY ON INVENTORY_BOOK_DETAILS.ADMIN_ID = INVENTORY.ADMIN_ID
                WHERE INVENTORY.ADMIN_ID = %s AND CUSTOMER.PINCODE = INVENTORY.PINCODE
                GROUP BY CUSTOMER.CUSTOMER_ID, ORDER_DETAILS.BOOK_ID
                """
                # Execute the query
                sales_statistics = execute_query(connection, sales_statistics_query, (admin_id,))

                # Check if sales_statistics is not empty
                if sales_statistics:
                    print("Sales Statistics:")
                    for CustomerName, BookTitle, TotalPurchasePrice in sales_statistics:
                        print(f"Name: {CustomerName}, Title: {BookTitle}, TotalPrice: ${TotalPurchasePrice:.2f}")
                else:
                    print("No sales data available.")
                cursor.execute("unlock tables;")
                cursor.execute("commit;")
                connection.commit()
            elif (n=="4"):
                update_price(admin_id)
                
            elif (n=="5"):
                print("Thank you")
                break
            else:
                print("Invalid Input. Please try again") 
    elif choice == "4":
        print("Exiting program...")
        break
    else:
        print("Wrong input. Please try again")
