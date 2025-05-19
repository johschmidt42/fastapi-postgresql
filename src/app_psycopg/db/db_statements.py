from typing import LiteralString

# region User

insert_user_stmt: LiteralString = """
    INSERT INTO users (id, name, created_at, profession_id) VALUES (%(id)s, %(name)s, %(created_at)s, %(profession_id)s)
    RETURNING id
"""

get_users_stmt: LiteralString = """
    SELECT 
        u.id, u.name, u.created_at, u.last_updated_at,
        row_to_json(p.*) profession
    FROM users u
    JOIN profession p ON u.profession_id = p.id
"""

get_users_count_stmt: LiteralString = """
    SELECT COUNT(*) FROM users
"""

get_user_stmt: LiteralString = """
    SELECT 
        u.id, u.name, u.created_at, u.last_updated_at,
        row_to_json(p.*) profession
    FROM users u
    JOIN profession p ON u.profession_id = p.id
    WHERE u.id = %(id)s
"""

update_user_stmt: LiteralString = """
    UPDATE users SET (name, last_updated_at, profession_id) = (%(name)s, %(last_updated_at)s, %(profession_id)s)
    WHERE id = %(id)s
    RETURNING id
"""

patch_user_stmt: LiteralString = """
    UPDATE users
    SET 
        name = COALESCE(%(name)s, name),
        last_updated_at = %(last_updated_at)s,
        profession_id = COALESCE(%(profession_id)s, profession_id)
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

# endregion

# region Order

get_order_stmt: LiteralString = """
    SELECT 
        t.id, t.amount,
        row_to_json(u1.*) payer,
        row_to_json(u2.*) payee
    FROM orders t
    JOIN users u1 ON t.payer_id = u1.id
    JOIN users u2 ON t.payee_id = u2.id
"""

get_orders_stmt: LiteralString = """
    SELECT * FROM orders
"""

get_orders_count_stmt: LiteralString = """
    SELECT COUNT(*) FROM orders
"""

# endregion

# region Document

insert_document_stmt: LiteralString = """
    INSERT INTO documents (id, document, created_at) VALUES (%(id)s, %(document)s, %(created_at)s)
    RETURNING id
"""

get_document_stmt: LiteralString = """
    SELECT * FROM documents WHERE id = %(id)s
"""

get_documents_stmt: LiteralString = """
    SELECT * FROM documents
"""

get_documents_count_stmt: LiteralString = """
    SELECT COUNT(*) FROM documents
"""

document_user_stmt: LiteralString = """
    UPDATE documents SET (document, last_updated_at) = (%(document)s, %(last_updated_at)s)
    WHERE id = %(id)s
    RETURNING id
"""

delete_document_stmt: LiteralString = """
    DELETE FROM documents WHERE id = %(id)s
"""

# endregion

# region Profession

insert_profession_stmt: LiteralString = """
    INSERT INTO profession (id, name, created_at) VALUES (%(id)s, %(name)s, %(created_at)s)
    RETURNING id
"""

get_profession_stmt: LiteralString = """
    SELECT * FROM profession WHERE id = %(id)s
"""

get_professions_stmt: LiteralString = """
    SELECT * FROM profession
"""

get_professions_count_stmt: LiteralString = """
    SELECT COUNT(*) FROM profession
"""

update_profession_stmt: LiteralString = """
    UPDATE profession SET (name, last_updated_at) = (%(name)s, %(last_updated_at)s)
    WHERE id = %(id)s
    RETURNING id
"""

delete_profession_stmt: LiteralString = """
    DELETE FROM profession WHERE id = %(id)s
"""

# endregion
