"""
Archer Simpson
19/5/23
Te Reo Dictionary
"""

from flask import Flask, render_template, session, request, redirect
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt
import datetime

# The following 4 lines are initializing the program. Line 9 is identifying the location of the database.
# Line 10 defines the app and lines 12 and 13 are setting up the encryption process via bcrypt
DATABASE = "C:/Users/arche/OneDrive/Documents/WC Stuff/Year 13/13DTS/Database/database_assesment/dictionary_database"
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'fsifs2134'


# This function makes a connection to my database from python. If any errors occur in this process it will print the
# error in my terminal, so I can address the issue
def create_connection(db_file):
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)
    return None


# This function identifies whether the active user is a student or teacher. It returns true if the user is a teacher
# and false if the user is a student
def student_or_teacher():
    print(session.get("usertype"))
    if session.get("usertype") == "Teacher":
        return True
    else:
        return False


# This function identifies whether a user is logged in by looking if an email is attached to the current user
def is_logged_in():
    if session.get("email") is None:
        print("not logged in")
        return False
    else:
        print("logged in")
        return True


# This app route occurs when the url '/' is met. The code then runs through the function which renders the main.html
# file and passes it the variables logged_in and student_or_teacher which are equal to their respective functions above
@app.route('/')
def render_main():
    return render_template('main.html', logged_in=is_logged_in(), student_or_teacher=student_or_teacher())


# This app route requires the variable and table column: category_id, to function. From there, the category_id is used
# to select all the information about every word in that category. The query is executed and a fetchall is used to
# contain the list
@app.route('/words/<category_id>')
def render_words(category_id):
    con = create_connection(DATABASE)
    query = "SELECT * FROM words WHERE category_id=?"
    cur = con.cursor()
    cur.execute(query, (category_id,))
    word_list = cur.fetchall()

# taking all the information from the category database. This is needed for the category links in html
    query = "SELECT * FROM categories"
    cur.execute(query)
    category_list = cur.fetchall()

# This code selects the category_name from the passed variable category_id. It fetches the value and
# removes the category_name from within the tuple format of which it is originally queried as
    query = "SELECT category_name FROM categories WHERE category_id=?"
    cur.execute(query, (category_id,))
    category_name = cur.fetchone()[0]
    con.close()

# printing out my variables to help debug any potential issues with my website
    print(category_name)
    print(word_list)
    print(category_list)

    return render_template('words.html', allwords=word_list, logged_in=is_logged_in(), categories=category_list,
                           category_name=category_name, student_or_teacher=student_or_teacher())


# This app route takes the variable word_id and uses it to create a page for every word
@app.route('/word_page/<word_id>')
def render_word(word_id):
    con = create_connection(DATABASE)
    query = "SELECT * FROM words WHERE word_id=?"
    cur = con.cursor()
    cur.execute(query, (word_id,))
    word_list = cur.fetchall()
    con.close()
    print(word_list)
    print(student_or_teacher())
    return render_template('word_page.html', logged_in=is_logged_in(), allwords=word_list,
                           student_or_teacher=student_or_teacher())


# This app route uses methods. Methods are also referred to as HTTP methods. These methods are designed to enable
# the client to communicate with the server. The post method takes client data and uploads it to the server. The get
# method is used for clients to take data from server
@app.route('/login', methods=['POST', 'GET'])
def render_login():
    # checking if the client is already logged in. i.e if the client is already logged in they can't log in again
    if is_logged_in():
        return redirect("/?logged+in")
    if request.method == "POST":
        # The two following lines are taking the inputs received from the form on the login page and assigning them to
        # a variable. The email variable is used to draw the users data that is available from when the user previously
        # signed up
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()
        query = """SELECT id, password, usertype FROM user_login WHERE email = ?"""
        con = create_connection(DATABASE)
        cur = con.cursor()
        cur.execute(query, (email,))
        con.commit()
        user_data = cur.fetchall()
        print(query)
        # checks if there is data in the list user_data - i.e. the email exists/input exists
        if len(user_data) > 0:
            user_data = user_data[0]
        con.close()
        try:
            # taking the group of data collected from the query above and assigning the variable belonging to each of
            # them. I know from the query above that user_data[0] will be the first column queried, and therefore it
            # will be id. The except IndexError will occur if user_data[X] occurs but there is no index for X
            print(user_data)
            user_id = user_data[0]
            user_password = user_data[1]
            usertype = user_data[2]
        except IndexError:
            return redirect('/login?error=Invalid+password+or+email')

        # checks that the password entered into the login form is the same as what has previously been in the database
        # from the original signup
        if not bcrypt.check_password_hash(user_password, password):
            return redirect(request.referrer + "?error=Email+invalid+or+password+incorrect")

        # creates session with the following form inputs, it essentially creates a global during that exact user's
        # session (or whilst they are logged in)
        session['email'] = email
        session['user_id'] = user_id
        session['usertype'] = usertype
        print(session)
        return redirect('/')

    return render_template('login.html', logged_in=is_logged_in())


# This app route is for logging out. In the function logout(): the program deletes (pops) all the session keys (data)
# that is being currently stored
@app.route('/logout')
def logout():
    print(list(session.keys()))
    [session.pop(key) for key in list(session.keys())]
    print(list(session.keys()))
    return redirect('/?later+mate')


@app.route('/signup', methods=['POST', 'GET'])
def render_signup():
    if is_logged_in():
        redirect("/login?already+signed+up+please+log+in")
    if request.method == 'POST':
        print(request.form)
        usertype = request.form.get('usertype').title().strip()
        fname = request.form.get('fname').title().strip()
        lname = request.form.get('lname').title().strip()
        email = request.form.get('email').lower().strip()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # The following  if statements confirm that the entered values for sign up are valid. The second and third if
        # statements confirm that the password and confirm password are the same and that the
        # password is less than 8 characters. The website does not accept short passwords because it is a security
        # concern/risk etc. The first if statement checks is the entered usertype input is one of the two
        # valid inputs: 'Teacher' or 'Student' (.title() and .strip() are used to dismiss capitalization or space
        # difference. The fourth and final if statement double checks that firstname or lastname are not empty.
        # For some reason my 'required' specification on my input was not functioning as intended so to ensure my
        # program is robust I added the failsafe which checks if the inputs are empty
        if usertype != "Student":
            if usertype != "Teacher":
                return redirect("/signup?error=Usertype+is+invalid")

        if password != confirm_password:
            return redirect("/signup?error=Passwords+do+not+match")

        if len(password) < 8:
            return redirect("/signup?error=Password+must+be+at+least+8+characters")

        if fname == '' or lname == '':
            return redirect("/signup?error=Please+enter+in+a+value+for+firstname+and+lastname")

        # Hashes the password. This basically scrambles each character of the password into random characters
        hashed_password = bcrypt.generate_password_hash(password)

        # Inserts the inputs provided in the signup form into the user_login table. The insert is done so that each
        # input is submitted into their respective column
        con = create_connection(DATABASE)
        query = "INSERT INTO user_login (firstname, lastname, password, usertype, email) VALUES (?, ?, ?, ?, ?)"
        cur = con.cursor()

        # Attempts to execute the query but accepts the integrity error which occurs when the email entered matches an
        # already existing email address
        try:
            cur.execute(query, (fname, lname, hashed_password, usertype, email))
        except sqlite3.IntegrityError:
            con.close()
            return redirect("/signup?error=Email+is+already+used")

        con.commit()
        con.close()

        return redirect("/login")

    return render_template('signup.html', logged_in=is_logged_in())


@app.route('/admin', methods=['POST', 'GET'])
def render_admin():
    # checks if student_or_teacher(): function is equal to false (student). Stops students from accessing admin features
    # which in this route revolve around the ability to add words to the dictionary database
    if not student_or_teacher():
        return redirect("/login?you+must+be+logged+in+as+a+teacher+to+access+this")
    con = create_connection(DATABASE)
    query = "SELECT * FROM categories"
    cur = con.cursor()
    cur.execute(query)
    category_list = cur.fetchall()
    print(category_list)
    return render_template("admin.html", logged_in=is_logged_in(), categories=category_list,
                           student_or_teacher=student_or_teacher())


# This app route takes the data given to the website surrounding the newly added word and commits into the database
@app.route('/add_word', methods=['POST'])
def render_add_word():
    if request.method == 'POST':
        added_by = session.get("user_id")
        english_translation = request.form.get('english_translation').title().strip()
        te_reo_translation = request.form.get('te_reo_translation').lower().strip()
        definition = request.form.get('definition').title().strip()
        # if the definition is shorter than 15 characters it is not a valid definition and is left as pending
        if len(definition) < 15:
            definition = "pending"
        category_name = request.form.get('category')
        category_name = category_name.split(", ")
        category_id = category_name[0]
        category_name = category_name[1]
        print(category_id)
        print(category_name)
        level = request.form.get('level').strip()
        # I have converted the variable of level into an integer so that I can use the following if statement without
        # crashing the server due to a type error
        # if the level entered is greater than 10 or less than 0 the form response is rejected and the user must
        # re-enter the details correctly
        print(level)
        level = int(level)
        if level > 10 or level < 0:
            return redirect("/admin?error=Please+enter+a+level+between+1+and+10")
        # The line of code below is a python function that collects the exact time (down to the millisecond) at the
        # time that the function is called upon
        date_added = datetime.datetime.now()
        print(date_added)
        print(request.form)
        con = create_connection(DATABASE)
        # The new inclusion in this query is NULL which I have assigned to the column picture, this is because I have
        # not added a user input for pictures and I do not want the query assigning any values to picture by error
        query = "INSERT INTO words (english_translation, te_reo_translation, definition, category_id, level, picture," \
                "date_added, added_by) " \
                "VALUES (?, ?, ?, ?, ?, NULL, ?, ?)"
        cur = con.cursor()

        try:
            cur.execute(query, (english_translation, te_reo_translation,
                                definition, category_id, level, date_added, added_by))
        except sqlite3.IntegrityError:
            con.close()
            return redirect("/admin?error=Duplicate+details+can't+add")

        con.commit()
        con.close()

        return redirect("/")


# Takes the input from the delete_word button on the word info page and passes it along
# to the template delete_word_confirm
@app.route('/delete_word', methods=['POST'])
def render_delete_word():
    if not is_logged_in():
        return redirect('/?message=Need+to+be+logged+in.')
    if request.method == "POST":
        word = request.form.get('word')
        print(word)
        return render_template("delete_word_confirm.html", id=word)
    return redirect("/")


# app route occurs when the user is deleting a word and selects confirm when prompted whether they are sure with their
# decision
@app.route('/delete_word_confirm/<word>')
def delete_word_confirm(word):
    if not is_logged_in():
        return redirect('/?message=Need+to+be+logged+in.')
    con = create_connection(DATABASE)
    query = "DELETE FROM words WHERE word_id= ?"
    cur = con.cursor()
    cur.execute(query, (word,))
    con.commit()
    con.close()
    return redirect("/")


app.run(host='0.0.0.0', debug=True)
