from .models import conn

def get_active_properties():
    with conn.cursor() as cur:
        cur.execute("SELECT id, address FROM properties WHERE active = TRUE LIMIT 10;")
        return cur.fetchall()

def get_property_info(property_id):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                p.number, p.area, o.name, o.birthdate, p.type, p.share, c.comment
            FROM
                properties p
            LEFT JOIN
                owners o ON p.owner_id = o.id
            LEFT JOIN
                comments c ON p.id = c.property_id
            WHERE
                p.id = %s;
        """, (property_id,))
        return cur.fetchall()

def add_comment(property_id, owner_id, comment):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO comments (property_id, owner_id, comment)
            VALUES (%s, %s, %s);
        """, (property_id, owner_id, comment))
        conn.commit()
