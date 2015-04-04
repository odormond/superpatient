ALTER TABLE consultations ADD COLUMN therapeute varchar(20), ADD COLUMN prix_cts integer, ADD COLUMN paye_par varchar(20), ADD COLUMN paye_le date;
CREATE TABLE tarifs (description text, prix_cts integer);
INSERT INTO tarifs VALUES ('entre 21 et 30 minutes', 10000), ('entre 31 et 40 minutes', 11000), ('entre 41 et 50 minutes', 12000);
CREATE TABLE therapeutes (therapeute varchar(20), adresse text);
INSERT INTO therapeutes VALUES ('tib', 'Tibor Csernay\nDipl. CDS-GDK\n\nAv. de la gare 5\n1003 Lausanne\n021 510 50 50\n021 510 50 49 (N° direct)\n\nRCC U905461'),
                               ('ch', 'Christophe Guinand\nDipl. CDS-GDK\n\nAv. de la gare 5\n1003 Lausanne\n021 510 50 50\n021 510 50 48 (No direct)\n\nRCC H503260\nRME 20663'),
                               ('lik', 'Laure-Isabelle Kazemi\nDipl. CDS-GDK\nMembre FSO\n\nAv. de la gare 5\n1003 Lausanne\n021 510 50 50\n021 510 50 47 (No direct)\n\nRCC K097161\nASCA K587449'),
                               ('CRT', 'Av. de la gare 5\n1003 Lausanne\n021 510 50 50');
