from flask import Flask, render_template, request, redirect, url_for, session, json
from db import *
import smtplib

app = Flask(__name__)

@app.route('/home')
def home_page():
    employees = get_calisanlar()
    return render_template("home.html", employees=employees)

@app.route('/add')
def add_page():
    employees = get_calisanlar()
    return render_template("add.html", employees=employees)

@app.route('/hr', methods=['GET', 'POST'])
def hr():
    applicants = model_for_applicants()
    if request.method == 'POST':
        title = request.form['custId']
        name = request.form['custName']
        age = request.form['custAge']
        experience = request.form['custEx']
        sector = request.form['custSec']


        calisan_ekle(name, age, experience, title, sector)
        server = smtplib.SMTP_SSL("smtp.gmail.com", "465")
        server.login("rikudelisv2@gmail.com", "tubitak123.")
        subj_str = "Ise Alim Sureci Hk."
        mail_str = "Merhaba " +str(name)+ ",\n\n Şirketimize başvurduğunuz için teşekkürler. Özgeçmişinizi dikkate değer bulduk ve hem pozisyon hakkında size daha detaylı bilgi vermek, hem de sizi daha yakından tanımak için sizinle ofisimizde bir görüşme yapmak istiyoruz. Uygun olduğunuz tarih ve saati bize mail yoluyla bildirirseniz seviniriz. \n\n Sizinle tanışmak için sabırsızlanıyoruz."
        message = 'Subject: {}\n\n{}'.format(subj_str, mail_str)
        server.sendmail("rikudelisv2@gmail.com", title, message.encode("utf8"))
        basvuran_sil(title)
    return render_template("human_recruitment.html", applicants=applicants)


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        if request.form['login_pass'] == 'password' and request.form['login_id'] == 'secometo':
            print("success")
            return redirect('/home')


    return render_template("login.html")

@app.route('/cal')
def cal():
    events = []
    etkinlikler = get_etkinlikler()
    for i in range(len(etkinlikler)):
        date = str(etkinlikler[i].tarih)

        events.append({'title': etkinlikler[i].ad, 'start': date})
    print(events)
    return render_template("cal.html", events=events)


@app.route('/annual_permit')
def annual_permit():
    permits = []
    izinler = get_izinler()
    for i in range(len(izinler)):
        id = izinler[i].id
        emp = get_calisan(id)
        date = str(izinler[i].izin_baslangic)
        date_2 = str(izinler[i].izin_bitis)
        permits.append({'title': 'Çalışan adı: ' + emp.ad_soyad +',  mail:' +izinler[i].calisan_mail, 'start': date, 'end': date_2})
        print(permits)
    return render_template("annual_permit.html", permits = permits)



@app.route('/add_annual', methods=['GET', 'POST'])
def add_annual():
    employees = get_calisanlar()
    message = ''
    if request.method == 'POST':
        title = request.form['title']
        start = request.form['start']
        end = request.form['end']
        date_time_obj = datetime.strptime(start, '%Y-%m-%d')
        date_time_obj_2 = datetime.strptime(end, '%Y-%m-%d')
        c_id = get_calisan_id(title)
        izin_bool = izin_ekle(c_id, date_time_obj, date_time_obj_2, title)
        print(izin_bool)

        if izin_bool == False:
            message = 'Eski tarihli izin girilemez!'
            print(message)
        else:
            message = 'Ekleme işlemi başarılı '

    return render_template("add_annual.html", employees=employees,  message=message)

@app.route('/add', methods=['GET', 'POST'])
def add():
    server = smtplib.SMTP_SSL("smtp.gmail.com", "465")
    server.login("rikudelisv2@gmail.com", "tubitak123.")
    if request.method == 'POST':
        title = request.form['title']
        start = request.form['start']
        end = request.form['end']
        url = request.form['url']
        select = request.form.getlist('participant')


        date_time_obj = datetime.strptime(start, '%Y-%m-%d')
        employees = get_calisanlar()

        et_bool = etkinlik_ekle(title, date_time_obj)
        if et_bool == False:
            message = 'Eski tarihli izin girilemez!'
            print(message)
        else:
            message = 'Ekleme işlemi başarılı '
            if end == '':
                end = start
                mail_str = "Merhaba,\n\n" + str(start) + " ve " + str(end) + " tarihleri arasindaki " + str(
                    title) + " etkinligine davetlisiniz."
            else:
                mail_str = "Merhaba,\n\n" + str(start) + " tarihindeki " + str(
                    title) + " etkinligine davetlisiniz."

            message = 'Subject: {}\n\n{}'.format(title, mail_str)
            if len(select) != 0:
                for i in select:
                    print(i)
                    server.sendmail("rikudelisv2@gmail.com", i, message.encode("utf8"))

    return render_template("add.html", employees= employees, message=message)


if __name__ == "__main__":
    app.run(debug=True, port=5000)