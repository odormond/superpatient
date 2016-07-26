CREATE TABLE factures_manuelles (id integer not null auto_increment unique, identifiant text, therapeute text, destinataire text, motif text, montant_cts integer, remarque text, date date, paye_le date, bv_ref text);
CREATE TABLE adresses (id text, adresse text);
