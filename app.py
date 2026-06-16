from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "universo_games_chave_2025"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ── MODELOS ──────────────────────────────────────────────
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(120), nullable=False)
    compras = db.relationship('Compra', backref='usuario', lazy=True)

class Compra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    produto_id = db.Column(db.String(50), nullable=False)
    produto_nome = db.Column(db.String(200), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    link_drive = db.Column(db.String(500), nullable=False)

# ── CATÁLOGO DE PRODUTOS ──────────────────────────────────
PRODUTOS = [
    {
        "id": "ps2",
        "console": "PlayStation 2",
        "tag": "PS2",
        "descricao": "Coleção completa com os melhores títulos em formato ISO. Compatível com OPL e FreeMCBoot.",
        "itens": "200+ jogos",
        "formato": ".ISO",
        "preco": 9.00,
        "cor": "#003087",
        "link_drive": "https://drive.google.com/SEU_LINK_PS2_AQUI"
    },
    {
        "id": "ps3",
        "console": "PlayStation 3",
        "tag": "PS3",
        "descricao": "Arquivos PKG prontos para instalar via Hen/CFW. Inclui jogos PSN e de disco.",
        "itens": "150+ jogos",
        "formato": ".PKG",
        "preco": 15.00,
        "cor": "#1a1a2e",
        "link_drive": "https://drive.google.com/SEU_LINK_PS3_AQUI"
    },
    {
        "id": "psp",
        "console": "PlayStation Portable",
        "tag": "PSP",
        "descricao": "Pack em CSO e ISO compactados, compatíveis com PPSSPP e PSP modificado.",
        "itens": "180+ jogos",
        "formato": ".CSO / .ISO",
        "preco": 8.00,
        "cor": "#2d2d2d",
        "link_drive": "https://drive.google.com/SEU_LINK_PSP_AQUI"
    },
    {
        "id": "xbox360",
        "console": "Xbox 360",
        "tag": "X360",
        "descricao": "Pastas no formato default.xex para rodar via RGH/JTAG ou emulador Xenia.",
        "itens": "120+ jogos",
        "formato": "default.xex",
        "preco": 12.00,
        "cor": "#107c10",
        "link_drive": "https://drive.google.com/SEU_LINK_XBOX360_AQUI"
    },
    {
        "id": "wii",
        "console": "Nintendo Wii",
        "tag": "WII",
        "descricao": "Jogos em WBFS e ISO para usar com USB Loader GX ou Dolphin Emulator.",
        "itens": "130+ jogos",
        "formato": ".WBFS / .ISO",
        "preco": 10.00,
        "cor": "#c0c0c0",
        "link_drive": "https://drive.google.com/SEU_LINK_WII_AQUI"
    },
    {
        "id": "wiiu",
        "console": "Nintendo Wii U",
        "tag": "WII U",
        "descricao": "Títulos em formato WUD e WUX, compatíveis com Cemu e console desbloqueado.",
        "itens": "80+ jogos",
        "formato": ".WUD / .WUX",
        "preco": 18.00,
        "cor": "#009ac7",
        "link_drive": "https://drive.google.com/SEU_LINK_WIIU_AQUI"
    },
    {
        "id": "gamecube",
        "console": "Nintendo GameCube",
        "tag": "GCN",
        "descricao": "ISOs para Dolphin Emulator ou console com SD Card e Swiss.",
        "itens": "90+ jogos",
        "formato": ".ISO / .GCZ",
        "preco": 10.00,
        "cor": "#6a0dad",
        "link_drive": "https://drive.google.com/SEU_LINK_GAMECUBE_AQUI"
    },
    {
        "id": "nds",
        "console": "Nintendo DS",
        "tag": "NDS",
        "descricao": "ROMs NDS para jogar no DeSmuME, melonDS ou cartuchos R4.",
        "itens": "250+ jogos",
        "formato": ".NDS",
        "preco": 7.00,
        "cor": "#cc0000",
        "link_drive": "https://drive.google.com/SEU_LINK_NDS_AQUI"
    },
]

def get_produto(pid):
    return next((p for p in PRODUTOS if p['id'] == pid), None)

def usuario_logado():
    return 'usuario_id' in session

# ── ROTAS ─────────────────────────────────────────────────
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        acao = request.form.get('acao')

        if acao == 'cadastro':
            nome  = request.form.get('nome', '').strip()
            email = request.form.get('email', '').strip().lower()
            senha = request.form.get('senha', '')
            if Usuario.query.filter_by(email=email).first():
                flash('E-mail já cadastrado. Faça login.', 'erro')
            else:
                u = Usuario(nome=nome, email=email, senha=senha)
                db.session.add(u)
                db.session.commit()
                session['usuario_id'] = u.id
                session['nome'] = u.nome
                return redirect(url_for('loja'))

        elif acao == 'login':
            email = request.form.get('email', '').strip().lower()
            senha = request.form.get('senha', '')
            u = Usuario.query.filter_by(email=email, senha=senha).first()
            if u:
                session['usuario_id'] = u.id
                session['nome'] = u.nome
                return redirect(url_for('loja'))
            else:
                flash('E-mail ou senha incorretos.', 'erro')

    return render_template('index.html', logado=usuario_logado())

@app.route('/loja')
def loja():
    if not usuario_logado():
        return redirect(url_for('index'))
    return render_template('loja.html', produtos=PRODUTOS, logado=True)

@app.route('/checkout/<produto_id>', methods=['GET', 'POST'])
def checkout(produto_id):
    if not usuario_logado():
        return redirect(url_for('index'))
    produto = get_produto(produto_id)
    if not produto:
        return redirect(url_for('loja'))

    if request.method == 'POST':
        total = produto['preco'] + 0.99
        compra = Compra(
            usuario_id=session['usuario_id'],
            produto_id=produto['id'],
            produto_nome=produto['console'],
            valor=total,
            link_drive=produto['link_drive']
        )
        db.session.add(compra)
        db.session.commit()
        return redirect(url_for('confirmacao', compra_id=compra.id))

    return render_template('checkout.html', produto=produto, logado=True)

@app.route('/confirmacao/<int:compra_id>')
def confirmacao(compra_id):
    if not usuario_logado():
        return redirect(url_for('index'))
    compra = Compra.query.get_or_404(compra_id)
    if compra.usuario_id != session['usuario_id']:
        return redirect(url_for('loja'))
    produto = get_produto(compra.produto_id)
    return render_template('confirmacao.html', compra=compra, produto=produto, logado=True)

@app.route('/area-cliente')
def area_cliente():
    if not usuario_logado():
        return redirect(url_for('index'))
    u = Usuario.query.get(session['usuario_id'])
    compras = Compra.query.filter_by(usuario_id=u.id).order_by(Compra.data.desc()).all()
    compras_com_produto = [(c, get_produto(c.produto_id)) for c in compras]
    return render_template('area_cliente.html', usuario=u, compras=compras_com_produto, logado=True)

@app.route('/sobre')
def sobre():
    return render_template('sobre.html', logado=usuario_logado())

@app.route('/contato', methods=['GET', 'POST'])
def contato():
    enviado = False
    if request.method == 'POST':
        enviado = True
    return render_template('contato.html', enviado=enviado, logado=usuario_logado())

@app.route('/sair')
def sair():
    session.clear()
    return redirect(url_for('index'))

# ── INICIALIZAÇÃO ─────────────────────────────────────────
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)