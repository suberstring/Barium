from flask import Flask,render_template,request, url_for, redirect, flash, session
import sys,os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin,login_required,login_user,current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'
login_manager = LoginManager(app)
login_manager.login_view = 'login'
prefix = 'sqlite:///'
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))  # 用户名
    password_hash = db.Column(db.String(128))  # 密码散列值

    def set_password(self, password):  # 用来设置密码的方法，接受密码作为参数
        self.password_hash = generate_password_hash(password)  # 将生成的密码保持到对应字段

    def validate_password(self, password):  # 用于验证密码的方法，接受密码作为参数
        return check_password_hash(self.password_hash, password)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30))
    text = db.Column(db.String(2000))
    writer = db.Column(db.String(20))

@login_manager.user_loader
def load_user(user_id):  # 创建用户加载回调函数，接受用户 ID 作为参数
    user = User.query.get(int(user_id))  # 用 ID 作为 User 模型的主键查询对应的用户
    return user

@app.route('/index')
def hello():
    session['loggedin'] = False
    session['logacc'] = None
    return render_template('index.html', bfb=[["Helloworld","E.R","/posts/15"],["Jupiter","Haf.R","/er/1"]])

@app.route('/er/1')
def e():
    return "1"

@app.route('/deleteall')
def dels():
    movies = User.query.all()
    movie_ = Post.query.all()
    for movie in movies:
        db.session.delete(movie)
    db.session.commit()

@app.route('/explore')
def expl():
    alposts = Post.query.all()
    pst_lst = []
    for i in alposts:
        pst_lst.append([i.title,len(i.text),"/posts/"+str(i.id),i.writer])
    return render_template('explore.html',exlst=pst_lst)

@app.route("/posts/<int:post_id>")
def ras(post_id):
    rdpost = Post.query.get_or_404(post_id)
    return render_template('postrend.html',postt=rdpost.title,postxt=rdpost.text,postwt=rdpost.writer)

@app.errorhandler(404)  # 传入要处理的错误代码
def page_not_found(e):
    return render_template('404.html'), 404

@app.route("/login",methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))

        user = User.query.first()
        # 验证用户名和密码是否一致
        if username == user.username and user.validate_password(password):
            login_user(user)  # 登入用户
            flash('Login success.')
            return redirect('create')  # 重定向到主页

        flash('Invalid username or password.')  # 如果验证失败，显示错误消息
        return redirect(url_for('login'))  # 重定向回登录页面

    return render_template('login.html')

@app.route("/register",methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('register'))
        elif username in User.query.all():
            flash('The user is exist!!!')
            return redirect(url_for('register'))
        else:
            user = User(username=username)
            user.set_password(password)  # 设置密码
            db.session.add(user)
            db.session.commit()
    return render_template('register.html')

@app.route('/create',methods=['GET', 'POST'])
@login_required
def fl_up():
    if request.method == 'POST':  # 判断是否是 POST 请求
        # 获取表单数据
        title = request.form.get('title')  # 传入表单对应输入字段的 name 值
        content = request.form.get('content')
        # 验证数据
        if not title or not content or len(content) > 2000 or len(title) > 30:
            flash('Invalid input.')  # 显示错误提示
            return redirect(url_for('index'))  # 重定向回主页
        db.session.add(Post(title=title, text=content,writer=current_user.username))  # 添加到数据库会话
        db.session.commit()  # 提交数据库会话
        flash('Post has been uploaded successfully.')  # 显示成功创建的提示
        return redirect(url_for('hello'))  # 重定向回主页
    return render_template('create.html')