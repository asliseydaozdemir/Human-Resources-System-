import psycopg2
from psycopg2 import sql
import sys
from datetime import datetime, timedelta
from classes.Calisan import *
from classes.Etkinlik import *
from classes.Basvuran import *
from classes.Izin import *
# generate random integer values
from numpy.random import seed
from numpy.random import randint
import pandas
import sklearn
import pickle
from psycopg2 import OperationalError, errorcodes, errors

try:
    connection = psycopg2.connect(user="postgres",
                                  password="202034",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="yazilim_proje_2")
    cursor = connection.cursor()


except (Exception, psycopg2.Error) as error:
    print("Error while fetching data from PostgreSQL", error)


def get_calisanlar():
   query = "select * from calisan"
   cursor.execute(query)
   records = cursor.fetchall()
   calisan_list = []
   for row in records:
      s = Calisan(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
      calisan_list.append(s)

   return calisan_list


def get_etkinlikler():
    query = "select * from etkinlik"
    cursor.execute(query)
    records = cursor.fetchall()
    etkinlik_list = []
    for row in records:
        s = Etkinlik(row[0], row[1], row[2])
        etkinlik_list.append(s)
    print(etkinlik_list)
    return etkinlik_list

def etkinlik_ekle(ad,tarih):
    tarih = tarih.strftime('%Y-%m-%d')
    cursor.execute("select nextval('etkinlik_id_seq')")
    result = str(cursor.fetchone())
    result = result.replace("(", "").replace(",)", "")
    result = int(result)
    try:
        cursor.execute(sql.SQL("INSERT INTO {} VALUES (%s, %s, %s);").format(sql.Identifier('etkinlik')), [result,ad,tarih])
        return True
    except Exception as err:
        print(err)
        return False

    connection.commit()

def get_calisan_id(mailx):
    cursor = connection.cursor()
    cursor.execute("SELECT calisan_id FROM calisan WHERE mail=%(mail)s", {'mail': mailx})
    #cursor.execute(postgreSQL_select_Query, (mailx))
    connection.commit()
    x=cursor.fetchone()
    x=str(x).replace("(","").replace(",)","")
    x=int(x)
    return x

def get_basvuran_id(mailx):
    cursor = connection.cursor()
    cursor.execute("SELECT basvuran_id FROM basvuran WHERE mail=%(mail)s", {'mail': mailx})
    connection.commit()
    x=cursor.fetchone()
    x=str(x).replace("(","").replace(",)","").replace('\'', '')

    print(x)
    x=int(x)

    return x


def izin_ekle(calisan_id, izin_baslangic, izin_bitis, calisan_mail):
    izin_baslangic = izin_baslangic.strftime('%Y-%m-%d')
    izin_bitis = izin_bitis.strftime('%Y-%m-%d')
    cursor.execute("select nextval('izin_id_seq')")
    result = str(cursor.fetchone())
    result = result.replace("(", "").replace(",)", "")
    result = int(result)
    try:
        cursor.execute(sql.SQL("INSERT INTO {} VALUES (%s, %s, %s,%s);").format(sql.Identifier('izin')), [result, izin_baslangic, izin_bitis, calisan_mail])
        return True
    except Exception as err:
        print(err)
        return False
connection.commit()


def get_izinler():
	query="select * from izin"
	cursor.execute(query)
	records=cursor.fetchall()
	izin_list=[]
	for row in records:
		s=Izin(row[0], row[1], row[2], row[3])
		izin_list.append(s)
	return izin_list


def get_calisan(calisan_id):
    query = "select * from calisan where calisan_id::int={c_id}".format(c_id=calisan_id)
    cursor.execute(query)
    calisan = cursor.fetchone()
    return Calisan(calisan[0], calisan[1], calisan[2], calisan[3], calisan[4], calisan[5], calisan[6], calisan[7])



def get_basvurular():
    basvuran_list = []
    query="select * from basvuran"
    cursor.execute(query)
    records=cursor.fetchall()
    basvuran=[]
    for row in records:
        s=Basvuran(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],row[8])
        basvuran_list.append(s)
    return basvuran_list

def model_for_applicants():
    # load the model from disk
    loaded_model = pickle.load(open('models/knn_model.sav', 'rb'))
    # 1 ehb , 2 makine, 3 yazilim, 0 ee
    list_basvuranlar = get_basvurular()
    persons = []
    for i in range(len(list_basvuranlar)):
        persons.append(
            [list_basvuranlar[i].yas, list_basvuranlar[i].deneyim, list_basvuranlar[i].gpa, list_basvuranlar[i].toefl,
             list_basvuranlar[i].sertifika, list_basvuranlar[i].sektor])
    points = 0
    i = 0
    list_persons = []
    for rows in persons:
        if float(rows[2]) >= 3.8:
            points += 20
        elif 3.5 <= float(rows[2]):
            points += 15
        elif 3.0 <= float(rows[2]):
            points += 10
        elif 2.0 < float(rows[2]) <= 2.5:
            points -= 10

        if rows[3] > 95:
            points += 20
        elif 80 < rows[3]:
            points += 15
        elif 70 < rows[3]:
            points += 15
        elif rows[3] > 50:
            points += 5

        if rows[1] > 10:
            points += 10
        elif rows[1] > 5:
            points += 5

        pred = loaded_model.predict([rows[:-1]])

        if pred == 1:
            pred = 'Elektronik ve Haberleşme'
        elif pred == 2:
            pred = 'Makine'
        elif pred == 3:
            pred = 'Yazılım'
        else:
            pred = 'Elektrik Elektronik'

        if rows[-1] == pred:
            points += 50
        rows.insert(0, list_basvuranlar[i].ad_soyad)
        rows.append(list_basvuranlar[i].mail)
        rows.append(points)
        points = 0
        i += 1
        list_persons.append(rows)

    return list_persons

model_for_applicants()
def basvuran_sil(mailx):
    basvuran_id =get_basvuran_id(mailx)
    query = "delete from basvuran where basvuran_id::int={id}".format(id=basvuran_id)
    cursor.execute(query)
    connection.commit()

def calisan_ekle(ad_soyad, yas, deneyim, mail, sektor):
    cursor.execute("select nextval('calisan_id_seq')")
    result = str(cursor.fetchone())
    result = result.replace("(", "").replace(",)", "")
    result = int(result)
    seed(1)
    # generate some integers

    maas = randint(7000, 10000, 1)
    maas = int(maas * int(int(2) / 2))
    x = 20
    cursor.execute(sql.SQL("INSERT INTO {} VALUES (%s, %s, %s,%s,%s,%s,%s, %s);").format(sql.Identifier('calisan')), [
        ad_soyad, yas, maas, deneyim, mail,result, sektor, x
    ])
    connection.commit()