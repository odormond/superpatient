ALTER TABLE consultations ADD COLUMN prix_txt text AFTER prix_cts;
UPDATE consultations SET prix_txt = (SELECT description FROM tarifs WHERE tarifs.prix_cts = consultations.prix_cts);
ALTER TABLE consultations ADD COLUMN majoration_txt text AFTER majoration_cts;
UPDATE consultations SET majoration_txt = (SELECT description FROM majorations WHERE majorations.prix_cts = consultations.majoration_cts LIMIT 1);
