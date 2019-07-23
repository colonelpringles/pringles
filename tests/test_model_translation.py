import pytest
from typing import Callable
from colonel.models.models import Model, AtomicModelBuilder, Coupled, Atomic, InPort, OutPort, IntLink, ExtInputLink, ExtOutputLink


def empty_top_model_generator() -> Model:
    return Coupled("top", [])


def interacciones_poblacion_model_generator() -> Model:
    FocoAtomic = AtomicModelBuilder().withName("Foco").build()
    ContagioAtomic = AtomicModelBuilder().withName("Contagio").build()

    a_foco = FocoAtomic("foco", mean=2, std=1)
    a_foco.add_inport("in")
    a_foco.add_outport("out")

    a_contagio = ContagioAtomic("contagio", threshold_NV=30, threshold_V=80)
    a_contagio.add_inport("in")
    a_contagio.add_outport("out")

    interacciones_poblacion = Coupled.builder() \
        .withName("interacciones_poblacion")\
        .withComponent(a_foco)\
        .withComponent(a_contagio)\
        .withInPort("in_port")\
        .withOutPort("out_port")\
        .withCoupling("in_port", a_foco.get_port("in"))\
        .withCoupling(a_foco.get_port("out"), a_contagio.get_port("in"))\
        .withCoupling(a_contagio.get_port("out"), "out_port")\
        .build()

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
