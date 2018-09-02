import logging
from urllib.parse import urlencode
from urllib.request import urlopen

from pystrich.datamatrix import DataMatrixEncoder, DataMatrixRenderer

from .credentials import SIGNATURE_USER, SIGNATURE_PASS
from .customization import SIGNATURE_URLS
from .ui.common import show_error


logger = logging.getLogger(__name__)

API_DATE_FMT = '%d.%m.%Y'


def sign(rcc, patient_birthday, patient_zip, treatment_cost_cts, treatment_date):
    if not all([SIGNATURE_URLS, SIGNATURE_USER, SIGNATURE_PASS]):
        # If we miss one of them then silently skip signing
        return None
    data = urlencode(dict(zsr=rcc,
                          patientBirthday=patient_birthday.strftime(API_DATE_FMT),
                          patientPostalCode=patient_zip,
                          treatmentCost='%0.2f' % (treatment_cost_cts/100),
                          treatmentBirthday=treatment_date.strftime(API_DATE_FMT),
                          apiUser=SIGNATURE_USER,
                          apiPassword=SIGNATURE_PASS)).encode()
    errors = []
    for url in SIGNATURE_URLS:
        try:
            response = urlopen(url, data)
        except OSError as e:
            errors.append(e)
        else:
            return response.read().decode()
    if errors:
        show_error(logger,
                "Une erreur s'est produite lors de l'obtention de la signature:\n"
                "{}\n"
                "La facture ne possédera pas de 2D-barcode de signature.".format(errors[0]))
        return None


def datamatrix(signature):
    m = DataMatrixEncoder(signature)
    r = DataMatrixRenderer(m.matrix, m.regions)
    return r.get_pilimage(2)
