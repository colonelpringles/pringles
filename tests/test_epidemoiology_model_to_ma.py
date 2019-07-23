import pytest
from typing import Callable
from colonel.models.models import Model, AtomicModelBuilder, Coupled, Atomic, InPort, OutPort, IntLink, ExtInputLink, ExtOutputLink

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


def empty_top_model_generator() -> Model:
    return Coupled("top", [])


def interacciones_poblacion_model_generator() -> Model:
    FocoAtomic = AtomicModelBuilder().withName("Foco").build()
    ContagioAtomic = AtomicModelBuilder().withName("Contagio").build()

    a_foco = FocoAtomic("foco", mean=2, std=1)
    foco_inport = a_foco.add_inport("in")
    foco_outport = a_foco.add_outport("out")

    a_contagio = ContagioAtomic("contagio", threshold_NV=30, threshold_V=80)
    contagio_inport = a_contagio.add_inport("in")
    contagio_outport = a_contagio.add_outport("out")

    interacciones_poblacion = Coupled("interacciones_poblacion",
                                      [a_foco, a_contagio])
    ip_inport = interacciones_poblacion.add_inport("in_port")
    ip_outport = interacciones_poblacion.add_outport("out_port")

    interacciones_poblacion.add_coupling(ip_inport, foco_inport)
    interacciones_poblacion.add_coupling(foco_outport, contagio_inport)
    interacciones_poblacion.add_coupling(contagio_outport, ip_outport)

    return interacciones_poblacion


@pytest.mark.parametrize("model_generator_func,expected_ma_file", [
    (empty_top_model_generator, "tests/generated_mas/empty_model.ma"),
    (interacciones_poblacion_model_generator, "tests/generated_mas/interacciones_poblacion.ma"),
])
def test_model_is_translated_into_ma_correctly(
        model_generator_func: Callable[[], Model],
        expected_ma_file: str):
    generated_model = model_generator_func()
    expected_model_text = ""
    with open(expected_ma_file, "r") as expected_ma_file:
        expected_model_text = expected_ma_file.read()
    assert generated_model.to_ma() == expected_model_text
