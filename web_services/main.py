from sqlalchemy.orm import joinedload
from flask import render_template, Response, request, jsonify, flash, redirect, url_for, Flask
import os
import traceback
import pandas as pd
import models
import utils
from database import Session, eng, Base
from passlib.hash import sha256_crypt
from flask_login import login_user, login_required, UserMixin, current_user, logout_user, LoginManager
from database import Base
from models import AOP, DensityMix, ActiveHeadCount, ActiveHeadCountBifrication
app = Flask(__name__)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

app.config['SECRET_KEY'] = 'abcd'


@login_manager.user_loader
def load_user(userid):
    db = Session()
# since the user_id is just the primary key of our user table, use it in the query for the user
    user = db.get(models.User, userid)
    db.close()
    return user


@app.route('/signup/submit/', methods=['GET', 'POST'])
# @login_required
def add_user():
    db = Session()
    userid = request.form.get("userid")
    name = request.form.get("name")
    password = request.form.get("password")

    user = db.query(models.User).filter(models.User.userid == userid).first()

    if user != None:
        return {"detail": f"'{userid}' already registered, Please try from another email"}, 400
    encpassword = sha256_crypt.encrypt(password)
    user = models.User(
        userid=int(userid),
        name=str(name),
        password=encpassword,
        rights=int(request.form.get("rights")),
        location=str(request.form.get("location"))
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    db.close()
    return render_template('admin_home.html', user=current_user)


@app.route("/signup/", methods=['GET', 'POST'])
# @login_required
def signup():
    return render_template('signup.html', userid=current_user)


@app.route("/")
def index():
    return render_template("login.html", userid=current_user)


@app.route("/logout/")
# @login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/admin/home", methods=['GET', 'POST'])
# @login_required
def admin_home(db=Session()):

    if request.method == "POST":
        # Handle document upload here

        try:
            file1 = request.files['file1']
            file2 = request.files['file2']
            file3 = request.files['file3']

            # print(type(file3))

            df1 = pd.read_csv(file1)
            df2 = pd.read_csv(file2)
            df3 = pd.read_csv(file3)

            myDict = {'UHD': 'TrueflexUHD', 'HD': ['TrueflexLCM', 'KIRANA'], 'MD': [
                'TRUEFLEXRegular', 'LMA', 'EFLEX'], 'LD': ['RFK', 'CB', 'EKARTWM', 'EKARTOthers']}

            activeheadcount_bifrication_mapping = {
                'UHD': 'uhd',
                'HD': 'high',
                'MD': 'medium',
                'LD': 'low'
            }

            print(myDict)

            # Verify columns in CSV files
            expected_columns_1 = ['loc_name', 'zone', 'gm', 'aop_count']
            expected_columns_2 = ['loc_name', 'uhd', 'high', 'medium', 'low']
            expected_columns_3 = ['loc_name', 'EFLEX', 'EKARTOthers', 'EKARTWM', 'KIRANA','LMA', 'CB', 'RFK', 'TRUEFLEXRegular', 'TrueflexLCM', 'TrueflexUHD']
            if not all(col in df1.columns for col in expected_columns_1) or not all(col in df2.columns for col in expected_columns_2):
                flash(
                    "Invalid columns in CSV files. Please ensure both files have the required columns.")
                return redirect(url_for('upload_files'))

            # Preprocess data to remove '%' symbols
            df2[['uhd', 'high', 'medium', 'low']] = df2[['uhd', 'high', 'medium', 'low']].replace({'%': ''}, regex=True)

            # Save data to database tables
            aop_data = df1.to_dict(orient='records')
            densitymix_data = df2.to_dict(orient='records')
            

            activeheadcount_data = []
            activeheadcountbif_data = []  # New list for ActiveHeadCountBifrication data
            
            for record in df3.to_dict(orient='records'):
                loc_name = record['loc_name']
                activeheadcount_entry = {'loc_name': loc_name}
                activeheadcountbif_entry = {'loc_name': loc_name}
                
                for key, value in myDict.items():
                    if isinstance(value, str):  # Single column case
                        activeheadcount_entry[key] = record.get(value, None)
                    elif isinstance(value, list):  # Multiple columns case
                        total = sum(record.get(col, 0) for col in value)
                        activeheadcount_entry[key] = total
                        activeheadcountbif_entry[activeheadcount_bifrication_mapping[key]] = total
                
                # Calculate the "uhd" value here based on the other columns
                calculated_uhd_value = record.get('TrueflexUHD', 0) + record.get('OtherUHDColumn', 0)  # Replace 'OtherUHDColumn' with the actual column name
    
                # Add the "uhd" key to the dictionary and assign the calculated value
                activeheadcountbif_entry['uhd'] = calculated_uhd_value
                
                activeheadcount_data.append(activeheadcount_entry)
                activeheadcountbif_data.append(activeheadcountbif_entry)
                
            active_head_count_records = db.query(ActiveHeadCount).all()
            active_head_count_bif_records = db.query(ActiveHeadCountBifrication).all()

            print("ActiveHeadCount Records:", active_head_count_records)
            print("ActiveHeadCountBifrication Records:", active_head_count_bif_records)

            activeheadcount_data = df3.to_dict(orient='records')
            
            db.bulk_insert_mappings(AOP, aop_data)
            db.bulk_insert_mappings(DensityMix, densitymix_data)
            db.bulk_insert_mappings(ActiveHeadCount, activeheadcount_data)
            # Insert into ActiveHeadCountBifrication
            db.bulk_insert_mappings(ActiveHeadCountBifrication, activeheadcountbif_data)
            db.commit()

            flash("Data uploaded successfully!")
        except Exception as e:
            db.rollback()
            db.close()
            flash(f"Error: {str(e)}")

    return render_template("admin_home.html", userid=current_user)


@app.route("/standard/home")
# @login_required
def standard_home():
    return render_template("standard_home.html", userid=current_user)


@app.route("/login/", methods=['GET', 'POST'])
def login(db=Session()):

    if request.method == "POST":
        userid = request.form.get("userid")
        password = request.form.get("password")

        # user = db.query.filter_by(userid=userid).first()
        user = db.query(models.User).filter_by(userid=userid).first()
        # print (user.password)
        if user and sha256_crypt.verify(password, user.password):
            # Successful login, you can add more logic here (e.g., setting session variables)
            if user.rights == 0:
                A_users = db.query(models.User).filter(
                    models.User.userid != user.userid).all()
                db.close()
                user_type_map = {0: "Admin", 1: "Standard"}
                return render_template("admin_home.html", users=A_users, user_type_map=user_type_map)

                # return redirect(url_for("admin_home"))
            elif user.rights == 1:
                b_users = db.query(models.User).filter(
                    models.User.userid != user.userid).all()
                hub_data = db.query(models.AOP).all()
                db.close()
                user_type_map = {0: "Admin", 1: "Standard"}
                return render_template("standard_home.html", is_aop_data=False, users=b_users, user_type_map=user_type_map, data=hub_data)

                # return redirect(url_for("standard_home"))
        else:
            # Invalid username or password
            db.close()
            return render_template("login.html", error="Invalid userid or password")
    db.close()
    return render_template("login.html", error=None, userid=current_user)


@app.route("/fetch-aop/", methods=['POST'])
def fetch_aop(db=Session()):

    try:
        hub_name = request.form.get('hub_name')
        # is_int = request.form.get("is_int")
        db_aop = db.query(models.AOP).filter(
            models.AOP.loc_name == hub_name).first()
        db_density_mix = db.query(models.DensityMix).filter(
            models.DensityMix.loc_name == hub_name).first()
        db_active_head = db.query(models.ActiveHeadCountBifrication).filter(models.ActiveHeadCountBifrication.loc_name == hub_name).first()
        db.close()
        if db_density_mix is None:
            return {"detail": f"Data not found for {hub_name}"}, 404

        # fetch_int = bool(int(is_int))

        res = utils.calculate_count(db_aop.aop_count, db_density_mix.uhd,
                                    db_density_mix.high, db_density_mix.medium, db_density_mix.low,)
        
        res2 = (db_active_head.uhd, db_active_head.high, db_active_head.medium, db_active_head.low)
        
        res3 = utils.slot_left(res,db_active_head.uhd, db_active_head.high, db_active_head.medium, db_active_head.low)

        return render_template("standard_home.html", data=res, data2 = res2, data3 = res3, is_aop_data=True, is_active_head=True)
        

    except Exception as err:
        traceback.print_exc()
        db.close()
        return {"detail": str(err)}, 400

@app.route('/update-active-count/', methods=['POST'])
def update_active_count(db=Session()):
    try:
        data = request.json
        hub_name = data.get('hubName')
        model = data.get('model')
        username = data.get('username')
        casper_id = data.get('casperId')
        rate = data.get('rate')

        # Retrieve the location based on the hub_name
        location = db.query(models.AOP).filter_by(loc_name=hub_name).first()
        
        # Update the activeheadcount table here
        active_head_count = db.query(models.ActiveHeadCount).filter_by(loc_name=location).first()
        
        # Update the count for the selected model
        setattr(active_head_count, model, getattr(active_head_count, model) + 1)
        
        db.commit()

        response_data = {'message': 'Active count updated successfully.'}
        return render_template("standard_home.html")
        
        return jsonify(response_data)
    except Exception as err:
        traceback.print_exc()
        db.rollback()
        return {'detail': str(err)}, 400



if __name__ == "__main__":

    if not os.path.exists("userManagement.db"):
        pass

    Base.metadata.create_all(eng)
    app.run(debug=True)
