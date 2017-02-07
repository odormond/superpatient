UPDATE consultations set paye_le = null WHERE id_consult = 17880;
ALTER TABLE consultations ADD COLUMN prix_txt text AFTER prix_cts;
UPDATE consultations SET prix_txt = (SELECT description FROM tarifs WHERE tarifs.prix_cts = consultations.prix_cts);
ALTER TABLE consultations ADD COLUMN majoration_txt text AFTER majoration_cts;
UPDATE consultations SET majoration_txt = (SELECT description FROM majorations WHERE majorations.prix_cts = consultations.majoration_cts ORDER BY description DESC LIMIT 1);
