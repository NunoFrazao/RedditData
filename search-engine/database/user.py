from database.connection import get_db_connection
def get_user_by_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Executa a query para obter o usuário pelo ID
        query = "SELECT * FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    return user