-- Insert professions
INSERT INTO profession (id, name)
VALUES (gen_random_uuid(), 'Engineer'),
(gen_random_uuid(), 'Doctor'),
(gen_random_uuid(), 'Artist');

-- Insert users
INSERT INTO users (id, name, created_at, last_updated_at, profession_id)
VALUES (
    gen_random_uuid(), 'Alice', now(), NULL, (
        SELECT id FROM profession
        ORDER BY random() LIMIT 1
    )
),
(
    gen_random_uuid(), 'Bob', now(), NULL, (
        SELECT id FROM profession
        ORDER BY random() LIMIT 1
    )
),
(
    gen_random_uuid(), 'Charlie', now(), NULL, (
        SELECT id FROM profession
        ORDER BY random() LIMIT 1
    )
),
(
    gen_random_uuid(), 'Diana', now(), NULL, (
        SELECT id FROM profession
        ORDER BY random() LIMIT 1
    )
),
(
    gen_random_uuid(), 'Eve', now(), NULL, (
        SELECT id FROM profession
        ORDER BY random() LIMIT 1
    )
),
(
    gen_random_uuid(), 'Frank', now(), NULL, (
        SELECT id FROM profession
        ORDER BY random() LIMIT 1
    )
),
(
    gen_random_uuid(), 'Grace', now(), NULL, (
        SELECT id FROM profession
        ORDER BY random() LIMIT 1
    )
),
(
    gen_random_uuid(), 'Hannah', now(), NULL, (
        SELECT id FROM profession
        ORDER BY random() LIMIT 1
    )
),
(
    gen_random_uuid(), 'Isaac', now(), NULL, (
        SELECT id FROM profession
        ORDER BY random() LIMIT 1
    )
),
(
    gen_random_uuid(), 'Jack', now(), NULL, (
        SELECT id FROM profession
        ORDER BY random() LIMIT 1
    )
),
(
    gen_random_uuid(), 'Kevin', now(), NULL, (
        SELECT id FROM profession
        ORDER BY random() LIMIT 1
    )
),
(
    gen_random_uuid(), 'Lily', now(), NULL, (
        SELECT id FROM profession
        ORDER BY random() LIMIT 1
    )
),
(
    gen_random_uuid(), 'Mia', now(), NULL, (
        SELECT id FROM profession
        ORDER BY random() LIMIT 1
    )
),
(
    gen_random_uuid(), 'Nathan', now(), NULL, (
        SELECT id FROM profession
        ORDER BY random() LIMIT 1
    )
),
(
    gen_random_uuid(), 'Olivia', now(), NULL, (
        SELECT id FROM profession
        ORDER BY random() LIMIT 1
    )
),
(
    gen_random_uuid(), 'Paul', now(), NULL, (
        SELECT id FROM profession
        ORDER BY random() LIMIT 1
    )
),
(
    gen_random_uuid(), 'Quinn', now(), NULL, (
        SELECT id FROM profession
        ORDER BY random() LIMIT 1
    )
),
(
    gen_random_uuid(), 'Ryan', now(), NULL, (
        SELECT id FROM profession
        ORDER BY random() LIMIT 1
    )
),
(
    gen_random_uuid(), 'Sophia', now(), NULL, (
        SELECT id FROM profession
        ORDER BY random() LIMIT 1
    )
),
(
    gen_random_uuid(), 'Tom', now(), NULL, (
        SELECT id FROM profession
        ORDER BY random() LIMIT 1
    )
);

-- Insert orders
INSERT INTO orders (id, amount, payer_id, payee_id)
VALUES (
    gen_random_uuid(), 250.00, (
        SELECT id FROM users
        ORDER BY random() LIMIT 1
    ),
    (
        SELECT id FROM users
        ORDER BY random() LIMIT 1
    )
),
(
    gen_random_uuid(), 500.50, (
        SELECT id FROM users
        ORDER BY random() LIMIT 1
    ),
    (
        SELECT id FROM users
        ORDER BY random() LIMIT 1
    )
),
(
    gen_random_uuid(), 75.90, (
        SELECT id FROM users
        ORDER BY random() LIMIT 1
    ),
    (
        SELECT id FROM users
        ORDER BY random() LIMIT 1
    )
),
(
    gen_random_uuid(), 999.99, (
        SELECT id FROM users
        ORDER BY random() LIMIT 1
    ),
    (
        SELECT id FROM users
        ORDER BY random() LIMIT 1
    )
),
(
    gen_random_uuid(), 120.75, (
        SELECT id FROM users
        ORDER BY random() LIMIT 1
    ),
    (
        SELECT id FROM users
        ORDER BY random() LIMIT 1
    )
);

-- Insert documents
INSERT INTO documents (id, document, created_at, last_updated_at)
VALUES (
    gen_random_uuid(),
    '{"title": "Doc1", "content": "Sample content 1"}',
    now(),
    NULL
),
(
    gen_random_uuid(),
    '{"title": "Doc2", "content": "Sample content 2"}',
    now(),
    NULL
),
(
    gen_random_uuid(),
    '{"title": "Doc3", "content": "Sample content 3"}',
    now(),
    NULL
),
(
    gen_random_uuid(),
    '{"title": "Doc4", "content": "Sample content 4"}',
    now(),
    NULL
),
(
    gen_random_uuid(),
    '{"title": "Doc5", "content": "Sample content 5"}',
    now(),
    NULL
),
(
    gen_random_uuid(),
    '{"title": "Doc6", "content": "Sample content 6"}',
    now(),
    NULL
),
(
    gen_random_uuid(),
    '{"title": "Doc7", "content": "Sample content 7"}',
    now(),
    NULL
),
(
    gen_random_uuid(),
    '{"title": "Doc8", "content": "Sample content 8"}',
    now(),
    NULL
),
(
    gen_random_uuid(),
    '{"title": "Doc9", "content": "Sample content 9"}',
    now(),
    NULL
),
(
    gen_random_uuid(),
    '{"title": "Doc10", "content": "Sample content 10"}',
    now(),
    NULL
),
(
    gen_random_uuid(),
    '{"title": "Doc11", "content": "Sample content 11"}',
    now(),
    NULL
),
(
    gen_random_uuid(),
    '{"title": "Doc12", "content": "Sample content 12"}',
    now(),
    NULL
),
(
    gen_random_uuid(),
    '{"title": "Doc13", "content": "Sample content 13"}',
    now(),
    NULL
),
(
    gen_random_uuid(),
    '{"title": "Doc14", "content": "Sample content 14"}',
    now(),
    NULL
),
(
    gen_random_uuid(),
    '{"title": "Doc15", "content": "Sample content 15"}',
    now(),
    NULL
);
