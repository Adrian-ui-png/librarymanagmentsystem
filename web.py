from flask import Flask, render_template, request
import mysql.connector
import time
from datetime import datetime


connection = mysql.connector.connect(host='localhost',user='root',password='root',database='library')
cursor = connection.cursor()

app = Flask(__name__)



@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/contact', methods=['GET'])
def contact():
    return render_template('home_page/contact_us.html')

@app.route('/about', methods=['GET'])
def about():
    return render_template('home_page/about_us.html')

@app.route('/login', methods=['GET'])
def login():
    return render_template('home_page/login.html')

@app.route("/admin", methods=['GET', 'POST'])
def admin():
    cursor.execute('SELECT user_name, paswd FROM user')
    credential = cursor.fetchall()

    if request.method == 'POST':
        username = request.form.get('textbox1')
        pwd = request.form.get('textbox2')


        for i in credential:
            db_username, db_password = i
            
            if db_username == username:
                if db_password == pwd:
                    cursor.execute('SELECT * FROM user WHERE user_name=%s', (username,))
                    global data
                    data = cursor.fetchall()
                    global ppicture
                    ppicture=f'/static/images/profile_photos/{data[0][1]}.jpeg'
                    if data[0][7]== 'member':
                        return render_template('member/profile.html', data=data,ppicture=ppicture)
                    else:
                         return render_template('admin/admin.html', data=data,ppicture=ppicture)
                else:
                    return render_template('home_page/login.html', msg='Invalid password')
        return render_template('home_page/login.html', msg='Invalid username')

    return render_template('home_page/login.html') 

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        genre = request.form['genre']
        author = request.form['author']
        publisher = request.form['publisher']

        
        query = "INSERT INTO books (book_name, author, publisher, genre, availability) VALUES (%s, %s, %s, %s,'Available')"
        data3 = (title, author, publisher, genre)

        cursor.execute(query, data3)
        connection.commit()

        return render_template('/admin/add_book.html', msg='Book details added successfully!')

    return render_template('/admin/add_book.html')


@app.route('/add_member', methods=['GET', 'POST'])
def add_member():
    if request.method == 'POST':
       
        name = request.form.get('name')
        password = request.form.get('password')
        email = request.form.get('email')
        address = request.form.get('address')  
        phone_no = request.form.get('phone_no')
        dob = request.form.get('dob')
        roll = request.form.get('roll')


        query = "INSERT INTO user (user_name, paswd, email, ph_no, address, dob, roles) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        data2 = (name, password, email, phone_no, address, dob, roll)

        
        cursor.execute(query, data2)
        connection.commit()

       
        return render_template('/admin/add_member.html', msg='Member details added successfully!')

   
    return render_template('/admin/add_member.html')


@app.route('/books', methods=['GET','POST'])
def books():
    search_query = request.args.get('search')  
    results = []  
    searched = None

    if search_query:
        searched = search_query
        query = "SELECT * FROM books WHERE book_name LIKE %s"
        data1 = (search_query,) 
        

        cursor.execute(query, data1)
        results = cursor.fetchall() 
        

        return render_template('/admin/books.html', book_data=results,name=searched)
    cursor.execute('select * from books')
    book_data=cursor.fetchall()
    return render_template('/admin/books.html',book_data=book_data)
    
@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    return render_template('/admin/admin.html',data=data,ppicture=ppicture)

@app.route('/delete_book', methods=['GET','POST'])
def delete_book():
    if request.method == 'POST':
        title=request.form['book_title']
        cursor.execute("DELETE FROM books WHERE book_name = %s", (title,))
        connection.commit()
        msg='succesfully deleted'
        return render_template('/admin/delete_book.html',msg=msg)


    return render_template('/admin/delete_book.html')


@app.route('/members_display', methods=['GET','POST'])
def members_display():
    search_query = request.args.get('search')  
    results = []  
    searched = None

    if search_query:
        searched = search_query
       
        query = "SELECT * FROM user WHERE user_name= %s"
        data1 = ( f"{search_query}",)  
        
        cursor.execute(query, data1)
        results = cursor.fetchall() 
        
        
        return render_template('/admin/members_display.html', user_data=results, name=searched)

   
    cursor.execute("SELECT * FROM user where roles='member'")
    user_data = cursor.fetchall()

  
    return render_template('/admin/members_display.html', user_data=user_data)

@app.route('/delete_member', methods=['GET','POST'])
def delete_member():
     if request.method == 'POST':
        member=request.form['member_identifier']
        cursor.execute("DELETE FROM user WHERE user_name = %s", (member,))
        connection.commit()
        msg='succesfully deleted'
        return render_template('/admin/delete_member.html',msg=msg)
     return render_template('/admin/delete_member.html')


@app.route('/currently_borrowed', methods=['GET','POST'])
def currently_borrowed():
    search_query = request.args.get('search')  
    results = []  
    searched = None

    if search_query:
        searched = search_query
       
        query = """
        SELECT user.user_name, books.book_name, borrow_date 
        FROM active_borrowings
        JOIN user ON active_borrowings.usr_id = user.usr_id
        JOIN books ON active_borrowings.book_id = books.book_id
        WHERE user.user_name = %s
        """
        data1 = (search_query,)  

        cursor.execute(query, data1)

        results = cursor.fetchall() 
        
        
        return render_template('/admin/currently_borrowed.html', user_data=results, name=searched)

   
    cursor.execute('SELECT user.user_name, books.book_name, borrow_date FROM active_borrowings, user, books WHERE active_borrowings.usr_id = user.usr_id AND active_borrowings.book_id = books.book_id')

    user_data = cursor.fetchall()

  
    return render_template('/admin/currently_borrowed.html', user_data=user_data)

@app.route('/records', methods=['GET','POST'])
def records():
    search_query = request.args.get('search')  
    results = []  
    searched = None

    if search_query:
        searched = search_query
       
        query = """
        SELECT record_id, user.user_name, books.book_name, borrow_date, return_date 
        FROM borrowing_records 
        JOIN user ON borrowing_records.usr_id = user.usr_id 
        JOIN books ON borrowing_records.book_id = books.book_id 
        WHERE user.user_name = %s
        """
        data1 = (search_query,)
        
        cursor.execute(query, data1)
        results = cursor.fetchall() 
        
        
        return render_template('/admin/records.html', user_data=results, name=searched)

   
    cursor.execute('SELECT record_id,user.user_name, books.book_name, borrow_date,return_date FROM borrowing_records, user, books WHERE borrowing_records.usr_id = user.usr_id AND borrowing_records.book_id = books.book_id')
    
    user_data = cursor.fetchall()

  
    return render_template('/admin/records.html', user_data=user_data)


@app.route('/admin-settings', methods=['GET', 'POST'])
def admin_settings():
    msg="Change password"
    if request.method == 'POST':
        current_password = request.form['name']
        new_password = request.form['email']
        re_enter_password = request.form['adress']

      
        user_name = data[0][1]
        curr_password = data[0][2]

        
        if current_password != curr_password:
            msg = 'Wrong current password'
            return render_template('/admin/admin_settings.html', msg=msg)

       
        elif new_password != re_enter_password:
            msg = "The new password re-entered is not correct"
            return render_template('/admin/admin_settings.html', msg=msg)

        else:
           
            cursor.execute('UPDATE user SET paswd = %s WHERE user_name = %s', (new_password, user_name))
            connection.commit()
            msg = "Successfully changed the password"
            return render_template('/admin/admin_settings.html', msg=msg)

    return render_template('/admin/admin_settings.html',msg=msg)


@app.route("/profile", methods=['GET', 'POST'])
def member_profile():
    return render_template('member/profile.html', data=data,ppicture=ppicture)


@app.route('/member_books', methods=['GET','POST'])
def member_books():
    title = request.args.get('search_title')  
    genre = request.args.get('search_genre')  
    results = []  
    searched = None

    if title:
        searched = title
        query = "SELECT * FROM books WHERE book_name LIKE %s"
        data1 = (title,) 
        

        cursor.execute(query, data1)
        results = cursor.fetchall() 
        

        return render_template('/member/member_books.html', book_data=results,name=searched)
    elif genre:
        searched = genre
        query = "SELECT * FROM books WHERE genre LIKE %s"
        data1 = (genre,) 
        

        cursor.execute(query, data1)
        results = cursor.fetchall() 
        

        return render_template('/member/member_books.html', book_data=results,name=searched)
    
    
    cursor.execute('select * from books')
    book_data=cursor.fetchall()
    return render_template('/member/member_books.html',book_data=book_data)


@app.route('/borrow_book_member', methods=['GET', 'POST'])
def borrow_book_member():
    if request.method == 'POST':
        book = request.form['member_identifier']

        
        cursor.execute('SELECT nbb FROM user WHERE user_name = %s', (data[0][1],))
        results = cursor.fetchall()
        limit = results[0][0]

        
        cursor.execute('SELECT book_id FROM books WHERE book_name = %s', (book,))
        re = cursor.fetchall()
        book_id = re[0][0]

        current_date = time.strftime('%Y-%m-%d', time.localtime())

       
        cursor.execute('SELECT availability FROM books WHERE book_name = %s', (book,))
        availability = cursor.fetchall()

        if availability[0][0] == 'Available':
            if limit >= 3:
                msg = 'You have exceeded the borrowing limit of 3.'
                return render_template('/member/borrow_book_member.html', msg=msg)
            else:
                limit += 1
                cursor.execute('UPDATE user SET nbb = %s WHERE user_name = %s', (limit, data[0][1]))
                connection.commit()

                query = 'INSERT INTO active_borrowings (usr_id, book_id, borrow_date) VALUES (%s, %s, %s)'
                data2 = (data[0][0], book_id, current_date)
                cursor.execute(query, data2)
                connection.commit()

                cursor.execute('UPDATE books SET availability = %s WHERE book_name = %s', ('Not Available', book))
                connection.commit()

                msg = f'Successfully borrowed the book {book}.'
                return render_template('/member/borrow_book_member.html', msg=msg)
        else:
            msg = 'Sorry, this book is not available.'
            return render_template('/member/borrow_book_member.html', msg=msg)

    return render_template('/member/borrow_book_member.html')


@app.route('/member_return', methods=['GET', 'POST'])
def member_return():
    if request.method == 'POST':
        book = request.form['member_identifier']

        
        cursor.execute('SELECT nbb FROM user WHERE user_name = %s', (data[0][1],))
        results = cursor.fetchall()
        limit = results[0][0]

        
        try:
            cursor.execute('SELECT book_id FROM books WHERE book_name = %s', (book,))
            re = cursor.fetchall()
            book_id = re[0][0]
        except:
            msg='no such book'
            return render_template('/member/member_return.html', msg=msg)

        current_date = time.strftime('%Y-%m-%d', time.localtime())

       
        cursor.execute('SELECT usr_id, book_id, borrow_date FROM active_borrowings WHERE usr_id = %s AND book_id = %s', (data[0][0], book_id))
        borrowed = cursor.fetchall()

        if borrowed:
            usr_id, borrowed_book_id, borrow_date = borrowed[0]

            if usr_id == data[0][0] and book_id == borrowed_book_id:
                limit -= 1
                cursor.execute('UPDATE user SET nbb = %s WHERE user_name = %s', (limit, data[0][1],))
                connection.commit()

                
                query = 'INSERT INTO borrowing_records (usr_id, book_id, borrow_date, return_date) VALUES (%s, %s, %s, %s)'
                data2 = (usr_id, book_id, borrow_date, current_date)
                cursor.execute(query, data2)
                connection.commit()

              
                cursor.execute('DELETE FROM active_borrowings WHERE book_id = %s AND usr_id = %s', (book_id, usr_id))
                connection.commit()

                
                cursor.execute('UPDATE books SET availability = %s WHERE book_name = %s', ('Available', book))
                connection.commit()

                msg = f'Successfully returned the book {book}.'
                return render_template('/member/member_return.html', msg=msg)

        msg = 'Sorry, you have not borrowed this book.'
        return render_template('/member/member_return.html', msg=msg)

    return render_template('/member/member_return.html')


@app.route('/member-settings', methods=['GET', 'POST'])
def member__settings():
    msg="Chamge Password"
    if request.method == 'POST':
        current_password = request.form['name']
        new_password = request.form['email']
        re_enter_password = request.form['adress']

      
        user_name = data[0][1]
        curr_password = data[0][2]

        
        if current_password != curr_password:
            msg = 'Wrong current password'
            return render_template('/member/member_settings.html', msg=msg)

       
        elif new_password != re_enter_password:
            msg = "The new password re-entered is not correct"
            return render_template('/member/member_settings.html', msg=msg)

        else:
           
            cursor.execute('UPDATE user SET paswd = %s WHERE user_name = %s', (new_password, user_name))
            connection.commit()
            msg = "Successfully changed the password"
            return render_template('/member/member_settings.html', msg=msg)

    return render_template('/member/member_settings.html',msg=msg)



@app.route('/currently_member', methods=['GET', 'POST'])
def currently_member():
    search_query = request.args.get('search')  
    results = []  
    searched = None

    if search_query:
        searched = search_query
        query = """
        SELECT 
        books.book_name, 
        active_borrowings.borrow_date
        FROM 
        active_borrowings
        INNER JOIN 
        user ON active_borrowings.usr_id = user.usr_id
        INNER JOIN 
        books ON active_borrowings.book_id = books.book_id
        WHERE 
        books.book_name = %s
        """
        data1 = (search_query,)
        
        cursor.execute(query, data1)
        results = cursor.fetchall() 
        
        return render_template('member/currently_member.html', book_data=results, name=searched)

   

    query = """
    SELECT books.book_name, active_borrowings.borrow_date
    FROM active_borrowings
    INNER JOIN user ON active_borrowings.usr_id = user.usr_id
    INNER JOIN books ON active_borrowings.book_id = books.book_id
    WHERE active_borrowings.usr_id = %s;
    """
    
    cursor.execute(query, (data[0][0],))
    book_data = cursor.fetchall()

    return render_template('member/currently_member.html', book_data=book_data)



@app.route('/notifications', methods=['GET', 'POST'])
def notifications():
    def date_difference(d1, d2):
        date_format = "%Y-%m-%d"
        d1 = datetime.strptime(d1, date_format)
        d2 = datetime.strptime(d2, date_format)
        return abs((d2 - d1).days)

    current_date = time.strftime('%Y-%m-%d', time.localtime())

    query = """
    SELECT books.book_name, active_borrowings.borrow_date
    FROM active_borrowings
    INNER JOIN user ON active_borrowings.usr_id = user.usr_id
    INNER JOIN books ON active_borrowings.book_id = books.book_id
    WHERE active_borrowings.usr_id = %s;
    """

    cursor.execute(query, (data[0][0],))
    notifi_data = cursor.fetchall()
    

    if not notifi_data:
        msg = 'No book borrowed by you !!!'

    notifications = []
    a = 1
    for i in notifi_data:
        days = date_difference(i[1], current_date)
        if days >= 20:
            notifications.append([a, f'You have an overdue book: {i[0]}'])
            a += 1

    if not notifications:
        msg = 'You have no book overdue'
    else:
        return render_template('member/notfications.html', notifications=notifications)

    return render_template('member/notfications.html', msg=msg)
if __name__ == '__main__':
    app.run(port=5500, debug=True)
