from urllib.parse import urlencode
from urllib.request import urlopen

from pystrich.datamatrix import DataMatrixEncoder, DataMatrixRenderer

from .credentials import SIGNATURE_USER, SIGNATURE_PASS
from .customization import SIGNATURE_URL
from .ui.common import showerror

API_DATE_FMT = '%d.%m.%Y'


def sign(rcc, patient_birthday, patient_zip, treatment_cost_cts, treatment_date):
    if not all([SIGNATURE_URL, SIGNATURE_USER, SIGNATURE_PASS]):
        # If we miss one of them then silently skip signing
        return None
    data = urlencode(dict(zsr=rcc,
                          patientBirthday=patient_birthday.strftime(API_DATE_FMT),
                          patientPostalCode=patient_zip,
                          treatmentCost='%0.2f' % (treatment_cost_cts/100),
                          treatmentBirthday=treatment_date.strftime(API_DATE_FMT),
                          apiUser=SIGNATURE_USER,
                          apiPassword=SIGNATURE_PASS)).encode()
    try:
        response = urlopen(SIGNATURE_URL, data)
    except OSError as e:
        try:
            SIG_ARRAY = SIGNATURE_URL.split(".")
            SIG_ARRAY[0] += "2"
            SIGNATURE2_URL = ".".join(SIG_ARRAY)
            response = urlopen(SIGNATURE2_URL, data)
        except OSError as e2:
            showerror("Signature impossible",
                  "Une erreur s'est produite lors de l'obtention de la signature:\n"
                  "{}\n"
                  "La facture ne possédera pas de 2D-barcode de signature.".format(e))
            return None
        else:
            return response.read().decode()
    else:
        return response.read().decode()


def datamatrix(signature):
    m = DataMatrixEncoder(signature)
    r = DataMatrixRenderer(m.matrix, m.regions)
    return r.get_pilimage(2)
