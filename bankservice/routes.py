from flask import render_template, request, redirect, url_for, session
from .models import db, User, AccountInformation, Deposit, Withdraw, Transfer
from werkzeug.security import generate_password_hash, check_password_hash

def init_routes(app):

    # Home route
    @app.route("/")
    def home():
        return render_template("base.html")


    # Sign up route
    @app.route("/sign-up", methods=["GET", "POST"])
    def sign_up():
        if request.method == "POST":
            username=request.form["username"]
            password=request.form["password"]

            # Checks if username already exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                return render_template("error.html", message="Username already exists.")

            # Generating hashed password from user's password
            hashed_password = generate_password_hash(password)
            # Creating new user for the hashed password
            new_user = User(username=username, password=hashed_password)
            try:
                # Adding the new user to the database
                db.session.add(new_user)
                # Commits the database
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return render_template("error.html", message="An error occured while creating your account.", context='signup')
            
            new_account = AccountInformation(
                account_number=f"CHK{new_user.id}",
                balance=0.0,
                account_type="checking",
                user_id=new_user.id
            )
            db.session.add(new_account)
            db.session.commit()

            # Redirect upon successfull register
            return redirect(url_for("success", message="User registered successfully."))
        
        return render_template("signup.html")


    # Creating login route
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username=request.form["username"]
            password=request.form["password"]

            # Filtering the user
            user = User.query.filter_by(username=username).first()
            # Checks the password hash and the user
            if user and check_password_hash(user.password, password):
                # Making 'user_id' hold the user.id
                session['user_id'] = user.id
                # Redirect to user profile
                return redirect(url_for("user_profile"))
            else:
                # Gives an error message and the error.html template
                return render_template("error.html", message="Invalid username or password.")
            
        return render_template("login.html")


    # Creating logout route
    @app.route("/logout")
    def logout():
        # Clears the session data
        session.pop('user_id', None)
        return redirect(url_for('home'))


    # Creating success route
    @app.route("/success")
    def success():
        # Message to the user from success
        message = request.args.get('message')
        return render_template("success.html", message=message)


    # Creating profile route
    @app.route("/profile")
    def user_profile():
        profile = True
        if 'user_id' in session:
            # Getting user id from session
            user_id = session['user_id']
            # Query the db for user from their id
            user = User.query.get(user_id)
            savings_account = AccountInformation.query.filter_by(user_id=user_id, account_type='savings').first()

            if user:
                # Returns the user's profile if user was logged in successully
                return render_template("profile.html", user=user, savings_account=savings_account)
            else:
                # Return error.html if the user is not found
                return render_template("error.html", message="User not found.")
        else:
            # Redirects back to login page if it was not successful
            return redirect(url_for("login"))


    @app.route("/create_savings", methods=["GET", "POST"])
    def create_savings():
        if 'user_id' in session:
            user_id = session['user_id']
            # Checking if the user has savings account
            savings_account = AccountInformation.query.filter_by(user_id=user_id, account_type="savings").first()

            if savings_account:
                return render_template("error.html", message="Savings account has already been created", context='profile')

            if request.method == "POST":    
                
                # Creating new savings account
                new_savings_account = AccountInformation(
                    account_number=f"SAV{user_id}",
                    balance=0.0,
                    account_type="savings",
                    user_id=user_id
                )
                db.session.add(new_savings_account)
                db.session.commit()

                return redirect(url_for("user_profile"))
            
            return render_template("savings.html")
        else:
            return redirect(url_for("login"))


    # Creating a deposit route
    @app.route("/deposit", methods=["GET", "POST"])
    def deposit():
        if request.method == "POST":
            deposit_amount = float(request.form["deposit"])

            # Gets the user's logged session
            user_id = session.get('user_id')
            if user_id:
                # Get the user's account
                account = AccountInformation.query.filter_by(user_id=user_id).first()

                if account:
                    # Update the account balance
                    account.balance += deposit_amount

                    # Create a new deposit record
                    new_deposit = Deposit(amount=deposit_amount, account_id=account.id)

                    db.session.add(new_deposit)
                    db.session.commit()

                    return redirect(url_for("user_profile"))
                else:
                    return render_template("error.html", message="Account not found.")
            else:
                return redirect(url_for("login"))

        return render_template("deposit.html")
    

    @app.route("/withdraw", methods=["GET", "POST"])
    def withdraw():
        if request.method == "POST":
            withdraw_amount = float(request.form["withdraw"])

            # Gets the user's logged session
            user_id = session.get('user_id')
            if user_id:
                # Get the user's account
                account = AccountInformation.query.filter_by(user_id=user_id).first()

                if account:
                    # Check if the account has enough funds
                    if account.balance >= withdraw_amount:

                        # Update the account balance
                        account.balance = account.balance - withdraw_amount

                        # Create a new withdawl record
                        new_withdrawl = Withdraw(amount=withdraw_amount, account_id=account.id)

                        db.session.add(new_withdrawl)
                        db.session.commit()

                        return redirect(url_for("user_profile"))
                    else:
                        return render_template("error.html", message="Insufficent funds.", context='profile')
                else:
                    return render_template("error.html", message="Account not found.", context='profile')
            else:
                return redirect(url_for("login"))

        return render_template("withdraw.html")

    @app.route("/transfer", methods=["GET", "POST"])
    def transfer():
        if request.method == "POST":
            try:
                transfer_amount = float(request.form["transfer_amount"])
                from_account_type = request.form["from_account_type"]
                to_account_type = request.form["to_account_type"]

                # Checks if the account type are the same
                if from_account_type == to_account_type:
                    return render_template("error.html", message="Cannot transfer to the same account type.", context='profile')

                # Gets the user for this session
                user_id = session.get('user_id')
                if user_id:
                    # Get the user's accounts
                    from_account = AccountInformation.query.filter_by(user_id=user_id, account_type=from_account_type).first()
                    to_account = AccountInformation.query.filter_by(user_id=user_id, account_type=to_account_type).first()

                    if from_account and to_account:
                        if from_account.balance >= transfer_amount:
                            # Perform the transfer
                            from_account.balance -= transfer_amount
                            to_account.balance += transfer_amount

                            # Create a new transfer record
                            new_transfer = Transfer(
                                amount=transfer_amount,
                                from_account_id=from_account.id,
                                to_account_id=to_account.id
                            )
                            
                            db.session.add(new_transfer)
                            db.session.commit()

                            return redirect(url_for("user_profile"))
                        else:
                            return render_template("error.html", message="Insufficient funds.", context='profile')
                    else:
                        return render_template("error.html", message="Account not found.", context='profile')
                else:
                    return redirect(url_for("login"))
            except ValueError:
                return render_template("error.html", message="Invalid transfer amount.", context='profile')

        return render_template("transfer.html")


    # Creating records route
    @app.route("/records")
    def records():
        if 'user_id' in session:
            user_id = session['user_id']

            account = AccountInformation.query.filter_by(user_id=user_id).first()

            if account:
                # Getting all queries in deposit
                deposits = Deposit.query.filter_by(account_id=account.id).all()
                
                # Getting all queries in withdraw
                withdrawls = Withdraw.query.filter_by(account_id=account.id).all()

                # Getting all queries in transfer
                transfers_recieved = Transfer.query.filter_by(to_account_id=account.id).all()

                transactions = {
                    "deposits": deposits,
                    "withdrawls": withdrawls,
                    "transfers_recieved": transfers_recieved
                }

                return render_template("records.html", transactions=transactions)
            else:
                return render_template("error.html", message="Account not found.", context='profile')
        else:
            return redirect(url_for("login"))
