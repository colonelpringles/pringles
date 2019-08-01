/********************************************************************
*																	*
*      				 Auto Generated File                            *
*                     												*
*********************************************************************/

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

#include "paranoia.h"
#include "helpers.h"

using namespace std;

Paranoia::Paranoia( const string &name )
: Atomic( name ),
  in(addInputPort( "in" )),
  out(addOutputPort( "out" )){
}
/*******************************************************************
* Function Name: initFunction
********************************************************************/
Model &Paranoia::initFunction() {
	passivate();
    if (ParallelMainSimulator::Instance().existsParameter(description(), "p_inf_NV")) {
        p_inf_NV = str2Value(ParallelMainSimulator::Instance().getParameter(description(), "p_inf_NV"));
    }
    if (ParallelMainSimulator::Instance().existsParameter(description(), "p_inf_V")) {
        p_inf_V = str2Value(ParallelMainSimulator::Instance().getParameter(description(), "p_inf_V"));
    }
    if (ParallelMainSimulator::Instance().existsParameter(description(), "alpha")) {
        alpha = str2Value(ParallelMainSimulator::Instance().getParameter(description(), "alpha"));
    }
	return *this ;
}
/*******************************************************************
* Function Name: externalFunction
* Description: This method executes when an external event is received.
********************************************************************/
Model &Paranoia::externalFunction( const ExternalMessage &msg )
{
	nextChange(VTime::Zero);
    Tuple<Real> poblacion = *(Tuple<Real>::ptr_from_value(msg.value()).get()); // SIRV (NV) SIRV (V)

    double prop_infectados = get_proporcion_infectados(poblacion);
    asistentes_centro = make_pair<int, int>(
        (prop_infectados * p_inf_V * alpha) > 0.2 ? poblacion[4].value() * 0.2 : poblacion[4].value() * (prop_infectados * p_inf_V * alpha),
        (prop_infectados * p_inf_NV * alpha) > 0.2 ? poblacion[0].value() * 0.2 : poblacion[0].value() * (prop_infectados * p_inf_NV * alpha));
	return *this ;
}

/*******************************************************************
* Function Name: internalFunction
********************************************************************/
Model &Paranoia::internalFunction( const InternalMessage & )
{
	passivate();
	return *this;
}
/*******************************************************************
* Function Name: outputFunction
********************************************************************/
Model &Paranoia::outputFunction( const CollectMessage &msg ) {

    vector<Real> out_value;
    out_value.push_back(Real(static_cast<Value>(asistentes_centro.first)));
    out_value.push_back(Real(static_cast<Value>(asistentes_centro.second)));

    Tuple<Real> outputmsg(&out_value);
    sendOutput(msg.time(), out, outputmsg);

    return *this;
}
