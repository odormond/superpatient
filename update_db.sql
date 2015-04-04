ALTER TABLE consultations ADD COLUMN therapeute varchar(20), ADD COLUMN prix_cts integer, ADD COLUMN paye_par varchar(20), ADD COLUMN paye_le date;
CREATE TABLE tarifs (description text, prix_cts integer);
INSERT INTO tarifs VALUES ('entre 21 et 30 minutes', 10000), ('entre 31 et 40 minutes', 11000), ('entre 41 et 50 minutes', 12000);
