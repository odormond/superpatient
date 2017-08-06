ALTER TABLE consultations ADD COLUMN status varchar(1) NOT NULL DEFAULT 'O';
UPDATE consultations SET status = 'P' WHERE paye_le IS NOT NULL;
ALTER TABLE factures_manuelles ADD COLUMN status varchar(1) NOT NULL DEFAULT 'O';
UPDATE factures_manuelles SET status = 'P' WHERE paye_le IS NOT NULL;
ALTER TABLE rappels ADD COLUMN status varchar(1) NOT NULL DEFAULT 'O';
UPDATE rappels SET status = 'O' WHERE paye IS NULL or NOT paye;
UPDATE rappels SET status = 'P' WHERE paye IS NOT NULL and paye;
ALTER TABLE rappels DROP COLUMN paye;
