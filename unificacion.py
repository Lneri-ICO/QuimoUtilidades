import psycopg2
conn = psycopg2.connect(
    dbname="quimoBD",
    user="postgres",
    password="67190",
    host="localhost",
    port="5432"
)
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM productos")
print(cur.fetchone())
conn.close()


from sqlalchemy import create_engine
engine = create_engine('postgresql://postgres:67190@localhost:5432/quimoBD')
df = pd.read_sql_query("SELECT * FROM productos", engine)