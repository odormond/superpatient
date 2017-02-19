CREATE TABLE frais_admins (description text, prix_cts integer);
INSERT INTO frais_admins VALUES ('BV', 500);
ALTER TABLE consultations ADD COLUMN frais_admin_cts integer AFTER majoration_txt, ADD COLUMN frais_admin_txt text AFTER frais_admin_cts;
UPDATE consultations SET frais_admin_cts = 0, frais_admin_txt = '' WHERE majoration_cts % 1000 = 0;
UPDATE consultations SET frais_admin_cts = 500, frais_admin_txt = 'BV', majoration_cts = 2000, majoration_txt = 'Majorations sam./jour férié' WHERE majoration_txt = 'Majorations sam./jour férié + BV';
UPDATE consultations SET frais_admin_cts = 500, frais_admin_txt = 'BV', majoration_cts = 0, majoration_txt = '' WHERE majoration_txt = 'Frais administratifs (BV)';
