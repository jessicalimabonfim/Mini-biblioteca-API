from flask import Flask, jsonify, request, abort
from flasgger import Swagger
from peewee import *

app = Flask(__name__)
swagger = Swagger(app)

# Banco SQLite local (arquivo livros.db)
db = SqliteDatabase("livros.db")


class BaseModel(Model):
    class Meta:
        database = db


class Livro(BaseModel):
    id = AutoField()
    titulo = CharField()
    autor = CharField()
    ano = IntegerField()
    disponivel = BooleanField(default=True)
    


# ------------------------------
# Ciclo de conexão por requisição
# ------------------------------
@app.before_request
def _db_connect():
    if db.is_closed():
        db.connect(reuse_if_open=True)


@app.teardown_request
def _db_close(exc):
    if not db.is_closed():
        db.close()


# ------------------------------
# Criação da tabela e dados iniciais
# ------------------------------
def init_db():
    db.connect(reuse_if_open=True)
    db.create_tables([Livro], safe=True)
    if Livro.select().count() == 0:
        Livro.create(titulo="Estruturas de Dados", autor="N. Wirth", ano=1976, disponivel=True)
        Livro.create(titulo="Clean Code", autor="R. Martin", ano=2008, disponivel=True)
    db.close()

init_db()

# Rotas da aplicação

@app.get("/api/livros")
def listar_livros():
    """
    Lista todos os livros 
    ---
    responses:
      200:
        description: Lista de livros
        examples:
          application/json: 
            - id: 1
              titulo: "Estruturas de Dados"
              autor: "N. Wirth"
              ano: 1976
              disponivel: true 
    """
    livros = Livro.select()

    lst = []
    for livro in livros:
        item = {}
        item['titulo'] = livro.titulo
        item['autor'] = livro.autor
        item['ano'] = livro.ano
        item['id'] = livro.id
        item['disponivel'] = livro.disponivel
        lst.append(item)
    
    return jsonify(lst)

@app.get("/api/livros/<int:lid>")
def obter_livro(lid):
    """
    Obtém os detalhes de um livro específico pelo ID
    ---
    parameters:
      - name: lid
        in: path
        type: integer
        required: true
        description: ID do livro
    responses:
      200:
        description: Livro encontrado
      404:
        description: Livro não encontrado
    """
    livro = Livro.select().where(Livro.id == lid)

    item = {}
    item['titulo'] = livro[0].titulo
    item['autor'] = livro[0].autor
    item['ano'] = livro[0].ano

    return jsonify(item)

@app.post("/api/livros")
def criar_livro():
    """
    Cria um novo livro
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - titulo
            - autor
            - ano
          properties:
            titulo:
              type: string
            autor:
              type: string
            ano:
              type: integer
            disponivel:
              type: boolean
    responses:
      201:
        description: Livro criado com sucesso
      400:
        description: Dados inválidos ou campos obrigatórios ausentes
    """
    data = request.get_json(force=True) or {}
    obrig = ["titulo", "autor", "ano"]
    if not all(k in data for k in obrig):
        abort(400, description="Campos obrigatórios: titulo, autor, ano")
    
    Livro.create(
        titulo = str(data["titulo"]).strip(),
        autor = str(data["autor"]).strip(),
        ano = int(data["ano"])
    )
    
    return "Livro adicionado com sucesso"

@app.delete("/api/livros/<int:lid>")
def remover_livro(lid):
    """
    Remove um livro pelo ID
    ---
    parameters:
      - name: lid
        in: path
        type: integer
        required: true
        description: ID do livro
    responses:
      204:
        description: Livro removido com sucesso
      404:
        description: Livro não encontrado
    """
    Livro.delete().where(Livro.id == lid).execute()
    return "Livro removido com sucesso!"

@app.patch("/api/livros/<int:lid>/disponibilidade")
def atualizar_disponibilidade(lid):
    """
    Atualiza a disponibilidade de um livro
    ---
    parameters:
      - name: lid
        in: path
        type: integer
        required: true
        description: ID do livro
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - disponivel
          properties:
            disponivel:
              type: boolean
    responses:
      200:
        description: Disponibilidade atualizada
      404:
        description: Livro não encontrado
    """
    data = request.get_json(force=True) or {}
    Livro.update(disponivel = data['disponivel']).where(Livro.id == lid).execute()
    return "Livro atualizado com sucesso"

@app.get("/api/livros/disponiveis")
def listar_livros_disponiveis():
    """
    Lista todos os livros disponíveis
    ---
    responses:
      200:
        description: Lista de livros
        examples:
          application/json: 
            - id: 1
              titulo: "Estruturas de Dados"
              autor: "N. Wirth"
              ano: 1976
              disponivel: true
    """
    livros = Livro.select().where(Livro.disponivel == True)

    lst = []
    for livro in livros:
        item = {}
        item['titulo'] = livro.titulo
        item['autor'] = livro.autor
        item['ano'] = livro.ano
        item['id'] = livro.id
        item['disponivel'] = livro.disponivel
        lst.append(item)

@app.patch("/api/livros/<int:lid>/editar")
def editar(lid):
    """
    Atualiza qualquer campo
    ---
    parameters:
      - name: lid
        in: path
        type: integer
        required: true
        description: ID do livro a ser atualizado
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - disponivel
            - titulo
            - autor
            - ano
          properties:
            titulo:
              type: string
              example: "Codigo Limpo"
            autor:
              type: string
              example: "Robert Martin"
            ano:
              type: integer
              example: 2008
            disponivel:
              type: boolean
              example: True  
    responses:
      200:
        description: Disponibilidade atualizada
      404:
        description: Livro não encontrado
    """
    data = request.get_json(force=True) or {}
    Livro.update(
      disponivel = data['disponivel'],
      autor = data['autor'],
      titulo = data['titulo'],
      ano = data['ano']
      ).where(Livro.id == lid).execute()
    return "Livro editado com sucesso"
    
    return jsonify(lst)    

if __name__ == "__main__":
    app.run(debug=True)