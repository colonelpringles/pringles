import pytest
from typing import Callable
from colonel.models.models import Model, AtomicModelBuilder, Coupled, Atomic, InPort, OutPort, IntLink, ExtInputLink, ExtOutputLink, PortNotFoundException
from colonel.serializers import MaSerializer


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

    interacciones_poblacion = Coupled("interacciones_poblacion", [a_foco, a_contagio])\
        .add_inport("in_port")\
        .add_outport("out_port")\
        .add_coupling("in_port", a_foco.get_port("in"))\
        .add_coupling(a_foco.get_port("out"), a_contagio.get_port("in"))\
        .add_coupling(a_contagio.get_port("out"), "out_port")\

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
    assert MaSerializer().serialize(generated_model) == expected_model_text


def test_non_existing_port():
    with pytest.raises(PortNotFoundException):
        empty_model = Coupled("test_model", [])
        empty_model.get_port("holis")
