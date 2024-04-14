from flask import Flask, render_template, request, redirect, url_for
import pymysql
import os
from werkzeug.utils import secure_filename
app = Flask(__name__, template_folder='templates')
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Srushob123$'
app.config['MYSQL_DB'] = 'formula1'
#app.config['UPLOAD_FOLDER'] = 'uploads'
db_connection = pymysql.connect(
    host="127.0.0.1",
    user="root",
    password="Srushob123$",
    database="formula1",
    cursorclass=pymysql.cursors.DictCursor  # This ensures query results are returned as dictionaries
)

mysql = pymysql.connect(host=app.config['MYSQL_HOST'], user=app.config['MYSQL_USER'],
                        password=app.config['MYSQL_PASSWORD'], db=app.config['MYSQL_DB'])
cursor = mysql.cursor(pymysql.cursors.DictCursor)

cursor.execute('''
    CREATE TABLE IF NOT EXISTS FantasyTeams (
        id INT AUTO_INCREMENT PRIMARY KEY,
        team_name VARCHAR(25) NOT NULL,
        driver_name VARCHAR(25) NOT NULL,
        logo_path VARCHAR(25)
    )
''')

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        if password == 'aksrkan':
            # Redirect to the home page if the password is correct
            return render_template('index.html')
        else:
            # Redirect back to the login page if the password is incorrect
            return redirect(url_for('login_page'))
@app.route('/drivers')
def drivers():
    cursor.execute('SELECT Driver_Name FROM Drivers')
    drivers_data = [row['Driver_Name'] for row in cursor.fetchall()]
    return render_template('drivers_list.html', drivers=drivers_data)

@app.route('/teams')
def teams():
    cursor.execute('SELECT Team_name from teams')
    teams_data = [row['Team_name'] for row in cursor.fetchall()]
    return render_template('teams_list.html', teams=teams_data)

@app.route('/driver_details/<Driver_Name>')
def driver_details(Driver_Name):
    cursor.execute('SELECT Driver_Name,Team_name,Country,Podiums,Points FROM Drivers WHERE Driver_Name = %s', (Driver_Name,))
    driver_details = cursor.fetchone()
    if driver_details:
        return render_template('driver_details.html', driver_name=driver_details['Driver_Name'], team=driver_details['Team_name'],country=driver_details['Country'],podiums=driver_details['Podiums'],points=driver_details['Points'])
    else:
        return 'Driver not found'
@app.route('/team_details/<Team_name>')
def team_details(Team_name):
    cursor.execute('SELECT Team_name,CTO,Principal,Driver1,Driver2 FROM teams WHERE Team_name = %s', (Team_name,))
    team_details = cursor.fetchone()

    if team_details:
        return render_template('team_details.html', team_name=team_details['Team_name'], CTO=team_details['CTO'],principal=team_details['Principal'],driver1=team_details['Driver1'],driver2=team_details['Driver2'])
    else:
        return 'Team not found'

@app.route('/circuits')
def circuits():
    cursor.execute('SELECT * FROM Circuit')
    circuits_data = cursor.fetchall()
    return render_template('circuits_list.html', circuits=circuits_data)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/fantasy', methods=['GET', 'POST'])
def fantasy():
    if request.method == 'POST':
        team_name = request.form['team_name']
        driver_name = request.form['driver']
        driver2_name = request.form['driver2']
        circuit_name = request.form['circuit']
        livery_name = request.form['livery']
        email = request.form['email']

        # Check if the file is present in the request
        if 'logo' in request.files:
            logo_file = request.files['logo']

            # Check if the file is allowed and secure the filename
            if logo_file and allowed_file(logo_file.filename):
                filename = secure_filename(logo_file.filename)
                logo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                # Save the file to the upload folder
                logo_file.save(logo_path)
            else:
                return 'Invalid file type or filename'

        return redirect(url_for('fantasy_success', team_name=team_name))
    else:
        cursor.execute('SELECT Driver_Name FROM Drivers')
        drivers_data = [row['Driver_Name'] for row in cursor.fetchall()]


        cursor.execute('SELECT circuit_name FROM Circuit')
        circuits_data = [row['circuit_name'] for row in cursor.fetchall()]

        cursor.execute('SELECT livery_name FROM Livery_teams')
        liveries_data = [row['livery_name'] for row in cursor.fetchall()]

        return render_template('fantasy.html', drivers=drivers_data, circuits=circuits_data, liveries=liveries_data)

@app.route('/create_team')
def create_team():
    cursor.execute('SELECT * FROM FantasyTeams')
    fantasy_data = cursor.fetchall()
    return render_template('fantasy_success.html', fantasy=fantasy_data)

@app.route('/livery_form', methods=['GET'])
def livery_form():
    # Fetch team names from the Livery table
    with db_connection.cursor() as cursor:
        cursor.execute("SELECT team_name FROM livery_teams;")
        teams = cursor.fetchall()
    return render_template('livery_form.html', teams=teams)
@app.route('/get_livery_info', methods=['POST'])
def get_livery_info():
    try:
        team_name = request.form['team_name']

        with db_connection.cursor() as cursor:
            cursor.execute("SELECT * FROM livery_teams WHERE team_name=%s;", (team_name,))
            livery_info = cursor.fetchall()

        # Generate HTML content for livery information
        html_content = "<h2>Livery Information</h2>"
        html_content += "<table border='1'>"
        html_content += "<tr><th>Livery Name</th><th>Livery ID</th></tr>"
        for row in livery_info:
            html_content += f"<tr><td>{row['livery_name']}</td><td>{row['Livery_id']}</td></tr>"
        html_content += "</table>"

        return html_content

    except Exception as e:
        return f"An error occurred: {str(e)}"
@app.route('/races')
def races():
    cursor.execute('SELECT * FROM races')
    races_data = cursor.fetchall()
    return render_template('Races.html', races=races_data)
@app.route('/rankings')
def rankings():
    with db_connection.cursor() as cursor:
        cursor.execute("SELECT Driver_Name FROM Drivers ORDER BY Points DESC LIMIT 3")
        top_3_drivers = cursor.fetchall()

    return render_template('rankings.html', drivers=top_3_drivers)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
