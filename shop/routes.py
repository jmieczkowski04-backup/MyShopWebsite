from flask import render_template, redirect, url_for, flash, abort, request, session
from markupsafe import Markup
from flask_login import login_user, login_required, logout_user
from shop.login_manager import url_has_allowed_host_and_scheme

from shop import app, db
from shop.models import Item, User
from shop.forms import RegisterForm, LoginForm, AddToCartForm, ChangeAmountForm, BuyForm, SearchForm


@app.route('/home')
@app.route('/', methods=['POST', 'GET'])
def home_page():
    search_form = SearchForm()
    return render_template("index.html", search_form=search_form)


@app.route('/shop', methods=['POST', 'GET'])
@login_required
def shop_page():
    form = AddToCartForm()
    search_form = SearchForm()

    if request.method == "POST":
        item_id = request.form['purchased_item']
        item = Item.query.get(item_id)
        item_amount = form.amount.data
        if form.validate_on_submit():
            if session.get('cart') is None:
                session['cart'] = {}
            session['cart'][item_id] = item_amount
            flash(Markup(f"You added {item.name} (x{item_amount}) to your cart - see it <a href='{url_for('cart_page')}' class='alert-link'> here </a>"),
                  category='success')
            return redirect(url_for('shop_page', per_page=request.args.get('per_page', 10)))
        else:
            flash(f"There was a problem with adding {item.name} to your cart", category='danger')
            return redirect(url_for('shop_page', per_page=request.args.get('per_page', 10)))

    else:
        per_page = request.args.get('per_page', 10, type=int)
        page = request.args.get('page', 1, type=int)
        searched_name = request.args.get('search_name', '')
        query = db.select(Item)
        if searched_name:
            query = query.where(Item.name.ilike(f"%{searched_name}%"))

        items = db.paginate(query, page=page, per_page=per_page)
        next_url = url_for('shop_page', page=items.next_num) if items.has_next else None
        prev_url = url_for('shop_page', page=items.prev_num) if items.has_prev else None
        return render_template('shop.html', items=items.items, pages=items.pages, page=items.page,
                               next_url=next_url, prev_url=prev_url,
                               form=form, search_form=search_form)


@app.route('/cart', methods=['POST', 'GET'])
@login_required
def cart_page():
    change_amount_form = ChangeAmountForm()
    buy_form = BuyForm()
    search_form = SearchForm()

    if request.method == 'POST':
        if change_amount_form.validate_on_submit():
            item_id = request.form['selected_item']
            if change_amount_form.minus_submit.data:
                session['cart'][item_id] -= 1
                print(session['cart'])
            elif change_amount_form.plus_submit.data:
                session['cart'][item_id] += 1
                print(session['cart'])
            else:
                del session['cart'][item_id]

            session.modified = True
            return redirect(url_for('cart_page'))

    else:
        items = []
        items_amounts = []
        counter_list = []
        counter = 1
        total = 0
        if session.get('cart') is not None:
            items_amounts = session['cart'].values()
            print(items_amounts)
            items_id = session['cart'].keys()
            for id, amount in zip(items_id, items_amounts):
                item = Item.query.get(id)
                items.append(item)
                counter_list.append(counter)
                counter += 1
                total += item.price * amount

        return render_template('cart.html', items=items, items_amounts=items_amounts,
                               total=total, counter_list=counter_list, zip=zip,
                               change_amount_form=change_amount_form, buy_form=buy_form, search_form=search_form)


@app.route('/search', methods=["POST"])
def search_page():
    search_form = SearchForm()
    search_name = search_form.search_input.data
    return redirect(url_for('shop_page', search_name=search_name))


@app.route('/register', methods=['POST', 'GET'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email=form.email.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash("You have successfully registered :)", category='success')
        return redirect(url_for('shop_page', per_page=request.args.get("per_page", 10)))

    if form.errors:
        flash("There were problems with creating your account", category='danger')

    return render_template('register.html', form=form, search_form=None)


@app.route('/login', methods=['POST', 'GET'])
def login_page():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        login_user(user, remember=form.remember_me.data)
        flash("You have successfully logged in :)", category='info')

        next = request.args.get('next')
        if not url_has_allowed_host_and_scheme(next, request.host) and next is not None:
            return abort(400)

        if next is None:
            return redirect(url_for('shop_page', per_page=request.args.get('per_page', 10)))
        else:
            return redirect(url_for(next, per_page=request.args.get('per_page', 10)))

    if form.errors:
        flash("There were problems with logging into your account", category='danger')

    return render_template('login.html', form=form, search_form=None)


@app.route("/logout")
@login_required
def logout_page():
    try:
        logout_user()
        session.clear()
        flash("You have been logged out ;)", category='info')
        return redirect(url_for('home_page', per_page=request.args.get('per_page', 10)))
    except Exception:
        flash("Something went wrong while logging out...", category='danger')
        return redirect(url_for('login_page', per_page=request.args.get('per_page', 10)))
