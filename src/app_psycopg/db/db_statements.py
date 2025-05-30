from typing import LiteralString

# region User

insert_user_stmt: LiteralString = """
    INSERT INTO users (id, name, created_at, profession_id) VALUES (%(id)s, %(name)s, %(created_at)s, %(profession_id)s)
    ON CONFLICT (id) DO NOTHING
    RETURNING id
"""

get_users_stmt: LiteralString = """
    SELECT 
        u.id, u.name, u.created_at, u.last_updated_at,
        json_build_object(
            'id', p.id,
            'name', p.name
        ) profession
    FROM users u
    JOIN professions p ON u.profession_id = p.id
"""

get_users_count_stmt: LiteralString = """
    SELECT COUNT(*) FROM users
"""

get_user_stmt: LiteralString = """
    SELECT 
        u.id, u.name, u.created_at, u.last_updated_at,
        json_build_object(
            'id', p.id,
            'name', p.name
        ) profession
    FROM users u
    JOIN professions p ON u.profession_id = p.id
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

# endregion

# region Order

insert_order_stmt: LiteralString = """
    INSERT INTO orders (id, amount, payer_id, payee_id, created_at) VALUES (%(id)s, %(amount)s, %(payer_id)s, %(payee_id)s, %(created_at)s)
    ON CONFLICT (id) DO NOTHING
    RETURNING id
"""

get_order_stmt: LiteralString = """
    SELECT 
        t.id, t.amount, t.created_at,
        json_build_object(
            'id', u1.id,
            'name', u1.name
        ) payer,
        json_build_object(
            'id', u2.id,
            'name', u2.name
        ) payee
    FROM orders t
    JOIN users u1 ON t.payer_id = u1.id
    JOIN users u2 ON t.payee_id = u2.id
    WHERE t.id = %(id)s
"""

get_orders_stmt: LiteralString = """
    SELECT 
        t.id, t.amount, t.created_at,
        json_build_object(
            'id', u1.id,
            'name', u1.name
        ) payer,
        json_build_object(
            'id', u2.id,
            'name', u2.name
        ) payee
    FROM orders t
    JOIN users u1 ON t.payer_id = u1.id
    JOIN users u2 ON t.payee_id = u2.id
"""

get_orders_count_stmt: LiteralString = """
    SELECT COUNT(*) FROM orders
"""

delete_order_stmt: LiteralString = """
    DELETE FROM orders WHERE id = %(id)s
"""

# endregion

# region Document

insert_document_stmt: LiteralString = """
    INSERT INTO documents (id, document, created_at, user_id) VALUES (%(id)s, %(document)s, %(created_at)s, %(user_id)s)
    ON CONFLICT (id) DO NOTHING
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
    INSERT INTO professions (id, name, created_at) VALUES (%(id)s, %(name)s, %(created_at)s)
    ON CONFLICT (id) DO NOTHING
    RETURNING id
"""

get_profession_stmt: LiteralString = """
    SELECT * FROM professions WHERE id = %(id)s
"""

get_professions_stmt: LiteralString = """
    SELECT * FROM professions
"""

get_professions_count_stmt: LiteralString = """
    SELECT COUNT(*) FROM professions
"""

update_profession_stmt: LiteralString = """
    UPDATE professions SET (name, last_updated_at) = (%(name)s, %(last_updated_at)s)
    WHERE id = %(id)s
    RETURNING id
"""

delete_profession_stmt: LiteralString = """
    DELETE FROM professions WHERE id = %(id)s
"""

# endregion

# region Company

insert_company_stmt: LiteralString = """
    INSERT INTO companies (id, name, created_at) VALUES (%(id)s, %(name)s, %(created_at)s)
    ON CONFLICT (id) DO NOTHING
    RETURNING id
"""

get_company_stmt: LiteralString = """
    SELECT * FROM companies WHERE id = %(id)s
"""

get_companies_stmt: LiteralString = """
    SELECT * FROM companies
"""

get_companies_count_stmt: LiteralString = """
    SELECT COUNT(*) FROM companies
"""

update_company_stmt: LiteralString = """
    UPDATE companies SET (name, last_updated_at) = (%(name)s, %(last_updated_at)s)
    WHERE id = %(id)s
    RETURNING id
"""

patch_company_stmt: LiteralString = """
    UPDATE companies
    SET 
        name = COALESCE(%(name)s, name),
        last_updated_at = %(last_updated_at)s
    WHERE id = %(id)s
    RETURNING id
"""

delete_company_stmt: LiteralString = """
    DELETE FROM companies WHERE id = %(id)s
"""

# endregion

# region UserCompanyLink

get_user_company_link_stmt: LiteralString = """
    SELECT * FROM users_companies WHERE user_id = %(user_id)s AND company_id = %(company_id)s
"""

insert_user_company_link_stmt: LiteralString = """
    INSERT INTO users_companies (user_id, company_id, created_at) 
    VALUES (%(user_id)s, %(company_id)s, %(created_at)s)
    ON CONFLICT (user_id, company_id) DO NOTHING
    RETURNING user_id, company_id
"""

get_user_company_links_by_user_stmt: LiteralString = """
    SELECT 
        uc.user_id, uc.created_at,
        json_build_object(
            'id', c.id,
            'name', c.name
        ) company
    FROM users_companies uc
    JOIN companies c ON uc.company_id = c.id
    WHERE uc.user_id = %(user_id)s
"""

get_user_company_links_by_company_stmt: LiteralString = """
    SELECT 
        uc.company_id, uc.created_at,
        json_build_object(
            'id', u.id,
            'name', u.name
        ) user_info
    FROM users_companies uc
    JOIN users u ON uc.user_id = u.id
    WHERE uc.company_id = %(company_id)s
"""

get_user_company_links_count_by_user_stmt: LiteralString = """
    SELECT COUNT(*) FROM users_companies WHERE user_id = %(user_id)s
"""

get_user_company_links_count_by_company_stmt: LiteralString = """
    SELECT COUNT(*) FROM users_companies WHERE company_id = %(company_id)s
"""

delete_user_company_link_stmt: LiteralString = """
    DELETE FROM users_companies 
    WHERE user_id = %(user_id)s AND company_id = %(company_id)s
"""

# endregion
