ALTER TABLE consultations ADD COLUMN therapeute varchar(20), ADD COLUMN prix_cts integer, ADD COLUMN majoration_cts integer, ADD COLUMN paye_par varchar(20), ADD COLUMN paye_le date;
UPDATE consultations SET majoration_cts = 0;
CREATE TABLE tarifs (description text, prix_cts integer);
INSERT INTO tarifs VALUES ('entre 21 et 30 minutes', 10000), ('entre 31 et 40 minutes', 11000), ('entre 41 et 50 minutes', 12000);
CREATE TABLE therapeutes (therapeute varchar(20), entete text);
INSERT INTO therapeutes VALUES ('tib', 'Tibor Csernay\nDipl. CDS-GDK\nRCC U905461'),
                               ('ch', 'Christophe Guinand\nDipl. CDS-GDK\nRME 20663\nRCC H503260'),
                               ('lik', 'Laure-Isabelle Kazemi\nMembre FSO-SVO\nDipl. CDS-GDK\nRCC K097161\nASCA K587449'),
                               ('mel', 'Mélanie Zurbuchen\nRME 28907\nRCC K349160'),
                               ('gal', 'Gaëlle Langel\nRME 29248\nRCC F342060'),
                               ('sts', 'Stéphanie Schmid\nRME 30427\nRCC S632862');
