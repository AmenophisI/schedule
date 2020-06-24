import os
from  flask import Flask ,render_template,request,redirect,session
from datetime import date , timedelta ,datetime as dt
import sqlite3
import datetime


#flaskの読み込み・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・
app = Flask(__name__)

app.secret_key = "sunabako"

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register" , methods=["GET","post"])
def register():
    #登録ページを表示させる
    if request.method == "GET":
        if "userid" in session :
            return redirect("/login")
        else:
            return render_template("register.html")
    #ここからpostの処理
    else:
        #登録ページで登録ボタンを押した時に走る処理
        username = request.form.get("username")
        pwd = request.form.get("pwd")
        mailadd = request.form.get("mailadd")

        conn = sqlite3.connect("studymanage.db")
        c = conn.cursor()
        c.execute("insert into users values (null,?,?,?,'no_img.png')",(username,pwd,mailadd))
        conn.commit()
        conn.close()
        return redirect("/login")

#GET /Login ➾ログイン画面を表示
#post /login ➾ログイン処理をする
@app.route("/login" , methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if "userid" in session :
            return redirect("/todotop")
        else:
            return render_template("login.html")
    else:
        # ブラウザから送られてきたデータを受け取る
        username = request.form.get("username")
        pwd = request.form.get("pwd")
        #ブラウザから送られてきた name、pwd を usersテーブルに一致するレコードが存在するかを判定する。
        #レコードが存在するとuseridに整数が代入、存在しなければnullが入る
        conn = sqlite3.connect("studymanage.db")
        c = conn.cursor()
        c.execute("select userid from users where username = ? and pwd = ?",(username,pwd))
        userid= c.fetchone()
        conn.close()
        # DBから取得してきたuserid、この時点ではダブル型
        print(type(userid))
        # useridが NULL（pythonではNone）じゃなければログイン成功
    if userid is None:
        #ログイン失敗すると、ログイン画面に戻す
        return render_template("login.html")
    else:
        session["userid"] = userid[0]
        return render_template("todotop.html")

#ユーザートップへのルートを記載
@app.route("/usertop")
def usertop():
    if 'userid' in session :
        return render_template("usertop.html")
        # # DBにアクセスしてログイン
    else:
        return redirect("/login")

@app.route("/log" , methods=["get"])
def log():
    if "userid" in session :
        return render_template("/log.html")
    else:
        return render_template("register.html")

@app.route("/log" , methods=["POST"])
def log_post():
        userid = session['userid']
        logday = date.today()
        log_hyouka = request.form.get("log_hyouka")
        log_txt = request.form.get("log_txt")
        conn = sqlite3.connect("studymanage.db")
        c = conn.cursor()
# 検証テストのために作った内容 以下
        c.execute("select logday,log_hyouka,log_txt,userid from logs where logid = 1")
        selectdata = c.fetchone()
        print (selectdata)
# 以上
        c.execute("insert into logs values (null,?,?,?,?)",(logday,log_hyouka,log_txt,userid))
        conn.commit()
        conn.close()

        return redirect("/log_list")

@app.route('/todotop')
def todo():
    if 'userid' in session :
        today = date.today()
        print(today)
        conn = sqlite3.connect("studymanage.db")
        c = conn.cursor()
        # 今日のデータをスケジュールテーブルの型に無理やり変換させている。
        c.execute("insert into todays values(null,?)",(today,))
        conn.commit()
        c.execute("select today from todays order by today desc limit 1") #直近の入力データを取得
        tday =c.fetchone()
        tday =tday[0]
        print(tday)
        ttday = dt.strptime(tday,"%Y-%m-%d")
        print(ttday)
        #以上（今日のデータをスケジュールテーブルの型に無理やり変換させている。）
        # クッキーからuseridを取得
        userid = session['userid']
        print(userid)
        conn = sqlite3.connect('studymanage.db')
        c = conn.cursor()
        # # DBにアクセスしてログインしているユーザ名にてスケジュール一覧を取得する
        c.execute("select bookname , schedule_start ,schedule_end from schedules join books on schedules.bookid = books.bookid where userid =? and schedule_day =? group by schedules.bookid", (userid,ttday,))

        todo_list = []
        for row in c.fetchall():
            todo_list.append({"bookname": row[0], "schedule_start": row[1] , "schedule_end": row[2]})
        print(todo_list)

        c.execute("select targetid , target from studytargets where userid = ? order by targetid", (userid,))

        target_list = []
        for row in c.fetchall():
            target_list.append({"targetid": row[0], "target": row[1]})
        c.close()
        return render_template('todotop.html' , todo_list = todo_list ,target_list = target_list)
    else:
        return redirect("/login")



@app.route("/log_list")
def log_list_post():
    if 'userid' in session :
        userid = session['userid']
        print(userid)
        conn = sqlite3.connect('studymanage.db')
        c = conn.cursor()
        c.execute("select logid,logday,log_hyouka,log_txt from logs where userid = ? order by logid DESC", (userid,))
        log_list = []
        for row in c.fetchall():
            log_list.append({"logid" : row[0],"logday" : row[1], "log_hyouka" : row[2], "log_txt" : row[3]})
        c.close()
        return render_template("log_list.html" , log_list = log_list)
    else:
        return render_template("login.html")

@app.route('/logedit/<int:logid>' , methods=["GET"])
def logedit(logid):
    if 'userid' in session :
        conn = sqlite3.connect('studymanage.db')
        c = conn.cursor()
        c.execute("select logday from logs where logid = ?", (logid,) )
        logday = c.fetchone()

        c.execute("select log_hyouka from logs where logid = ?", (logid,) )
        log_hyouka =c.fetchone()
        c.execute("select log_txt from logs where logid = ?", (logid,) )
        log_txt =c.fetchone()

        conn.close()
        if logday is not None:
            # None に対しては インデクス指定できないので None 判定した後にインデックスを指定
            logday = logday[0]
            log_hyouka = log_hyouka[0]
            log_txt = log_txt[0]
            # "りんご" ○   ("りんご",) ☓
            # fetchone()で取り出したtupleに 0 を指定することで テキストだけをとりだす
        else:
            return "アイテムがありません" # 指定したIDの name がなければときの対処
        item = { "logid":logid, "logday":logday}
        item_2 = { "logid":logid, "log_hyouka":log_hyouka}
        item_3 = { "logid":logid, "log_txt":log_txt}
        return render_template("logedit.html", logday=item , log_hyouka=item_2 , log_txt = item_3)
    else:
        return redirect("/login")

@app.route("/logedit", methods=["POST"])
def logedit_post():
    # ブラウザから送られてきたデータを取得
    item_id = request.form.get("item_id") # id
    # item_2_id = request.form.get("item_2_id") # id
    # item_3_id = request.form.get("item_3_id") # id

    logday = request.form.get("logday") # 編集されたテキストを取得する
    log_hyouka = request.form.get("log_hyouka")
    log_txt = request.form.get("log_txt")
    # 既にあるデータベースのデータを送られてきたデータに更新
    conn = sqlite3.connect('studymanage.db')
    c = conn.cursor()
    c.execute("update logs set logday = ? , log_hyouka = ? , log_txt = ? where logid = ?",(logday,log_hyouka,log_txt,item_id))
    conn.commit()
    conn.close()

    # アイテム一覧へリダイレクトさせる
    return redirect("/log_list")

@app.route('/logdel' ,methods=["POST"])
def del_log():
    logid = request.form.get("logid")
    conn = sqlite3.connect("studymanage.db")
    c = conn.cursor()
    c.execute("delete from logs where logid = ?", (logid,))
    conn.commit()
    c.close()
    return redirect("/log_list")

@app.route("/targetadd" , methods=["get"])
def studytarget():
    if "userid" in session :
        return render_template("/targetadd.html")
    else:
        return render_template("login.html")

@app.route("/targetadd" , methods=["POST"])
def studytarget_post():
        userid = session['userid']
        target = request.form.get("target")
        kadai_1 = request.form.get("kadai_1")
        kadai_1_gday = request.form.get("kadai_1_gday")
        kadai_2 = request.form.get("kadai_2")
        kadai_2_gday = request.form.get("kadai_2_gday")
        kadai_3 = request.form.get("kadai_3")
        kadai_3_gday = request.form.get("kadai_3_gday")
        kadai_4 = request.form.get("kadai_4")
        kadai_4_gday = request.form.get("kadai_4_gday")
        kadai_5 = request.form.get("kadai_5")
        kadai_5_gday = request.form.get("kadai_5_gday")
        conn = sqlite3.connect("studymanage.db")
        c = conn.cursor()
        c.execute("insert into studytargets values (null,?,?,?,?,?,?,?,?,?,?,?,?)",(target,kadai_1,kadai_1_gday,kadai_2,kadai_2_gday,kadai_3,kadai_3_gday,kadai_4,kadai_4_gday,kadai_5,kadai_5_gday,userid))
        conn.commit()
        conn.close()
        return render_template("/bookadd.html")

@app.route("/bookadd" , methods=["get"])
def bookadd():
    if "userid" in session :
        return render_template("/bookadd.html")
    else:
        return render_template("/login.html")

@app.route("/bookadd" , methods=["POST"])
def bookadd_post():
        userid = session['userid']
        bookname = request.form.get("bookname")
        book_start = request.form.get("book_start")
        book_goal = request.form.get("book_goal")  
        now = date.today()
        book_startday = now
        enddays = request.form.get("enddays")
        delta = timedelta(days =+ int(enddays) )
        book_goalday = now + delta
        conn = sqlite3.connect("studymanage.db")
        c = conn.cursor()
        c.execute("insert into books values (null,?,?,?,?,?,?)",(bookname,book_start,book_goal,book_startday,book_goalday,userid))
        conn.commit()
        conn.close()
        return redirect("/book_keisan")


@app.route("/book_keisan")
def book_keisan_post():
    conn = sqlite3.connect("studymanage.db")
    c = conn.cursor()
# bookaddで入力されたbookidを特定化する
    # 直近の入力データをbookidとして取得
    c.execute("select bookid from books order by bookid desc limit 1")
    bookid_b = c.fetchone()
    bookid_b = bookid_b[0]
    conn.commit()
    print(bookid_b)

    c.execute("select book_startday from books where bookid = ?", (bookid_b,))
    startday = c.fetchone()
    startday = startday[0]
    print(startday)
    conn.commit()

    c.execute("select book_goalday from books where bookid = ?", (bookid_b,))
    goalday = c.fetchone()
    goalday = goalday[0]
    conn.commit()

    c.execute("select book_start from books where bookid = ?", (bookid_b,))
    book_start = c.fetchone()
    book_start = book_start[0]

    c.execute("select book_goal from books where bookid = ?", (bookid_b,))
    book_goal = c.fetchone()
    book_goal = book_goal[0]
    conn.commit()

    #勉強日数計算
    strdt = dt.strptime(startday, "%Y-%m-%d")
    enddt = dt.strptime(goalday, '%Y-%m-%d')
    days_num = (enddt - strdt).days + 1
    print(days_num)

    #全体の勉強ページ数
    book_total = book_goal - book_start  # いったん、のけた+1
    print(book_total)

    #１日あたりの計算の余り
    amari = book_total % days_num

    #１日あたりの計算式
    book_per = (book_total - amari) / days_num
    print(book_per)

# １日毎の開始頁
    TEISUU_BOOK_PER = book_per
    index = 0
    start_list = []
    per_start = book_start
    for i in range(days_num):
        start_list.append(per_start + i * TEISUU_BOOK_PER + index)
        # print(index)
        index += 1
        # print(index)
        if amari == 0:
            index = 0
        if index > amari and amari != 0:
            index -= 1

        print('i:%d' % i)
    # print(i)
    print("開始頁リスト")
    print(start_list)

    # １日毎の終了頁
    TEISUU_BOOK_PER = book_per
    index = 0
    end_list = []
    per_end = book_start
    for i in range(days_num):
        end_list.append(per_end + i * TEISUU_BOOK_PER +
                        TEISUU_BOOK_PER + index)
        # print(index)
        index += 1
        # print(index)
        if amari == 0:
            index = 0
        if index > amari and amari != 0:
            index -= 1
        print('i:%d' % i)
    # print(i)
    print("終了頁リスト")
    print(end_list)

    #日付の計算式を記載
    date_list = []
    for i in range(days_num):
        date_list.append(strdt + timedelta(days=i))

    # （確認用）
    for d in date_list:
        print(d.strftime("%Y-%m-%d"))  # (%A) ==曜日です。

    #データ統合のためのbookIDを指定数（日数）文だけ作る。
    day_list = []
    for i in range(days_num):
        day_list.append(bookid_b)
    print(bookid_b)

    #リストの統合を記載
    result_list = list(zip(date_list, start_list, end_list, day_list))
    print(result_list)  # リザルトは問題なし

    # 統合リストをDBに挿入
    # ※※※bookid=2として仮置き
    insert_sql = "insert into schedules (schedule_id,schedule_day,schedule_start,schedule_end,bookid) values (null,?,?,?,?)"
    c.executemany(insert_sql, result_list)
    conn.commit()

    c.execute(
        "select schedule_day , schedule_start , schedule_end from schedules where bookid = ? ", (bookid_b,))
    bookschedule_list = []
    for row in c.fetchall():
        bookschedule_list.append(
            {"schedule_day": row[0], "schedule_start": row[1], "schedule_end": row[2]})
    c.close()
    return render_template("bookschedule_list.html", bookschedule_list=bookschedule_list)

@app.route('/bookmanage')
def book():
    if 'userid' in session :
        # クッキーからuseridを取得
        userid = session['userid']
        conn = sqlite3.connect('studymanage.db')
        c = conn.cursor()
        # # DBにアクセスしてログインしているユーザ名と投稿内容を取得する
        # クッキーから取得したuseridを使用してusersテーブルのusernameを取得
        c.execute("select username from users where userid = ?", (userid,))
        # fetchoneはタプル型
        user_info = c.fetchone()
        c.execute("select bookid,bookname from books where userid = ? order by bookid", (userid,))
        book_list = []
        for row in c.fetchall():
            book_list.append({"bookid": row[0], "bookname": row[1]})
        c.close()
        return render_template('bookmanage.html' , user_info = user_info , book_list = book_list)
    else:
        return redirect("/login")

@app.route('/bookdel' ,methods=["POST"])
def del_book():
    targetid = request.form.get("bookid")
    conn = sqlite3.connect("studymanage.db")
    c = conn.cursor()
    c.execute("delete from books where bookid = ?", (targetid,))
    conn.commit()
    c.execute("delete from schedules where bookid = ?", (targetid,))
    conn.commit()
    c.close()
    return redirect("/bookmanage")


@app.route('/bookedit/<int:bookid>', methods=["GET"])
def bookedit(bookid):
    if 'userid' in session:
        conn = sqlite3.connect('studymanage.db')
        c = conn.cursor()
        c.execute("select bookname from books where bookid = ?", (bookid,))
        bookname = c.fetchone()

        conn.close()
        if target is not None:
            # None に対しては インデクス指定できないので None 判定した後にインデックスを指定
            bookname = bookname[0]
            # "りんご" ○   ("りんご",) ☓
            # fetchone()で取り出したtupleに 0 を指定することで テキストだけをとりだす
        else:
            return "アイテムがありません"  # 指定したIDの name がなければときの対処
        item = {"bookid": bookid, "bookname": bookname}
        return render_template("bookedit.html", bookname=item, bookid=item)
    else:
        return redirect("/login")


@app.route("/bookedit", methods=["POST"])
def bookedit_post():
    # ブラウザから送られてきたデータを取得
    userid = session['userid']
    bookid = request.form.get("bookid")  # id
    # idが取得されていない➾bookidを取得してくることが必要
    print(bookid)
    bookname = request.form.get("bookname")  # 編集されたテキストを取得する
    book_start = request.form.get("book_start")
    book_goal = request.form.get("book_goal")
    now = date.today()
    book_startday = now
    enddays = request.form.get("enddays")
    delta = timedelta(days=+ int(enddays))
    book_goalday = now + delta
    # 既にあるデータベースのデータを送られてきたデータに更新
    # 一度、テーブル「books、schedules」にあるbookidを全消去。
    #その後、テーブル「books、schedules」に新規登録。
    #1st.全消去
    conn = sqlite3.connect('studymanage.db')
    c = conn.cursor()
    c.execute("delete from books where bookid = ?", (bookid,))
    c.execute("insert into books values (null,?,?,?,?,?,?)", (bookname,
                                                              book_start, book_goal, book_startday, book_goalday, userid))
    # 直近の入力データをbookidとして取得
    c.execute("select bookid from books order by bookid desc limit 1")
    bookid_b = c.fetchone()
    bookid_b = bookid_b[0]
    conn.commit()
    print(bookid_b)

    c.execute("delete from schedules where bookid = ?", (bookid,))
    conn.commit()

    c.execute("select book_startday from books where bookid = ?", (bookid_b,))
    startday = c.fetchone()
    startday = startday[0]
    print(startday)
    conn.commit()

    c.execute("select book_goalday from books where bookid = ?", (bookid_b,))
    goalday = c.fetchone()
    goalday = goalday[0]
    conn.commit()

    c.execute("select book_start from books where bookid = ?", (bookid_b,))
    book_start = c.fetchone()
    book_start = book_start[0]

    c.execute("select book_goal from books where bookid = ?", (bookid_b,))
    book_goal = c.fetchone()
    book_goal = book_goal[0]
    conn.commit()

    #勉強日数計算
    strdt = dt.strptime(startday, "%Y-%m-%d")
    enddt = dt.strptime(goalday, '%Y-%m-%d')
    days_num = (enddt - strdt).days + 1
    print(days_num)

    #全体の勉強ページ数
    book_total = book_goal - book_start
    print(book_total)

    #１日あたりの計算の余り
    amari = book_total % days_num

    #１日あたりの計算式
    book_per = (book_total - amari) / days_num
    # book_per = math.floor(book_per) #整数化はしないこととした。
    print(book_per)

# １日毎の開始頁
    TEISUU_BOOK_PER = book_per
    index = 0
    start_list = []
    per_start = book_start
    for i in range(days_num):
        start_list.append(per_start + i * TEISUU_BOOK_PER + index)
        # print(index)
        index += 1
        # print(index)
        if amari == 0:
            index = 0
        if index > amari and amari != 0:
            index -= 1

        print('i:%d' % i)
    # print(i)
    print("開始頁リスト")
    print(start_list)

    # １日毎の終了頁
    TEISUU_BOOK_PER = book_per
    index = 0
    end_list = []
    per_end = book_start
    for i in range(days_num):
        end_list.append(per_end + i * TEISUU_BOOK_PER +
                        TEISUU_BOOK_PER + index)
        # print(index)
        index += 1
        # print(index)
        if amari == 0:
            index = 0
        if index > amari and amari != 0:
            index -= 1
        print('i:%d' % i)
    # print(i)
    print("終了頁リスト")
    print(end_list)

    #日付の計算式を記載
    date_list = []
    for i in range(days_num):
        date_list.append(strdt + timedelta(days=i))

    # （確認用）
    for d in date_list:
        print(d.strftime("%Y-%m-%d"))  # (%A) ==曜日です。

    #データ統合のためのbookIDを指定数（日数）文だけ作る。
    day_list = []
    for i in range(days_num):
        day_list.append(bookid_b)
    print(bookid_b)

    #リストの統合を記載
    result_list = list(zip(date_list, start_list, end_list, day_list))
    print(result_list)  # リザルトは問題なし

    # 統合リストをDBに挿入
    insert_sql = "insert into schedules (schedule_id,schedule_day,schedule_start,schedule_end,bookid) values (null,?,?,?,?)"
    c.executemany(insert_sql, result_list)
    conn.commit()

    # 今日のデータをスケジュールテーブルの型に無理やり変換させている。
    # c.execute("insert into todays values(null,?)",(now,))
    # conn.commit()
    # c.execute("select today from todays order by today desc limit 1") #直近の入力データを取得
    # tday =c.fetchone()
    # tday =tday[0]
    # print(tday)
    # ttday = dt.strptime(tday,"%Y-%m-%d")
    # print(ttday)
    #     # 以上（今日のデータをスケジュールテーブルの型に無理やり変換させている。）
    # c.execute("select schedule_day , schedule_start , schedule_end from schedules join books on schedules.bookid = books.bookid where userid =? and schedules.bookid = ? group by schedules.bookid", (userid,bookid_b,))
    c.execute(
        "select schedule_day , schedule_start , schedule_end from schedules where bookid = ? ", (bookid_b,))

    bookschedule_list = []
    for row in c.fetchall():
        bookschedule_list.append(
            {"schedule_day": row[0], "schedule_start": row[1], "schedule_end": row[2]})
    c.close()
    return render_template("bookschedule_list.html", bookschedule_list=bookschedule_list)


@app.route("/schedule_list")
def schedule_list():
    if 'userid' in session :
        today = date.today()
        userid = session['userid']
        conn = sqlite3.connect('studymanage.db')
        c = conn.cursor()
        # 今日のデータをスケジュールテーブルの型に無理やり変換させている。
        c.execute("insert into todays values(null,?)",(today,))
        conn.commit()
        c.execute("select today from todays order by today desc limit 1") #直近の入力データを取得
        tday =c.fetchone()
        tday =tday[0]
        print(tday)
        ttday = dt.strptime(tday,"%Y-%m-%d")
        print(ttday)
        # 以上（今日のデータをスケジュールテーブルの型に無理やり変換させている。）        

        c.execute("select bookname , schedule_day , schedule_start ,schedule_end from schedules join books on schedules.bookid = books.bookid where userid =? and schedule_day >=? order by schedule_day asc", (userid,ttday))

        schedule_list = []
        for row in c.fetchall():
            schedule_list.append({"bookname" : row[0],"schedule_day" : row[1],"schedule_start" : row[2], "schedule_end" : row[3]})
        c.close()
        print(schedule_list)        
        return render_template("schedule_list.html" , schedule_list = schedule_list)
    else:
        return render_template("login.html")
#以下、編集中です。・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・

# @app.route('/kari_bookresultedit/<int:userid>' , methods=["GET"])
# def kari_bookresultedit(userid):
#     if 'userid' in session :
#         # 今日のデータをスケジュールテーブルの型に無理やり変換させている。
#         today = date.today()
#         conn = sqlite3.connect('studymanage.db')
#         c = conn.cursor()
#         c.execute("insert into todays values(null,?)",(today,))
#         conn.commit()
#         c.execute("select today from todays order by today desc limit 1") #直近の入力データを取得
#         tday =c.fetchone()
#         tday =tday[0]
#         print(tday)
#         ttday = dt.strptime(tday,"%Y-%m-%d")
#         print(ttday)
#         #以上（今日のデータをスケジュールテーブルの型に無理やり変換させている。）
#         c.execute("select books.bookid , bookname , schedule_start ,schedule_end , book_start , book_goal , book_startday , book_goalday  from schedules join books on schedules.bookid = books.bookid where userid =? and schedule_day =? group by schedules.bookid", (userid,ttday,))

#         todo_list = []
#         for row in c.fetchall():
#             todo_list.append({"books.bookid" : row[0], "bookname": row[1], "schedule_start": row[2] , "schedule_end": row[3] , "book_start":row[4] , "book_goal":row[5] , "book_startday":row[6] , "book_goalday":row[7] })
#         print(todo_list)
#         c.close()

#         return render_template("kari_bookresultedit.html", todo_list = todo_list)
#     else:
#         return redirect("/login")

# # 以下、リスト化をあきらめた。・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・
# @app.route("/kari_bookresultedit", methods=["POST"])
# def kari_bookresultedit():
#     # ブラウザから送られてきたデータを取得
#     item_id = request.form.get("item_id") # id
#     # item_2_id = request.form.get("item_2_id") # id
#     # item_3_id = request.form.get("item_3_id") # id

#     bookname = request.form.get("bookname") # 編集されたテキストを取得する
#     book_start = request.form.get("book_start")
#     log_txt = request.form.get("log_txt")
#     # 既にあるデータベースのデータを送られてきたデータに更新
#     conn = sqlite3.connect('studymanage.db')
#     c = conn.cursor()
#     c.execute("update logs set logday = ? , log_hyouka = ? , log_txt = ? where logid = ?",(logday,log_hyouka,log_txt,item_id))
#     conn.commit()
#     conn.close()

#     # アイテム一覧へリダイレクトさせる
#     return redirect("/log_list")
# 以下、リスト化をあきらめた。・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・


# 以上・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・    
@app.route('/useredit/<int:userid>' , methods=["GET"])
def useredit(userid):
    if 'userid' in session :
        conn = sqlite3.connect('studymanage.db')
        c = conn.cursor()
        c.execute("select userid from users where userid = ?", (userid,) )
        userid = c.fetchone()
        userid = userid[0]
        print(userid)

        c.execute("select username from users where userid = ?", (userid,) )
        username = c.fetchone()
        print(username)

        c.execute("select pwd from users where userid = ?", (userid,) )
        pwd = c.fetchone()
        print(pwd)

        c.execute("select mailadd from users where userid = ?", (userid,) )
        mailadd = c.fetchone()
        print(mailadd)

        conn.close()
            # None に対しては インデクス指定できないので None 判定した後にインデックスを指定
        username = username[0]
        print(username)
        pwd = pwd[0]
        print(pwd)
        mailadd = mailadd[0]
        print(mailadd)
        # "りんご" ○   ("りんご",) ☓
        # fetchone()で取り出したtupleに 0 を指定することで テキストだけをとりだす
        item = { "userid":userid, "username":username}
        item_2 = { "userid":userid, "pwd":pwd}
        item_3 = { "userid":userid, "mailadd":mailadd}
        return render_template("useredit.html", username=item , pwd=item_2 , mailadd = item_3)    
    else:
        return redirect("/login")

@app.route("/useredit", methods=["POST"])
def useredit_post():
    # ブラウザから送られてきたデータを取得
    item_id = request.form.get("item_id") # id
    # item_2_id = request.form.get("item_2_id") # id
    # item_3_id = request.form.get("item_3_id") # id

    username = request.form.get("username") # 編集されたテキストを取得する
    print(username)
    pwd = request.form.get("pwd")
    print(pwd)
    mailadd = request.form.get("mailadd")
    print(mailadd)
    # 既にあるデータベースのデータを送られてきたデータに更新
    conn = sqlite3.connect('studymanage.db')
    c = conn.cursor()
    c.execute("update users set username = ? , pwd = ? , mailadd = ? where userid = ?",(username,pwd,mailadd,item_id))
    conn.commit()
    conn.close()

    # アイテム一覧へリダイレクトさせる
    return redirect("/login")

@app.route("/userinfo")
def userinfo():
    if 'userid' in session :
        userid = session['userid']
        conn = sqlite3.connect('studymanage.db')
        c = conn.cursor()       
        c.execute("select userid from users where userid = ?", (userid,) )
        item_id = c.fetchone()

        c.execute("select username from users where userid = ?", (userid,) )
        username = c.fetchone()
        
        c.execute("select pwd from users where userid = ?", (userid,) )
        pwd = c.fetchone()
        
        c.execute("select mailadd from users where userid = ?", (userid,) )
        mailadd = c.fetchone()
        c.close()
        
        item_id = item_id[0]
        username = username[0]
        pwd = pwd[0]
        mailadd = mailadd[0]
        # "りんご" ○   ("りんご",) ☓
        # fetchone()で取り出したtupleに 0 を指定することで テキストだけをとりだす

        return render_template("userinfo.html", userid=item_id , username=username , pwd = pwd, mailadd = mailadd) 

    else:
        return render_template("login.html")

@app.route('/targettop')
def target():
    if 'userid' in session :
        # クッキーからuseridを取得
        userid = session['userid']
        conn = sqlite3.connect('studymanage.db')
        c = conn.cursor()
        # # DBにアクセスしてログインしているユーザ名と投稿内容を取得する
        # クッキーから取得したuseridを使用してusersテーブルのusernameを取得
        # c.execute("select username from users where userid = ?", (userid,))
        # fetchoneはタプル型
        # user_info = c.fetchone()
        c.execute("select targetid,target ,kadai_1,kadai_1_gday,kadai_2,kadai_2_gday,kadai_3,kadai_3_gday,kadai_4,kadai_4_gday,kadai_5,kadai_5_gday from studytargets where userid = ? order by targetid", (userid,))

        target_list = []
        for row in c.fetchall():
            target_list.append({"targetid": row[0], "target": row[1] , "kadai_1": row[2], "kadai_1_gday": row[3], "kadai_2": row[4], "kadai_2_gday": row[5], "kadai_3": row[6], "kadai_3_gday": row[7], "kadai_4": row[8], "kadai_4_gday": row[9], "kadai_5": row[10], "kadai_5_gday": row[11]})

        c.close()
        return render_template('targettop.html' , target_list = target_list)
    else:
        return redirect("/login")

@app.route('/targetedit/<int:targetid>' , methods=["GET"])
def targetedit(targetid):
    if 'userid' in session :
        conn = sqlite3.connect('studymanage.db')
        c = conn.cursor()
        c.execute("select target from studytargets where targetid = ?", (targetid,) )
        target = c.fetchone()

        c.execute("select kadai_1_gday from studytargets where targetid = ?", (targetid,) )
        kadai_1_gday =c.fetchone()
        c.execute("select kadai_1 from studytargets where targetid = ?", (targetid,) )
        kadai_1 =c.fetchone()

        c.execute("select kadai_2_gday from studytargets where targetid = ?", (targetid,) )       
        kadai_2_gday =c.fetchone()
        c.execute("select kadai_2 from studytargets where targetid = ?", (targetid,) )
        kadai_2 =c.fetchone()

        c.execute("select kadai_3_gday from studytargets where targetid = ?", (targetid,) )       
        kadai_3_gday =c.fetchone()
        c.execute("select kadai_3 from studytargets where targetid = ?", (targetid,) )
        kadai_3 =c.fetchone()

        c.execute("select kadai_4_gday from studytargets where targetid = ?", (targetid,) )       
        kadai_4_gday =c.fetchone()
        c.execute("select kadai_4 from studytargets where targetid = ?", (targetid,) )
        kadai_4 =c.fetchone()

        c.execute("select kadai_5_gday from studytargets where targetid = ?", (targetid,) )       
        kadai_5_gday =c.fetchone()
        c.execute("select kadai_5 from studytargets where targetid = ?", (targetid,) )
        kadai_5 =c.fetchone()

        conn.close()
        if target is not None:
            # None に対しては インデクス指定できないので None 判定した後にインデックスを指定
            target = target[0]
            kadai_1_gday = kadai_1_gday[0]
            kadai_1 = kadai_1[0]
            kadai_2_gday = kadai_2_gday[0]
            kadai_2 = kadai_2[0]
            kadai_3_gday = kadai_3_gday[0]
            kadai_3 = kadai_3[0]
            kadai_4_gday = kadai_4_gday[0]
            kadai_4 = kadai_4[0]
            kadai_5_gday = kadai_5_gday[0]
            kadai_5 = kadai_5[0]
            # "りんご" ○   ("りんご",) ☓
            # fetchone()で取り出したtupleに 0 を指定することで テキストだけをとりだす
        else:
            return "アイテムがありません" # 指定したIDの name がなければときの対処
        item = { "targetid":targetid, "target":target}
        item_2 = { "targetid":targetid, "kadai_1_gday":kadai_1_gday}
        item_3 = { "targetid":targetid, "kadai_1":kadai_1}
        item_4 = { "targetid":targetid, "kadai_2_gday":kadai_2_gday}
        item_5 = { "targetid":targetid, "kadai_2":kadai_2}
        item_6 = { "targetid":targetid, "kadai_3_gday":kadai_3_gday}
        item_7 = { "targetid":targetid, "kadai_3":kadai_3}
        item_8 = { "targetid":targetid, "kadai_4_gday":kadai_4_gday}
        item_9 = { "targetid":targetid, "kadai_4":kadai_4}
        item_10 = { "targetid":targetid, "kadai_5_gday":kadai_5_gday}
        item_11 = { "targetid":targetid, "kadai_5":kadai_5}
        return render_template("targetedit.html", target=item , kadai_1_gday=item_2 , kadai_1 = item_3, kadai_2_gday=item_4 , kadai_2 = item_5, kadai_3_gday=item_6 , kadai_3 = item_7, kadai_4_gday=item_8 , kadai_4 = item_9, kadai_5_gday=item_10 , kadai_5 = item_11)
    else:
        return redirect("/login")

@app.route("/targetedit", methods=["POST"])
def targetedit_post():
    # ブラウザから送られてきたデータを取得
    item_id = request.form.get("item_id") # id
    # item_2_id = request.form.get("item_2_id") # id
    # item_3_id = request.form.get("item_3_id") # id
    # item_4_id = request.form.get("item_4_id") # id
    # item_5_id = request.form.get("item_5_id") # id
    # item_6_id = request.form.get("item_6_id") # id
    # item_7_id = request.form.get("item_7_id") # id

    target = request.form.get("target") # 編集されたテキストを取得する
    kadai_1_gday = request.form.get("kadai_1_gday")
    kadai_1 = request.form.get("kadai_1")
    kadai_2_gday = request.form.get("kadai_2_gday")
    kadai_2 = request.form.get("kadai_2")
    kadai_3_gday = request.form.get("kadai_3_gday")
    kadai_3 = request.form.get("kadai_3")
    kadai_4_gday = request.form.get("kadai_4_gday")
    kadai_4 = request.form.get("kadai_4")
    kadai_5_gday = request.form.get("kadai_5_gday")
    kadai_5 = request.form.get("kadai_5")
    # 既にあるデータベースのデータを送られてきたデータに更新
    conn = sqlite3.connect('studymanage.db')
    c = conn.cursor()
    c.execute("update studytargets set target = ? , kadai_1 = ? , kadai_1_gday = ? ,kadai_2 = ? ,kadai_2_gday = ?  ,kadai_3 = ? ,kadai_3_gday = ?,kadai_4 = ? ,kadai_4_gday = ?  ,kadai_5 = ? ,kadai_5_gday = ? where targetid = ?",(target,kadai_1,kadai_1_gday,kadai_2,kadai_2_gday,kadai_3,kadai_3_gday,kadai_4,kadai_4_gday,kadai_5,kadai_5_gday,item_id))
    conn.commit()
    c.close()

    # アイテム一覧へリダイレクトさせる
    return render_template("/targettop.html")

@app.route('/targetdel' ,methods=["POST"])
def del_target():
    targetid = request.form.get("targetid")
    conn = sqlite3.connect("studymanage.db")
    c = conn.cursor()
    c.execute("delete from studytargets where targetid = ?", (targetid,))
    conn.commit()
    c.close()
    return redirect("/targettop")
#以下、編集中です。・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・
# strdt = dt.strptime("2018-02-04" , "%Y-%m-%d")
# enddt = dt.strptime("2018-03-5",'%Y-%m-%d')

# 以上・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・    
#以下、未完成です。・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・

#404エラーメッセージ・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・    
@app.errorhandler(404)
def notfound(code):
    return "何にもないＨＰですよ"
#おまじない・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・
if __name__=="__main__":
    app.run(debug=True)

    # 作業環境のテストを以下に記載。
#@app.route('/')
#def hello():
#    return "卒業課題に向けて考察中"

#@app.route('/top')
#def top():
#    return "卒業課題のトップだよ"

#@app.route('/user/<name>')
#def user(name):
#    return "私の名前は" + name + "です"

#@app.route("/temptest")
#def temptest():
#    user_name =  "テスト"
#    name = "スナバコ"
#    age = 27
#    address = "香川県"
#    return render_template('index.html',user_name = user_name , name = name , age = age , address = address) 

#@app.route("/dbtest")
#def dbtest():
#    conn = sqlite3.connect("studymanage.db")
#    c = conn.cursor()
#    c.execute("select username,mailadd from users")
#    user_info = c.fetchall()
#    c.close()
#
#    print(user_info)
#
#    return render_template("dbtest.html",user_info = user_info)
