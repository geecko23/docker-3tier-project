from flask import Flask
import redis
import mysql.connector

from db_config import (
    DB_HOST,
    DB_PORT,
    DB_USER,
    DB_PASSWORD,
    DB_NAME
)

app = Flask(__name__)

# Redis connection
redis_client = redis.Redis(
    host="redis",
    port=6379,
    decode_responses=True
)


def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


@app.route("/")
def home():

    # Redis
    visits = redis_client.incr("visits")

    # MySQL
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id, name, role FROM users")
    users = cursor.fetchall()

    cursor.close()
    connection.close()

    user_list = ""

    for user in users:
        user_list += f"<li>{user[1]} - {user[2]}</li>"

    return f"""
    <h1>Docker 3-Tier Application</h1>

    <h2>Redis</h2>
    <p>Page visits: {visits}</p>

    <h2>MySQL Users</h2>
    <ul>
        {user_list}
    </ul>
    """


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
