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

#include "sist_prevencion.h"
#include "helpers.h"

using namespace std;

SistPrevencion::SistPrevencion( const string &name )
: Atomic( name ),
  in(addInputPort( "in" )),
  out(addOutputPort( "out" )){
}
/*******************************************************************
* Function Name: initFunction
********************************************************************/
Model &SistPrevencion::initFunction() {
	passivate();
    if (ParallelMainSimulator::Instance().existsParameter(description(), "prop_infectados_inicio")) {
        prop_infectados_inicio = str2Value(ParallelMainSimulator::Instance().getParameter(description(), "prop_infectados_inicio"));
    }
    if (ParallelMainSimulator::Instance().existsParameter(description(), "prop_infectados_cierre")) {
        prop_infectados_cierre = str2Value(ParallelMainSimulator::Instance().getParameter(description(), "prop_infectados_cierre"));
    }
    sistema_activo = false;
}
/*******************************************************************
* Function Name: externalFunction
* Description: This method executes when an external event is received.
********************************************************************/
Model &SistPrevencion::externalFunction( const ExternalMessage &msg ) {
    nextChange(VTime::Zero);
    Tuple<Real> poblacion = Tuple<Real>::from_value(msg.value()); // SIRV (NV) SIRV (V)

    double prop_infectados = get_proporcion_infectados(poblacion);

    if (sistema_activo && prop_infectados < prop_infectados_cierre) {
        sistema_activo = false;
    } else if (!sistema_activo && prop_infectados > prop_infectados_inicio) {
        sistema_activo = true;
    }
    return *this ;
}

/*******************************************************************
* Function Name: internalFunction
********************************************************************/
Model &SistPrevencion::internalFunction( const InternalMessage & )
{
	passivate();
	return *this;
}
/*******************************************************************
* Function Name: outputFunction
********************************************************************/
Model &SistPrevencion::outputFunction( const CollectMessage &msg ) {
    double val = sistema_activo ? 1.0 : 0.0;

    sendOutput(msg.time(), out, val);
    return *this;
}
