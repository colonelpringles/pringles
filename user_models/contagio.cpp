/********************************************************************
*																	*
*      				 Auto Generated File                            *
*                     												*
*********************************************************************/

#include "message.h"       // InternalMessage
#include "parsimu.h"      // class MainSimulator


#include <map>
#include <vector>

#include "contagio.h"
#include "helpers.h"

using namespace std;

Contagio::Contagio( const string &name )
: Atomic( name ),
  in(addInputPort( "in" )),
  out(addOutputPort( "out" )){
}
/*******************************************************************
* Function Name: initFunction
********************************************************************/
Model &Contagio::initFunction() {
	passivate();
    if (ParallelMainSimulator::Instance().existsParameter(description(), "threshold_NV")) {
        threshold_NV = str2Int(ParallelMainSimulator::Instance().getParameter(description(), "threshold_NV"));
    }
    if (ParallelMainSimulator::Instance().existsParameter(description(), "threshold_V")) {
        threshold_V = str2Int(ParallelMainSimulator::Instance().getParameter(description(), "threshold_V"));
    }
    return *this ;
}
/*******************************************************************
* Function Name: externalFunction
* Description: This method executes when an external event is received.
********************************************************************/
Model &Contagio::externalFunction( const ExternalMessage &msg )
{
	nextChange(VTime::Zero);
    nuevos_enfermos_V = 0;
    nuevos_enfermos_NV = 0;

    Tuple<Real> parejas = *(Tuple<Real>::ptr_from_value(msg.value()).get());
    double encuentos_altoriesgo = parejas[0].value();
    double encuentos_bajoriesgo = parejas[1].value();

    for (int i =0; i< encuentos_altoriesgo; i++){
        uint randnum = randint_inrange(0,100);
        if (randnum < threshold_V) {
            nuevos_enfermos_V++;
        }
    }

    for (int i =0; i< encuentos_bajoriesgo; i++){
        uint randnum = randint_inrange(0,100);
        if (randnum < threshold_NV) {
            nuevos_enfermos_NV++;
        }
    }
	return *this ;
}

/*******************************************************************
* Function Name: internalFunction
********************************************************************/
Model &Contagio::internalFunction( const InternalMessage & )
{
	passivate();
	return *this;
}
/*******************************************************************
* Function Name: outputFunction
********************************************************************/
Model &Contagio::outputFunction( const CollectMessage &msg ) {
    vector<Real> out_value;
    out_value.push_back(Real(static_cast<Value>(nuevos_enfermos_V)));
    out_value.push_back(Real(static_cast<Value>(nuevos_enfermos_NV)));

    Tuple<Real> outputmsg(&out_value);
    sendOutput(msg.time(), out, outputmsg);

    return *this;
}
