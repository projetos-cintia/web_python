import sqlite3
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash

DATABASE = "./tmp/flaskr.db"
SECRET_KEY = "teste"
USERNAME = "admin"
PASSWORD = "default"

app = Flask(__name__)
app.config.from_object(__name__)

def criar_bd():
    with closing(conectar_bd()) as bd:
        with app.open_resource('esquema.sql') as sql:
            bd.cursor().executescript(sql.read().decode("utf-8"))
        bd.commit()



def conectar_bd():
    return sqlite3.connect(DATABASE)

criar_bd()

@app.before_request
def pre_requisicao():
    g.bd = conectar_bd()

@app.teardown_request
def encerrar_requisicao(exception):
    g.bd.close()


@app.route('/')
def exibir_entradas():
    sql = "SELECT titulo, texto FROM entradas ORDER BY id DESC"
    cursor = g.bd.execute(sql)
    entradas = [dict(titulo=titulo, texto=texto) for titulo, texto in cursor.fetchall()]

    return render_template('exibir_entradas.html', entradas=entradas)

@app.route('/inserir', methods=['POST'])
def inserir_entradas():
    if not session.get('logado'):
        abort(401)
    sql = "INSERT INTO entradas(titulo, texto) VALUES (?, ?)"
    g.bd.execute(sql, [request.form['titulo'], request.form['texto']])
    g.bd.commit()
    flash("Nova entrada inserida com sucesso")
    return redirect(url_for('exibir_entradas'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == "POST":
        if request.form['username'] != USERNAME or request.form['password'] != PASSWORD:
            erro = "Usuário ou senha inválidos"
        else:
            session['logado'] = True
            flash('Bem vindo!')
            return redirect(url_for('exibir_entradas'))
    return render_template('login.html', erro=erro)

@app.route('/logout')
def logout():
    session['logado'] = False
    flash('Saiu com sucesso!')
    return redirect(url_for('exibir_entradas'))

