from flask import Flask, render_template,request,redirect,session,url_for,flash
import pymysql
from flask_login import LoginManager
from config import connection
from datetime import timedelta

app = Flask(__name__)
app.secret_key = '12345678'  # 用于 session 管理
login_manager = LoginManager()
login_manager.init_app(app)

db = pymysql.connect(
    host="localhost",       # 数据库地址，通常是 localhost
    user="root",            # 你的数据库用户名
    password="Jianghuweizhi100",    # 填入密码
    database="logistics", # 确保这个数据库已存在
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor  # 返回字典形式
)

cursor = db.cursor()

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)
# 首页
@app.route('/')
def index():
    return redirect(url_for('login'))

# 注册页面
@app.route('/register', methods=['GET', 'POST'])
def register():
    error_msg = None  # 初始化
    if request.method == 'POST':
        adminid = request.form['adminid']
        password = request.form['password']
        name = request.form['name']
        telephoneno = request.form['telephoneno']

        conn = connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admin WHERE adminID = %s", (adminid,))
        if cursor.fetchone():
            error_msg = "管理员已存在，请更换ID"
            cursor.close()
            return render_template('register.html', error_msg=error_msg)
        cursor.execute("INSERT INTO admin (adminID, password, name, telephoneno) VALUES (%s, %s, %s, %s)",
                       (adminid, password, name, telephoneno))
        db.commit()
        cursor.close()
        flash("注册成功，请登录！", "success")
        return redirect(url_for('login'))
    return render_template('register.html', error_msg=error_msg)

# 登录页面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        adminid = request.form['adminid']
        password = request.form['password']

        conn = connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admin WHERE adminID = %s AND password = %s", (adminid, password))
        admin = cursor.fetchone()
        cursor.close()

        if admin:
            session['adminid'] = adminid
            return redirect(url_for('dashboard'))
        else:
            return "用户名或密码错误！"
    return render_template('login.html')

# 登出
@app.route('/logout')
def logout():
    session.pop('adminid', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'adminid' not in session:
        return redirect(url_for('login'))
    conn = connection()
    cursor = conn.cursor()
    # 今日订单数
    cursor.execute("SELECT COUNT(*) AS cnt FROM orders WHERE DATE(setting_time)=CURDATE()")
    today_orders = cursor.fetchone()['cnt']

    # 运输中包裹数
    cursor.execute("SELECT COUNT(*) AS cnt FROM commodity WHERE cstatus='运输中'")
    shipping_count = cursor.fetchone()['cnt']

    # 异常包裹数
    cursor.execute("SELECT COUNT(*) AS cnt FROM commodity WHERE cstatus='延误'")
    delayed_count = cursor.fetchone()['cnt']

    # 快递员数量
    cursor.execute("SELECT COUNT(*) AS cnt FROM courier")
    courier_count = cursor.fetchone()['cnt']

    # 订单状态分布
    cursor.execute("SELECT cstatus, COUNT(*) AS cnt FROM commodity GROUP BY cstatus")
    status_rows = cursor.fetchall()
    status_map = {'订单已创建': 0, '运输中': 0, '已送达': 0, '延误': 0}
    for row in status_rows:
        status_map[row['cstatus']] = row['cnt']
    status_data = [
        status_map['订单已创建'],
        status_map['运输中'],
        status_map['已送达'],
        status_map['延误']
    ]

    # 近7天订单趋势
    cursor.execute("""
        SELECT DATE(setting_time) as day, COUNT(*) as cnt
        FROM orders
        WHERE setting_time >= DATE_SUB(CURDATE(), INTERVAL 6 DAY)
        GROUP BY day
        ORDER BY day
    """)
    trend = cursor.fetchall()
    trend_labels = [str(row['day']) for row in trend]
    trend_data = [row['cnt'] for row in trend]
    conn.close()
    return render_template(
        'dashboard.html',
        adminid=session['adminid'],
        today_orders=today_orders,
        shipping_count=shipping_count,
        delayed_count=delayed_count,
        courier_count=courier_count,
        status_data=status_data,
        trend_labels=trend_labels,
        trend_data=trend_data
    )


@app.route('/get_logistics')
def get_logistics():
    if 'userid' not in session:
        return "未登录"

    userid = session['userid']
    cursor = db.cursor()
    cursor.execute("""
        SELECT c.commodityID, c.cstatus, c.logistic_timeline, c.Expdeliverytime
        FROM commodity c
        JOIN orders o ON c.orderID = o.orderID
        WHERE o.recipientID = %s
    """, (userid,))
    logistics = cursor.fetchall()
    cursor.close()

    if not logistics:
        return "暂无物流信息。"

    html = "<ul>"
    for l in logistics:
        html += f"<li>货物ID: {l[0]} | 状态: {l[1]} | 预计送达: {l[3]}<br>物流轨迹: {l[2]}</li>"
    html += "</ul>"
    return html

#展示订单信息
@app.route('/orders')
def orders():
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders")
    orders_data = cursor.fetchall()
    conn.close()
    return render_template("orders.html", orders=orders_data)

@app.route('/commodities')
def commodities():
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM commodity")
    commodities_data = cursor.fetchall()
    conn.close()
    return render_template("commodities.html", commodities=commodities_data)

#订单评价页面
@app.route('/evaluation')
def evaluation():
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM evaluation")
    evaluation_data = cursor.fetchall()
    conn.close()
    return render_template("evaluation.html", evaluation=evaluation_data)

#删除订单
@app.route('/delete_order/<order_id>', methods=['POST'])
def delete_order(order_id):
    conn = connection()
    try:
        cursor = conn.cursor()
        # 开始事务
        conn.begin()

        # 删除评价
        cursor.execute("DELETE FROM evaluation WHERE orderID = %s", (order_id,))
        # 删除商品
        cursor.execute("DELETE FROM commodity WHERE orderID = %s", (order_id,))
        # 删除订单
        cursor.execute("DELETE FROM orders WHERE orderID = %s", (order_id,))

        # 提交事务
        conn.commit()
        message = f"订单 {order_id} 及其相关数据已成功删除。"
    except Exception as e:
        conn.rollback()
        message = f"删除订单失败：{str(e)}"
    finally:
        conn.close()
    return redirect(url_for('orders')) 

@app.route('/personnel',methods=['GET','POST'])
def personnel():
    conn = connection()
    cursor = conn.cursor()

    # 查询三类人员及其基本信息
    cursor.execute('''
        SELECT u.UserID, u.name, u.telephoneno, r.preffered_payment_methods, r.default_shippingaddr
        FROM Users u 
        JOIN recipient r ON u.UserID = r.UserID;
    ''')
    recipients = cursor.fetchall()

    cursor.execute('''
        SELECT u.UserID, u.name, u.telephoneno, a.shippingaddr
        FROM Users u 
        JOIN addresser a ON u.UserID = a.UserID;
    ''')
    addressers = cursor.fetchall()

    cursor.execute('''
        SELECT u.UserID, u.name, u.telephoneno, c.delivery_area
        FROM Users u 
        JOIN courier c ON u.UserID = c.UserID;
    ''')
    couriers = cursor.fetchall()

    conn.close()

    return render_template('personnel.html',
                           recipients=recipients,
                           addressers=addressers,
                           couriers=couriers)


@app.route('/add_personnel', methods=['GET', 'POST'])
def add_personnel():
    error_msg = None  # 初始化错误信息
    conn = connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        telephoneno = request.form['telephoneno']
        role = request.form['role']
        try:
            # 查找当前最大UserID（Uxxx形式），并生成新的UserID
            cursor.execute("""
                SELECT MAX(CAST(SUBSTRING(UserID, 2) AS UNSIGNED)) AS max_num
                FROM Users
                WHERE UserID LIKE 'U%'
                FOR UPDATE
            """)
            result = cursor.fetchone()
            current_max = result['max_num'] if result['max_num'] else 0
            new_num = current_max + 1
            userid = f"U{new_num:03d}"  # 生成U001、U002等格式

            cursor.execute(
                "INSERT INTO Users (UserID, name, telephoneno, role) VALUES (%s, %s, %s, %s)",
                (userid, name, telephoneno, role)
            )
            conn.commit()
            flash("添加人员信息成功！", "success")  # 添加成功提示
        except Exception as e:
            conn.rollback()
            error_msg = f"添加人员失败：{str(e)}"

    # 查询收件人
    cursor.execute('''
        SELECT U.UserID, U.name, U.telephoneno, R.preffered_payment_methods, R.default_shippingaddr
        FROM Users U JOIN recipient R ON U.UserID = R.UserID
    ''')
    recipients = cursor.fetchall()

    # 查询发件人
    cursor.execute('''
        SELECT U.UserID, U.name, U.telephoneno, A.shippingaddr
        FROM Users U JOIN addresser A ON U.UserID = A.UserID
    ''')
    addressers = cursor.fetchall()

    # 查询快递员
    cursor.execute('''
        SELECT U.UserID, U.name, U.telephoneno, C.delivery_area
        FROM Users U JOIN courier C ON U.UserID = C.UserID
    ''')
    couriers = cursor.fetchall()

    conn.close()
    return render_template(
        'personnel.html',
        recipients=recipients,
        addressers=addressers,
        couriers=couriers,
        error_msg=error_msg
    )

#更新货物物流信息
@app.route('/update_timeline/<commodity_id>', methods=['POST'])
def update_timeline(commodity_id):
    new_timeline = request.form['new_timeline']
    new_status = request.form['new_status']
    conn = connection()
    try:
        cursor = conn.cursor()
        cursor.callproc('UpdateLogisticTimeline', (commodity_id, new_timeline,new_status))
        conn.commit()
        flash(f'更新成功：货物 {commodity_id} 的物流状态已更新。', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'更新失败：{str(e)}', 'danger')
    finally:
        conn.close()
    return redirect(url_for('commodities'))


@app.route('/add_order', methods=['GET', 'POST'])
def add_order():
    conn = connection()
    cursor = conn.cursor()
    try:
        # 获取发件人/收件人列表
        cursor.execute("""
            SELECT a.UserID, a.shippingaddr, u.name 
            FROM addresser a
            JOIN users u ON a.UserID = u.UserID
            """)
        addresser_list = cursor.fetchall()

        cursor.execute("""
            SELECT r.UserID, r.default_shippingaddr, u.name 
            FROM recipient r
            JOIN users u ON r.UserID = u.UserID
            """)
        recipient_list = cursor.fetchall()

        if request.method == 'POST':
        # 获取表单数据
            sender_id = request.form['senderID']
            recipient_id = request.form['recipientID']
            dispatch_addr = request.form['dispatchaddr']
            receipt_addr = request.form['reciptaddr']
            commodity_id = request.form['commodityID']
            try:
                # 开启事务
                conn.begin()

                # 获取当前最大订单号（带行锁）
                cursor.execute("""
                    SELECT MAX(CAST(SUBSTRING(orderID, 2) AS UNSIGNED)) AS max_num 
                    FROM orders 
                    WHERE orderID LIKE 'O%' 
                    FOR UPDATE
                """)
                result = cursor.fetchone()
                current_max = result['max_num'] if result['max_num'] else 0

                # 生成新订单ID
                new_num = current_max + 1
                order_id = f"O{new_num:04d}"  # 格式化为O0001

                # 获取当前时间
                cursor.execute("SELECT NOW() as now_time")
                now_time = cursor.fetchone()['now_time']
                # 计算预期送达时间（now_time 是 datetime 类型）
                Expdeliverytime = now_time + timedelta(days=4)

                # 插入订单
                cursor.execute('''
                    INSERT INTO orders 
                    (orderID, ostatus, dispatchaddr, reciptaddr, senderID, recipientID, setting_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', (order_id, '订单已创建', dispatch_addr, receipt_addr, sender_id, recipient_id, now_time))

                # 随机分配一个快递员
                cursor.execute("SELECT UserID FROM courier ORDER BY RAND() LIMIT 1")
                courier = cursor.fetchone()
                courier_id = courier['UserID'] if courier else None

                # 生成物流信息
                logistic_timeline = f"{now_time} 已创建订单"

                # 插入商品
                cursor.execute('''
                    INSERT INTO commodity 
                    (commodityID, cstatus, orderID, logistic_timeline, Expdeliverytime, courierID)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (commodity_id, '订单已创建', order_id, logistic_timeline, Expdeliverytime, courier_id))

                conn.commit()
                return redirect(url_for('orders'))

            except pymysql.IntegrityError as e:
                conn.rollback()
                error_msg = "订单号冲突，请重试"
            except Exception as e:
                conn.rollback()
                error_msg = f"系统错误：{str(e)}"
    
            return render_template('add_order.html',
                error_msg=error_msg,
                addresser_list=addresser_list,
                recipient_list=recipient_list)

        return render_template('add_order.html',
            addresser_list=addresser_list,
            recipient_list=recipient_list)
    finally:
        cursor.close()
        conn.close()

#含有视图的物流综合信息查询
@app.route('/commodity_view', methods=['GET'])
def commodity_view():
    order_filter = request.args.get('orderID', '').strip()
    commodity_filter = request.args.get('commodityID', '').strip()
    courier_filter = request.args.get('courierID', '').strip()
    conn = connection()
    cursor = conn.cursor()

    sql = "SELECT * FROM view_commodity_info WHERE 1=1"
    params = []

    if order_filter:
        sql += " AND orderID = %s"
        params.append(order_filter)
    if commodity_filter:
        sql += " AND commodityID = %s"
        params.append(commodity_filter)
    if courier_filter:
        sql += " AND courierID = %s"
        params.append(courier_filter)

    cursor.execute(sql, tuple(params))
    records = cursor.fetchall()
    conn.close()
    return render_template(
        'commodity_view.html',
        commodities=records,
        order_filter=order_filter,
        commodity_filter=commodity_filter,
        courier_filter=courier_filter
    )

if __name__ == '__main__':
    app.run(debug=True)