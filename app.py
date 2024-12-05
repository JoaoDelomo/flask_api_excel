from flask import Flask, send_file, jsonify
from psycopg2 import connect, sql
from psycopg2.extras import RealDictCursor
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import NameObject, TextStringObject
import os

app = Flask(__name__)

# Configurações do banco de dados
DATABASE_CONFIG = {
    "dbname": "postgres",
    "user": "postgres.dulfptftanpgjzmzcvut",
    "password": "bzV12L6t2j6xfYHp",
    "host": "aws-0-sa-east-1.pooler.supabase.com",
    "port": "6543"
}

# Função para preencher o PDF (somente página 3)
def preencher_pdf_pagina3(arquivo_entrada, arquivo_saida, dados_pag3):
    reader = PdfReader(arquivo_entrada)
    writer = PdfWriter()

    # Copiar todas as páginas do PDF
    for page in reader.pages:
        writer.add_page(page)

    # Ajustar o tamanho do texto no campo
    def ajustar_tamanho_fonte(campo, tamanho=6):
        campo.update({
            NameObject("/DA"): TextStringObject(f"/Helv {tamanho} Tf 0 g")
        })

    # Preencher somente a página 3
    page = writer.pages[2]  # Índice da página 3 (começa do 0)
    if "/Annots" in page:
        for annot in page["/Annots"]:
            campo = annot.get_object()
            nome_campo = campo.get("/T")
            if nome_campo and nome_campo in dados_pag3:
                campo.update({
                    NameObject("/V"): TextStringObject(dados_pag3[nome_campo])
                })
                ajustar_tamanho_fonte(campo)

    # Escrever o PDF preenchido
    with open(arquivo_saida, "wb") as output_pdf:
        writer.write(output_pdf)

# Função para buscar dados do banco
def buscar_dados_attendant(id):
    try:
        conn = connect(**DATABASE_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(sql.SQL("SELECT * FROM attendant WHERE id = %s"), (id,))
        dados = cursor.fetchone()
        conn.close()
        return dados
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")
        return None

# Rota para gerar o PDF apenas com os dados do `attendant`
@app.route('/generate_attendant_pdf/<int:id>', methods=['GET'])
def generate_attendant_pdf(id):
    """
    Rota para gerar o PDF da ficha de inscrição (página 3) com os dados do `attendant`.
    """
    # Buscar dados do banco
    dados = buscar_dados_attendant(id)
    if not dados:
        return jsonify({"error": "Dados não encontrados para o ID fornecido."}), 404

    # Mapeamento de dados para os campos da página 3
    dados_pag3 = {
        "Text28": dados.get("name", ""),
        "Text93": "Feminino" if dados.get("gender") == "female" else "Masculino" if dados.get("gender") == "male" else "",
        "Text29": dados.get("date_of_subscription", ""),
        "Text30": dados.get("date_of_registration", ""),
        "Text31": dados.get("nis_number", ""),
        "Text32": dados.get("date_of_shutdown", ""),
        "Text7": dados.get("dismissal", ""),
        "Text8": dados.get("naturalness", ""),
        "Text9": dados.get("color", ""),
        "Text10": "Sim" if dados.get("person_with_disabilities") else "Não",
        "Text11": dados.get("cpf", ""),
        "Text12": dados.get("rg", ""),
        "Text25": dados.get("rg_emission", ""),
        "Text27": dados.get("rg_issuer", ""),
        "Text34": dados.get("rg_state", ""),
        "Text39": dados.get("birth_certificate_number", ""),
        "Text40": dados.get("birth_certificate_page", ""),
        "Text41": dados.get("birth_certificate_book", ""),
        "Text42": dados.get("school_name", ""),
        "Text43": dados.get("school_series", ""),
        "Text44": dados.get("school_schedule", ""),
        "Text45": dados.get("mother_name", ""),
        "Text46": dados.get("father_name", ""),
        "Text47": dados.get("guardian_name", ""),
        "Text48": dados.get("guardian_relationship", ""),
        "Text49": dados.get("guardian_marital_status", ""),
        "Text50": dados.get("guardian_education_level", ""),
        "Text51": dados.get("guardian_profession", ""),
        "Text52": dados.get("guardian_occupation", ""),
        "Text53": dados.get("guardian_condition", ""),
        "Text54": dados.get("guardian_income", ""),
        "Text55": dados.get("address", ""),
        "Text56": dados.get("address_number", ""),
        "Text57": dados.get("address_complement", ""),
        "Text58": dados.get("address_zip", ""),
        "Text59": dados.get("address_neighborhood", ""),
        "Text60": dados.get("address_district", ""),
        "Text61": dados.get("home_phone", ""),
        "Text62": dados.get("cell_phone", ""),
        "Text63": dados.get("other_phone", ""),
        "Text64": dados.get("reference_point", ""),
        "Text65": dados.get("housing_conditions", ""),
        "Text66": dados.get("room_count", ""),
        "Text67": dados.get("rent_or_financing_value", ""),
        "Text68": dados.get("construction_type", ""),
        "Text69": dados.get("housing_status", ""),
        "Text70": "Sim" if dados.get("income_transfer_program") else "Não",
        "Text71": "Sim" if dados.get("continuous_cash_benefit") else "Não",
    }

    # Gerar o PDF
    arquivo_entrada = "./pdfs/modelo_sem_links_corrigido.pdf"
    arquivo_saida = f"./pdfs/attendant_{id}_pag3.pdf"
    if not os.path.exists("./pdfs"):
        os.makedirs("./pdfs")

    preencher_pdf_pagina3(arquivo_entrada, arquivo_saida, dados_pag3)

    # Retornar o arquivo gerado
    return send_file(
        arquivo_saida,
        as_attachment=True,
        mimetype="application/pdf"
    )

# Rota de teste
@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "API está funcionando!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
