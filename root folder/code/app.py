import os
from flask import Flask,render_template,request
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
matplotlib.use('Agg')
current_directory=os.path.abspath(os.path.dirname(__file__))
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///"+os.path.join(current_directory,"grocery.sqlite3")
db=SQLAlchemy()
db.init_app(app)
app.app_context().push()

class user(db.Model):
    __tablename__='user'
    id=db.Column(db.Integer,unique=True,primary_key=True,autoincrement=True)
    userid=db.Column(db.String)
    name = db.Column(db.String)
    password = db.Column(db.String)

    def __init__(self,userid,name,password):
        self.userid=userid
        self.name=name
        self.password=password


class product(db.Model):
    __tablename__='product'
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    name=db.Column(db.Text,unique=True)
    manufacture_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    category_id=db.Column(db.Integer)
    available_stocks=db.Column(db.Integer)
    rate = db.Column(db.Integer)
    unit = db.Column(db.Text)

    def __init__(self,name,mfd,exd,cid,stocks,rate,unit):
        self.name=name
        self.manufacture_date=mfd
        self.expiry_date=exd
        self.category_id=int(cid)
        self.available_stocks=stocks
        self.rate=int(rate)
        self.unit=unit

class category(db.Model):
    __tablename__='category'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)

    def __init__(self,name):
        self.name=name

class cart(db.Model):
    __tablename__='cart'
    sno = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username=db.Column(db.String )
    p_id = db.Column(db.Integer)
    c_id = db.Column(db.Integer)
    quantity = db.Column(db.Integer)

    def __init__(self,username,pid,cid,quantity):
        self.username=username
        self.p_id=pid
        self.c_id=cid
        self.quantity=quantity

class summary(db.Model):
    __tablename__='summary'
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    c_id=db.Column(db.Integer,primary_key=True)
    p_id = db.Column(db.Integer)
    count = db.Column(db.Integer)

    def __init__(self,cid,pid,count):
        self.c_id=cid
        self.p_id=pid
        self.count=count

@app.route("/")
def index():
    return render_template('login.html')
@app.route("/create_user")
def create_user():
    return render_template('create_user.html')

def password(p):
    if(len(p)>=8):
        return True
    return False
def String(s):
    c=0
    for i in s:
        if(i.isalpha() or i.isspace() ):
            c+=1
        else:
            return False
    if c==len(s):
        return True
    return False

def vdate(m,e):
    s=str(e-m)
    if(s=="0:00:00"):
        return False
    return True
def num(n):
    if n.isnumeric():
        return True
    return False

def username(u):
    if(u!=""):
        r=user.query.filter_by(userid=u).first()

        if(r!=None):
            return False
        else:
            return True

    return False
def date_format(s):
    try:
        y=int(s[0:4])
        m=int(s[5:7])
        d=int(s[8:10])
        return(datetime(y,m,d))
    except:
        if(s==""):
            return False
        return True



@app.route("/save",methods=['POST'])
def save():
    if request.method == "POST":
        n=request.form.get("name")
        un=request.form.get("username")
        p=request.form.get("password")
        if(String(n)):
            if(username(un)):
                if(password(p)):
                    data=user(un,n,p)
                    db.session.add(data)
                    db.session.commit()
                    return home(un)
                else:
                    return render_template("create_user.html", p="Password should all 8 characters",vn=n,vun=un,vp=p)
            else:
                return render_template("create_user.html", un="username already exist",vn=n,vun=un,vp=p)
        else:
            return render_template("create_user.html",n="enter the name",vn=n,vun=un,vp=p)

@app.route("/home/<string:un>")
def home(un):
    r=product.query.all()
    return render_template("home.html",r=r,un=un)
@app.route("/user_login")
def user_login():
    return render_template("login.html")
@app.route("/user_check",methods=['POST'])
def user_check():
    if request.method == "POST":
        un = request.form.get("username")
        p = request.form.get("password")
        r=user.query.filter_by(userid=un).first()
        try:
            if(p==r.password):
                return home(un)

            else:
                return render_template('login.html', p='wrong password')
        except:
            return render_template('login.html',a='user does not exit')

@app.route("/admin_login")
def admin_login():
    return render_template("admin_loginpage.html")
@app.route("/admin_check",methods=['POST'])
def admin_check():
    if request.method == "POST":
        un = request.form.get("admin")
        p = request.form.get("password")
        if(un=="admin"):
            if(p=="12345678"):

                return admin_page()
            else:
                return render_template('admin_loginpage.html', p='wrong password')
        else:
            return render_template('admin_loginpage.html',a='admin does not exit')
@app.route("/admin_page")
def admin_page():
    r=category.query.all()
    return render_template('admin_homepage.html',r=r,i='c')
@app.route("/admin_page_productwise")
def product_wise():
    r=product.query.all()
    return render_template('admin_homepage.html',r=r,i='p')
@app.route("/add_category")
def add_category():
    r=category.query.all()
    return render_template('add_category.html',r=r)

@app.route("/addtoserver",methods=['POST'])
def addtoserver():
    if request.method == "POST":
        n=request.form.get("name")
        if(String(n)==False):
            return render_template('add_category.html',p='Enter the category')
        data=category(n)
        db.session.add(data)
        db.session.commit()
        return add_category()
@app.route("/delete_cat/<string:id>")
def delete_cat(id):
    d=category.query.filter_by(id=id).first()
    db.session.delete(d)
    db.session.commit()
    dp=product.query.filter_by(category_id=id).all()
    if(dp!=[]):
        for i in dp:
            p=product.query.filter_by(id=i.id).first()
            db.session.delete(p)
            db.session.commit()
    return admin_page()
@app.route("/edit_page/<string:id>")
def edit_page(id):
    r=category.query.filter_by(id=id).first()
    name=r.name
    w=category.query.all()
    return render_template("edit_category.html",name=name,id=id,w=w)

@app.route("/update_edit",methods=['POST'])
def update():
    if request.method == "POST":
        id=request.form.get("id")
        name=request.form.get("name")
        if(String(name)):
            r=category.query.filter_by(id=id).first()
            r.name=name
            db.session.commit()
            return admin_page()
        return render_template("edit_page.html",w="only should contain alphabets",id=id,name=name)
@app.route("/add_items/<string:id>/<string:c>")
def add_items(id,c):
    n=id

    return render_template('add_product.html',id=n,c=c)
@app.route("/additemtoserver/<string:c>/<int:n>",methods=['POST'])
def additemtoserver(c,n):
    id=n
    if request.method == "POST":
        name=request.form.get("name")
        mfd = request.form.get("mfd")
        ed = request.form.get("ed")
        rate = request.form.get("rate")
        av=request.form.get("av")
        u=request.form.get("unit")
        mfd=date_format(mfd)
        ed=date_format(ed)
        if(String(name)):
            if(date_format(mfd)):
                if (vdate(mfd,ed)):
                    if (num(rate)):
                        if (num(av)):
                            data=product(name,mfd,ed,id,av,rate,u)
                            db.session.add(data)
                            db.session.commit()
                            return show_items(id,c)
                        return render_template("add_product.html",id=id,c=c,asw="only no should be entered")
                    return render_template("add_product.html", id=id, c=c, rw="only no should be entered")
                return render_template("add_product.html", id=id, c=c, ew="same date as manufacturing Date")
            return render_template("add_product.html",id=id,c=c,mw="enter the Manufacture Date")
        return render_template("add_product.html", id=id, c=c, nw="only alphabets should be entered")
@app.route("/show_items/<string:id>/<string:c>")
def show_items(id,c):
    r=product.query.filter_by(category_id=id)

    return render_template("admin_productpage.html",r=r,c=c,id=id)
@app.route("/edit_item/<string:id>/<string:c>")
def edit_item(id,c):

    r=product.query.filter_by(id=id).first()
    return render_template("edit_product.html",name=r.name,mfd=r.manufacture_date,ed=r.expiry_date,r=r.rate,i=id,cid=r.category_id,av=r.available_stocks,u=r.unit,c=c)
@app.route("/edit_item_at_server/<string:id>/<string:cid>/<string:c>",methods=['POST'])
def edit_item_at_server(id,cid,c):
    if request.method=="POST":
        n=request.form.get("name")
        m = request.form.get("mfd")
        e = request.form.get("ed")
        ra = request.form.get("rate")
        av = request.form.get("available_stocks")
        r=product.query.filter_by(id=id).first()
        r.name=n
        r.manufacture_date=date_format(m)
        r.expiry_date=date_format(e)
        r.available_stocks=int(av)
        r.rate=int(ra)
        db.session.commit()
    return show_items(cid,c)
@app.route("/delete_items/<string:id>/<int:cid>/<string:c>")
def delete_items(id,cid,c):
    d=product.query.filter_by(id=id).first()
    db.session.delete(d)
    db.session.commit()
    return show_items(cid,c)
#-----------------------------------------------------------------------------------------------------------------
@app.route("/search/<un>",methods=['POST'])
def search(un):
    if request.method == "POST":
        v=request.form.get("dropdown")
        n=request.form.get("box")
        if(n!=""):
            if(v=="product"):
                r=product.query.filter_by(name=n).all()
                if(r!=None):
                    return render_template("home.html",r=r,n='name',p='price',m='manufacture date',e='expiry date',q='quality',un=un)
                return render_template("home.html", er="Not available", un=un)
            if (v == "rate"):
                r=product.query.filter_by(rate=n).all()
                if (r != None):
                    return render_template("home.html", r=r,n='name',p='price',m='manufacture date',e='expiry date',q='quality',un=un)
                return render_template("home.html", er="Not available", un=un)
            if (v == "manufacture_date"):
                r = product.query.filter_by(manufacture_date=n).all()
                if (r != None):
                    return render_template("home.html", r=r,n='name',p='price',m='manufacture date',e='expiry date',q='quality',un=un)
                return render_template("home.html", er="Not available", un=un)
            if (v == "expiry_date"):
                r = product.query.filter_by(expiry_date=n).all()
                if(r!=None):
                    return render_template("home.html", r=r,n='name',p='price',m='manufacture date',e='expiry date',q='quality',un=un)
                return render_template("home.html",er="Not available",un=un)
            if (v == "category"):
                c=category.query.filter_by(name=n).first()
                if(c!=None):
                    id=c.id
                    r=product.query.filter_by(category_id=id).all()
                    return render_template("home.html", r=r,n='name',p='price',m='manufacture date',e='expiry date',q='quality',un=un)
                return render_template("home.html",er="Not available",un=un )
        else:
            return home(un)




@app.route("/adding_to_cart/<string:pid>/<string:cid>/<un>",methods=['POST'])
def adding_to_cart(pid,cid,un):
    if request.method == "POST":
        r1=product.query.filter_by(category_id=cid,id=pid).first()

        if(r1!=None):

            q=request.form.get("q")
            data = cart(un, pid, cid, q)
            db.session.add(data)
            db.session.commit()
            r=search(un)
            return home(un)
        else:
            return home(un)
@app.route("/cart/<string:un>")
def cart_section(un):
    r=cart.query.filter_by(username=un).all()
    l=[]
    total=0

    for i in r:
        pid=i.p_id
        cid=i.c_id
        q=i.quantity
        r2=product.query.filter_by(id=pid,category_id=cid).first()
        t=r2.rate*q
        total+=t
        s=(r2.name,r2.rate,q,t,pid,cid,r2.unit)
        l.append(s)
    return render_template("cart.html",r=l,total=total,un=un)
@app.route("/delete_from_cart/<cid>/<pid>/<string:un>")
def delete_from_cart(pid,cid,un):
    d=cart.query.filter_by(p_id=pid,c_id=cid).first()
    db.session.delete(d)
    db.session.commit()
    return cart_section(un)

@app.route("/add_quantity/<pid>/<cid>/<string:un>/<int:q>/<string:n>")
def add_quantity(pid,cid,un,q,n):
    return render_template("add_quantity.html",un=un,q=q,pid=pid,cid=cid,n=n)

@app.route("/add_quantity_to_server/<pid>/<cid>/<string:un>",methods=['POST'])
def add_quantity_to_server(pid,cid,un):
    if request.method == "POST":
        q=request.form.get("quantity")
        r=cart.query.filter_by(username=un,p_id=pid,c_id=cid).first()
        r.quantity=q
        db.session.commit()
        return cart_section(un)

@app.route("/place_a_order/<string:un>")
def place_a_Order(un):
    r=cart.query.filter_by(username=un)
    for i in r:
        s = summary.query.filter_by(p_id=i.p_id).first()
        if(s==None):
            data=summary(i.c_id,i.p_id,i.quantity)
            db.session.add(data)
            db.session.commit()
        else:
            d=summary.query.filter_by(p_id=i.p_id).first()
            d.count+=i.quantity
            db.session.commit()
    for i in r:
        av=product.query.filter_by(id=i.p_id,category_id=i.c_id).first()
        if(av.available_stocks>0):
            rs=av.available_stocks-i.quantity
            if(rs<0):
                rs=0
        r=product.query.filter_by(id=i.p_id,category_id=i.c_id).first()
        r.available_stocks=rs
        db.session.commit()
    try:
        while(True):
           d=cart.query.filter_by(username=un).first()
           db.session.delete(d)
           db.session.commit()
    except:
        pass
    db.session.commit()
    return cart_section(un)
@app.route("/summary")
def summary_section():
    s=summary.query.all()
    name_list=[]
    c=[]
    for i in s:
        p=product.query.filter_by(id=i.p_id,category_id=i.c_id).first()
        try:
            n=p.name
            name_list.append(n)
            c.append(i.count)
        except:
            print("error")

    fig=plt.figure()
    x=np.array(name_list)
    y=np.array(c)
    plt.bar(x,y)
    plt.title("Summary")
    plt.xlabel("products")
    plt.ylabel("sold")
    fig.savefig('static/plot.png')
    plt.close()
    return render_template("summary.html")


if __name__=='__main__':
    app.run(debug=True)


