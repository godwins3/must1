from flask import Flask, session, url_for, redirect, render_template, request, abort
from db import *
from db.database import list_users, verify, delete_user_from_db, add_user
from db.database import read_note_from_db, write_note_into_db, delete_note_from_db, match_user_id_with_note_id, read_vehicle_insurance_from_db
from joblib import load


app = Flask(__name__)
app.config.from_object('config')


@app.errorhandler(401)
def FUN_401(error):
    return render_template("page_401.html"), 401

@app.errorhandler(403)
def FUN_403(error):
    return render_template("page_403.html"), 403

@app.errorhandler(404)
def FUN_404(error):
    return render_template("page_404.html"), 404

@app.errorhandler(405)
def FUN_405(error):
    return render_template("page_405.html"), 405

@app.errorhandler(413)
def FUN_413(error):
    return render_template("page_413.html"), 413

@app.route("/")
def FUN_root():
    return render_template("index.html")

@app.route("/public/")
def FUN_public():
    
    if "current_user" in session.keys():
        return render_template("insurance.html")
    else:
        return abort(401)

@app.route("/private/")
def FUN_private():
    if "current_user" in session.keys():
        notes_list = read_note_from_db(session['current_user'])
        notes_table = zip([x[0] for x in notes_list],\
                          [x[1] for x in notes_list],\
                          [x[2] for x in notes_list],\
                          ["/delete_prediction/" + x[0] for x in notes_list])


        return render_template("private_page.html", notes = notes_table)
    else:
        return abort(401)

@app.route("/admin/")
def FUN_admin():
    if session.get("current_user", None) == "ADMIN":
        user_list = list_users()
        user_table = zip(range(1, len(user_list)+1),\
                        user_list,\
                        [x + y for x,y in zip(["/delete_user/"] * len(user_list), user_list)])
        return render_template("admin.html", users = user_table)
    else:
        return abort(401)

@app.route("/delete_prediction/<note_id>", methods = ["GET"])
def FUN_delete_note(note_id):
    if session.get("current_user", None) == match_user_id_with_note_id(note_id): # Ensure the current user is NOT operating on other users' note.
        delete_note_from_db(note_id)
    else:
        return abort(401)
    return(redirect(url_for("FUN_private")))


@app.route("/register_user", methods = ["POST"])
def FUN_add_users():
    if request.form.get('id').upper() in list_users():
        user_list = list_users()
        user_table = zip(range(1, len(user_list)+1),\
                        user_list,\
                        [x + y for x,y in zip(["/delete_user/"] * len(user_list), user_list)])
        return(render_template("register.html", id_to_add_is_duplicated = True, users = user_table))
    if " " in request.form.get('id') or "'" in request.form.get('id'):
        user_list = list_users()
        user_table = zip(range(1, len(user_list)+1),\
                        user_list,\
                        [x + y for x,y in zip(["/delete_user/"] * len(user_list), user_list)])
        return(render_template("register.html", id_to_add_is_invalid = True, users = user_table))
    else:
        add_user(request.form.get('id'), request.form.get('pw'))
        return(redirect(url_for("FUN_login")))
    
@app.route("/login", methods = ["POST"])
def FUN_login():
    id_submitted = request.form.get("id").upper()
    if (id_submitted in list_users()) and verify(id_submitted, request.form.get("pw")):
        session['current_user'] = id_submitted
    
    return(redirect(url_for("FUN_root")))

@app.route("/logout/")
def FUN_logout():
    session.pop("current_user", None)
    return(redirect(url_for("FUN_root")))

@app.route("/delete_user/<id>/", methods = ['GET'])
def FUN_delete_user(id):
    if session.get("current_user", None) == "ADMIN":
        if id == "ADMIN": # ADMIN account can't be deleted.
            return abort(403)

        # [2] Delele the records in database files
        delete_user_from_db(id)
        return(redirect(url_for("FUN_admin")))
    else:
        return abort(401)

@app.route("/add_user", methods = ["POST"])
def FUN_add_user():
    if session.get("current_user", None) == "ADMIN": # only Admin should be able to add user.
        # before we add the user, we need to ensure this is doesn't exsit in database. We also need to ensure the id is valid.
        if request.form.get('id').upper() in list_users():
            user_list = list_users()
            user_table = zip(range(1, len(user_list)+1),\
                            user_list,\
                            [x + y for x,y in zip(["/delete_user/"] * len(user_list), user_list)])
            return(render_template("admin.html", id_to_add_is_duplicated = True, users = user_table))
        if " " in request.form.get('id') or "'" in request.form.get('id'):
            user_list = list_users()
            user_table = zip(range(1, len(user_list)+1),\
                            user_list,\
                            [x + y for x,y in zip(["/delete_user/"] * len(user_list), user_list)])
            return(render_template("admin.html", id_to_add_is_invalid = True, users = user_table))
        else:
            add_user(request.form.get('id'), request.form.get('pw'))
            return(redirect(url_for("FUN_admin")))
    else:
        return abort(401)

@app.route('/cars_disposal', methods = ['POST'])
def predict_car_disposal():

    mileage = request.form.get("text_note_to_take")
    mileage = [[int(mileage)]]
    
    # Load the trained model
    loaded_model = load('cars_disposal_period_model.pkl')
    predict = loaded_model.predict(mileage)
    prediction = predict[0]
    write_note_into_db(session['current_user'], prediction)    

    return(redirect(url_for("FUN_private")))

@app.route('/insurance')
def fun_insurance():
    if "current_user" in session.keys():
        vehicle_list = read_vehicle_insurance_from_db(session['current_user'])
        vehicle_table = zip([x[0] for x in vehicle_list],\
                          [x[1] for x in vehicle_list],\
                          [x[2] for x in vehicle_list],\
                          [x[3] for x in vehicle_list],\
                          [x[4] for x in vehicle_list],\
                          ["/delete_vehicle/" + x[0] for x in vehicle_list])
        return render_template('insurance.html', insurance = vehicle_table)
    else:
        return abort(401)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")