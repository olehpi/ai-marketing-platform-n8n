docker exec -it container_postgres psql -U POSTGRES_USER -d POSTGRES_DB
docker logs container_postgres --tail 50

SELECT * FROM n8n_chat_histories ORDER BY id DESC LIMIT 1;
SELECT * FROM n8n_chat_histories LIMIT 20;

WITH deleted AS (
    DELETE FROM n8n_chat_histories
    WHERE session_id = SESSION_ID
    RETURNING id
)



