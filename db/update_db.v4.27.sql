ALTER TABLE bills ALTER COLUMN site DROP DEFAULT;
ALTER TABLE patients ALTER COLUMN site DROP DEFAULT;
ALTER TABLE consultations ALTER COLUMN site DROP DEFAULT;

CREATE INDEX patients_site_idx ON patients (site);
CREATE INDEX consultations_site_idx ON consultations (site);

CREATE TABLE version_info (db_version int);
INSERT INTO version_info VALUES (1);
