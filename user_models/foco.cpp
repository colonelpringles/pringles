#include "message.h"
#include "parsimu.h"
#include "assert.h"
#include "foco.h"
#include "helpers.h"

using namespace std;

Foco::Foco( const string &name )
: Atomic( name ),
  in(addInputPort( "in" )),
  out(addOutputPort( "out" )) {
}


Model &Foco::initFunction() {
	passivate();
	resetParejas();
    double mean = 0.5;
    double std = 0.15;
	if (ParallelMainSimulator::Instance().existsParameter(description(), "mean")) {
		mean = str2Value(ParallelMainSimulator::Instance().getParameter(description(), "mean"));
	}
    if (ParallelMainSimulator::Instance().existsParameter(description(), "std")) {
		std = str2Value(ParallelMainSimulator::Instance().getParameter(description(), "std"));
	}

    dist = Distribution::create("normal");
    dist->setVar(0, mean);
    dist->setVar(1, std);
	return *this ;
}


Model &Foco::externalFunction( const ExternalMessage &msg ) {
	nextChange(VTime::Zero);
    Tuple<Real> poblacion = Tuple<Real>::from_value(msg.value()); // SIRV (NV) SIRV (V)
    vector<double> pobl_vec = from_tuple(poblacion);

	resetParejas();
    int tamanio_pobl = get_cant_poblacion(poblacion);
    double cant_parejas = tamanio_pobl * get_randnorm(0, tamanio_pobl);
    // cout<< "cant_parejas" << cant_parejas << endl;
    for (int i=0; i<cant_parejas; i++) {
        Estado persona1 = randpick(pobl_vec);
        assert (pobl_vec[uint(persona1)] > 0);
        pobl_vec[uint(persona1)] -= 1;
        Estado persona2 = randpick(pobl_vec);
        assert (pobl_vec[uint(persona2)] > 0);
        pobl_vec[uint(persona2)] -= 1;
        // cout << persona1 << " con " << persona2 << endl;

        pair<Estado, Estado> pareja = make_pair(persona1,persona2);
        if (this->parejas.find(pareja) == this->parejas.end()){
            pareja = make_pair(persona2, persona1);
        }
        this->parejas[pareja] ++;
        if (get_cant_poblacion(pobl_vec) < 2) {
            return *this;
        }
    }
	return *this ;
}

double Foco::get_randnorm(int min, int max) {
    float result = dist->get();
    if (result > max) {
        return max;
    } else if (result < min) {
        return min;
    }
    return result;
}


Model &Foco::internalFunction( const InternalMessage & ) {
	passivate();
	return *this;
}


Model &Foco::outputFunction( const CollectMessage &msg ) {

    double encuentos_altoriesgo = this->parejas[std::make_pair(SusceptibleV, InfectadoNV)] +
                                  this->parejas[std::make_pair(SusceptibleV, InfectadoV)];
    double encuentos_bajoriesgo = this->parejas[std::make_pair(SusceptibleNV, InfectadoNV)] +
                                  this->parejas[std::make_pair(SusceptibleNV, InfectadoV)];
    // cout << "hay altoriesgo " << this->parejas[std::make_pair(SusceptibleV, InfectadoNV)] << " y " << this->parejas[std::make_pair(SusceptibleV, InfectadoV)] << endl;
    // cout << "hay bajo " << this->parejas[std::make_pair(SusceptibleNV, InfectadoNV)] << " y " << this->parejas[std::make_pair(SusceptibleNV, InfectadoV)] << endl;
    vector<Real> out_value;
    out_value.push_back(Real(encuentos_altoriesgo));
    out_value.push_back(Real(encuentos_bajoriesgo));

    Tuple<Real> outputmsg(&out_value);
    sendOutput(msg.time(), out, outputmsg);

    return *this;
}

void Foco::resetParejas() {
	vector<Estado> estados_posibles = { SusceptibleNV, InfectadoNV, RecuperadoNV, VacunadoNV,
										 SusceptibleV, InfectadoV, RecuperadoV, VacunadoV };
	for (uint i = 0; i < estados_posibles.size(); i++) {
		for (uint j = i; j < estados_posibles.size(); j++) {
			this->parejas[std::make_pair(estados_posibles[i], estados_posibles[j])] = 0;
		}
	}
}
