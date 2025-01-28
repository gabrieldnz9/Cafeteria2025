from flask import Flask, render_template, redirect, url_for # importando a biblioteca flask
from flask_sqlalchemy import SQLAlchemy # importando a biblioteca sqlalchemy
from flask_wtf import FlaskForm # importando a biblioteca flask form
from wtforms import StringField, FileField, FloatField, SelectField, TextAreaField, SubmitField
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif' }


app = Flask(__name__) # criando uma instância da classe flask
app.config['SECRET_KEY'] = 'the end' # configurando a chave
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafeteria.db' # configurando o banco de dados
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app) # criando uma instância da classe SQLALchemy

class Cafeteria(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String(1), nullable=False)
    imagem = db.Column(db.String(250), nullable=False)

class CadastroForm(FlaskForm):
    nome = StringField('Nome')
    preco = FloatField('Preço')
    categoria = SelectField('Categorias', choices=[('1', 'Comidas'), ('2', 'Bebidas')])
    imagem = FileField('Imagem')
    submit = SubmitField('Cadastrar')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro', methods=['GET', 'POST'])  
def cadastro():
    form = CadastroForm()
    if form.validate_on_submit():
        imagem = form.imagem.data
        image_path = f'{app.config["UPLOAD_FOLDER"]}/{secure_filename(imagem.filename)}'
        cafeteria = Cafeteria(nome=form.nome.data,
                               preco=form.preco.data,
                               imagem=image_path,      
                               categoria=form.categoria.data)
        imagem.save(image_path)
        db.session.add(cafeteria)
        db.session.commit()
        return redirect(url_for('cardapio'))
    return render_template('cadastro.html', form=form, cafeteria = None)

@app.route('/listagem', methods=['GET'])
def listagem():
    cafeterias = Cafeteria.query.all()
    return render_template('listagem.html', cafeterias=cafeterias)

@app.route('/editar/<int:id>', methods= ['GET', 'POST'])
def editar(id):
    cafeteria = Cafeteria.query.get(id)
    form = CadastroForm(obj=cafeteria)
    if form.validate_on_submit():
        imagem = form.imagem.data
        image_path = f'{app.config["UPLOAD_FOLDER"]}/{secure_filename(imagem.filename)}'
        cafeteria.nome = form.nome.data
        cafeteria.preco = form.preco.data
        cafeteria.imagem = image_path
        cafeteria.categoria = form.categoria.data
        db.session.commit()
        imagem.save(image_path)
        return redirect(url_for('listagem'))
    return render_template('cadastro.html', form=form, cafeteria=cafeteria)
        
@app.route('/excluir/<int:id>')
def excluir(id):
    cafeteria = Cafeteria.query.get(id)
    db.session.delete(cafeteria)
    db.session.commit()
    return redirect(url_for('listagem'))

@app.route('/cardapio', methods=['GET'])
def cardapio():
    # cafeterias = Cafeteria.query.all()
    # comidas = Cafeteria.filter_by('categoria'==1)
    # bebidas = Cafeteria.filter_by('categoria'==2)
    comidas = db.session.query(Cafeteria).filter_by(categoria='1')
    bebidas = db.session.query(Cafeteria).filter_by(categoria='2')
    return render_template('cardapio.html', comidas=comidas, bebidas=bebidas)

 

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)