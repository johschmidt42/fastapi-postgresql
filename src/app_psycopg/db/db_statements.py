from typing import LiteralString

insert_user_stmt: LiteralString = """
    INSERT INTO users (id, name, created_at) VALUES (%(id)s, %(name)s, %(created_at)s)
    RETURNING id
"""

get_user_stmt: LiteralString = """
    SELECT * FROM users WHERE id = %(id)s
"""

update_user_stmt: LiteralString = """
    UPDATE users SET (name, last_updated_at) = (%(name)s, %(last_updated_at)s)
    WHERE id = %(id)s
    RETURNING id
"""

delete_user_stmt: LiteralString = """
    DELETE FROM users WHERE id = %(id)s
"""

insert_order_stmt: LiteralString = """
    INSERT INTO orders (id, amount, payer_id, payee_id) VALUES (%(id)s, %(amount)s, %(payer_id)s, %(payee_id)s)
    RETURNING id
"""

get_order_stmt: LiteralString = """
    SELECT 
        t.*,
        row_to_json(u1.*) payer,
        row_to_json(u2.*) payee
    FROM orders t
    JOIN users u1 ON t.payer_id = u1.id
    JOIN users u2 ON t.payee_id = u2.id
"""
