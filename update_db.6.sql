ALTER TABLE consultations ADD COLUMN status varchar(1) NOT NULL DEFAULT 'O';
UPDATE TABLE consultations SET status = 'P' WHERE paye_le IS NOT NULL;
ALTER TABLE factures_manuelles ADD COLUMN status varchar(1) NOT NULL DEFAULT 'O';
UPDATE TABLE factures_manuelles SET status = 'P' WHERE paye_le IS NOT NULL;
ALTER TABLE rappels ADD COLUMN status varchar(1) NOT NULL DEFAULT 'O';
UPDATE TABLE rappels SET status = 'P' WHERE paye_le IS NOT NULL;
