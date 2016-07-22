ALTER TABLE consultations ADD COLUMN bv_ref varchar(27);
CREATE TABLE bvr_sequence (counter integer NOT NULL);
INSERT INTO bvr_sequence VALUES (1);
