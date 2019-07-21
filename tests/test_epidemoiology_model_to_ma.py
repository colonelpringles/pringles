import pytest
from colonel.models.models import Coupled, Atomic, InPort, OutPort, IntLink, ExtInputLink, ExtOutputLink

expected_interacciones_poblacion_ma = """[interacciones_poblacion]
components : foco@Foco contagio@Contagio
out : out_port
in : in_port
link : in_port in@foco
link : out@foco in@contagio
link : out@contagio out_port


[foco]
mean : 2
std : 1


[contagio]
threshold_NV : 30
threshold_V : 80
"""

class Poblacion(Atomic):
    pass


class Contagio(Atomic):
    pass


class Foco(Atomic):
    pass


class SistPrevencion(Atomic):
    pass


class Paranoia(Atomic):
    pass


class Vacunatorio(Atomic):
    pass


def test_empty_top_model_is_drawn_correctly():
    top_model = Coupled("top", [])
    assert top_model.to_ma() == "[top]\ncomponents: \nout: \nin: \n"


def test_top_model_with_one_atomic_is_drawn_correctly():

    a_foco = Foco("foco", mean=2, std=1)
    foco_inport = a_foco.add_inport("in")
    foco_outport = a_foco.add_outport("out")

    a_contagio = Contagio("contagio", threshold_NV=30, threshold_V=80)
    contagio_inport = a_contagio.add_inport("in")
    contagio_outport = a_contagio.add_outport("out")

    interacciones_poblacion = Coupled("interacciones_poblacion", 
                                      [a_foco, a_contagio])
    ip_inport = interacciones_poblacion.add_inport("in_port")
    ip_outport = interacciones_poblacion.add_outport("out_port")

    interacciones_poblacion.add_external_input_coupling(
        ExtInputLink(ip_inport, foco_inport))

    interacciones_poblacion.add_internal_coupling(
        IntLink(foco_outport, contagio_inport))

    interacciones_poblacion.add_external_output_coupling(
        ExtOutputLink(contagio_outport, ip_outport))
    
    assert interacciones_poblacion.to_ma().replace(" ", "") == expected_interacciones_poblacion_ma.replace(" ", "")