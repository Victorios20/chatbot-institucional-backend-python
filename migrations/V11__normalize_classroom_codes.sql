-- One building letter A-Z and two room digits 01-99. Preserve valid codes.
WITH rooms AS (
    SELECT id,
           COALESCE(substring(room FROM '(?i)bloco\s+([A-Z])'), 'A') AS building,
           row_number() OVER (ORDER BY id) AS room_number
    FROM subject_offerings
    WHERE room IS NULL OR room !~ '^[A-Z](0[1-9]|[1-9][0-9])$'
)
UPDATE subject_offerings o
SET room = upper(r.building) || lpad((((r.room_number - 1) % 80) + 1)::text, 2, '0')
FROM rooms r WHERE o.id = r.id;

ALTER TABLE subject_offerings ADD CONSTRAINT subject_offerings_room_code
CHECK (room IS NOT NULL AND room ~ '^[A-Z](0[1-9]|[1-9][0-9])$');
