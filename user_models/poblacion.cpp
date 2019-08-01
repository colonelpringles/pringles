#include "message.h"       // InternalMessage
#include "parsimu.h"      // class MainSimulator


#include <cmath>
#include <iomanip>
#include <iostream>
#include <map>
#include <math.h>
#include <random>
#include <sstream>
#include <stdlib.h>
#include <string>
#include <vector>

#include "poblacion.h"
#include "helpers.h"

using namespace std;

Poblacion::Poblacion( const string &name )
: Atomic( name ),
  in_deltavac(addInputPort( "in_deltavac" )),
  in_deltainf(addInputPort( "in_deltainf" )),
  out(addOutputPort( "out" )){
}
/*******************************************************************
* Function Name: initFunction
********************************************************************/
Model &Poblacion::initFunction() {
	nextChange(VTime::Zero);
    if (ParallelMainSimulator::Instance().existsParameter(description(), "susceptibles_nv")) {
        susceptibles_nv = str2Int(ParallelMainSimulator::Instance().getParameter(description(), "susceptibles_nv"));
    }
    if (ParallelMainSimulator::Instance().existsParameter(description(), "susceptibles_v")) {
        susceptibles_v = str2Int(ParallelMainSimulator::Instance().getParameter(description(), "susceptibles_v"));
    }
    if (ParallelMainSimulator::Instance().existsParameter(description(), "infectados_nv")) {
        infectados_nv = str2Int(ParallelMainSimulator::Instance().getParameter(description(), "infectados_nv"));
    }
    if (ParallelMainSimulator::Instance().existsParameter(description(), "infectados_v")) {
        infectados_v = str2Int(ParallelMainSimulator::Instance().getParameter(description(), "infectados_v"));
    }
    if (ParallelMainSimulator::Instance().existsParameter(description(), "recuperados_nv")) {
        recuperados_nv = str2Int(ParallelMainSimulator::Instance().getParameter(description(), "recuperados_nv"));
    }
    if (ParallelMainSimulator::Instance().existsParameter(description(), "recuperados_v")) {
        recuperados_v = str2Int(ParallelMainSimulator::Instance().getParameter(description(), "recuperados_v"));
    }
    if (ParallelMainSimulator::Instance().existsParameter(description(), "vacunados_nv")) {
        vacunados_nv = str2Int(ParallelMainSimulator::Instance().getParameter(description(), "vacunados_nv"));
    }
    if (ParallelMainSimulator::Instance().existsParameter(description(), "vacunados_v")) {
        vacunados_v = str2Int(ParallelMainSimulator::Instance().getParameter(description(), "vacunados_v"));
    }
    if (ParallelMainSimulator::Instance().existsParameter(description(), "proba_sana_nv")) {
        proba_sana_nv = str2Value(ParallelMainSimulator::Instance().getParameter(description(), "proba_sana_nv"));
    }
    if (ParallelMainSimulator::Instance().existsParameter(description(), "proba_sana_v")) {
        proba_sana_v = str2Value(ParallelMainSimulator::Instance().getParameter(description(), "proba_sana_v"));
    }
    return *this;
}
/*******************************************************************
* Function Name: externalFunction
* Description: This method executes when an external event is received.
********************************************************************/
Model &Poblacion::externalFunction( const ExternalMessage &msg ) {
    // cout << "Se llama a extfun " << endl;
    Tuple<Real> delta = Tuple<Real>::from_value(msg.value());
    // cout << "El msj dice : " << static_cast<int>(delta[0].value()) << ", " << static_cast<int>(delta[1].value()) << endl;

    // Si los cambios en vacunados y en susceptibles que llegan juntos hay mas que los sanos, el que llega despues satura 
    int delta_v = susceptibles_v - delta[0].value() < 0 ? susceptibles_v : static_cast<int>(delta[0].value());
    int delta_nv = susceptibles_nv - delta[1].value() < 0 ? susceptibles_nv : static_cast<int>(delta[1].value());

    susceptibles_v -= delta_v;
    susceptibles_nv -= delta_nv;
    if(msg.port() == in_deltavac){
        // cout << "Es de vacunas" << endl;
        vacunados_v += delta_v;
        vacunados_nv += delta_nv;
	} else if(msg.port() == in_deltainf){
        // cout << "Es de infectados"<< endl;
        infectados_v += delta_v;
        infectados_nv += delta_nv;
    }

    holdIn(AtomicState::active, VTime(0, 0, 1, 0, 0)); //Tomamos los segundos como si fueran dias

	return *this ;
}


Model &Poblacion::internalFunction( const InternalMessage & )
{
    // Ya tenemos infectados y vacunados que nos mandaron los otros
    // cout << "Tras interna..." << endl;
    int cant_sanados_nv = infectados_nv * proba_sana_nv;
    int cant_sanados_v = infectados_v * proba_sana_v;
    // cout << "se sanaron " << cant_sanados_v << " y " << cant_sanados_nv << endl;
    recuperados_nv += cant_sanados_nv;
    infectados_nv -= cant_sanados_nv;

    recuperados_v += cant_sanados_v;
    infectados_v -= cant_sanados_nv;

    passivate();

	return *this;
}

Model &Poblacion::outputFunction( const CollectMessage &msg ) {
    sendOutput(msg.time(), out, get_poblacion_serializada());
    return *this;
}


Tuple<Real> Poblacion::get_poblacion_serializada() {
    // SIRV (NV) SIRV (V)
    vector<Real> return_vec;
    return_vec.push_back(Real(static_cast<Value>(susceptibles_nv)));
    return_vec.push_back(Real(static_cast<Value>(infectados_nv)));
    return_vec.push_back(Real(static_cast<Value>(recuperados_nv)));
    return_vec.push_back(Real(static_cast<Value>(vacunados_nv)));
    return_vec.push_back(Real(static_cast<Value>(susceptibles_v)));
    return_vec.push_back(Real(static_cast<Value>(infectados_v)));
    return_vec.push_back(Real(static_cast<Value>(recuperados_v)));
    return_vec.push_back(Real(static_cast<Value>(vacunados_v)));

    return Tuple<Real>(&return_vec);
}
