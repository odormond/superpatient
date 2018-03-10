ALTER TABLE bills ADD COLUMN signature text;
ALTER TABLE positions ADD COLUMN total_cts integer;
UPDATE positions SET total_cts = quantity * price_cts;
ALTER TABLE positions MODIFY COLUMN total_cts integer NOT NULL;
