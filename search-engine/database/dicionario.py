from database.connection import get_db_connection
def get_dicionario_by_user_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Executa a query para obter os dicionários do usuário
        query = "SELECT * FROM dicionario WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        dicionario = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return dicionario