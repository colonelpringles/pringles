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

#include "vacunatorio.h"
#include "helpers.h"

using namespace std;

Vacunatorio::Vacunatorio( const string &name )
: Atomic( name ),
  in_pacientes(addInputPort( "in_pacientes" )),
  in_activo(addInputPort( "in_activo" )),
  out(addOutputPort( "out" )){
}
/*******************************************************************
* Function Name: initFunction
********************************************************************/
Model &Vacunatorio::initFunction() {
	passivate();
    cant_vacunas = 0;
    if (ParallelMainSimulator::Instance().existsParameter(description(), "cant_vacunas_por_dia_activo")) {
		cant_vacunas_por_dia_activo = str2Int(ParallelMainSimulator::Instance().getParameter(description(), "cant_vacunas_por_dia_activo"));
	}
	return *this ;
}
/*******************************************************************
* Function Name: externalFunction
* Description: This method executes when an external event is received.
********************************************************************/
Model &Vacunatorio::externalFunction( const ExternalMessage &msg )
{
	nextChange(VTime::Zero);
    if(msg.port() == in_activo){
        bool activo = Real::from_value(msg.value()).value() != 0.0;
        cant_vacunas = activo ? cant_vacunas_por_dia_activo : 0;
	} else if(msg.port() == in_pacientes){
        Tuple<Real> pacientes_vnv = *(Tuple<Real>::ptr_from_value(msg.value()).get());
        int vulnerables = static_cast<int>(pacientes_vnv[0].value());
        int novulnerables = static_cast<int>(pacientes_vnv[1].value());

        if (cant_vacunas <= vulnerables) {
            vacunados = make_pair<int, int>(int(cant_vacunas), 0);
        } else {
            vacunados = make_pair<int, int>(int(vulnerables),
                                            int(std::min(cant_vacunas - vulnerables, novulnerables)));
        }
    }
	return *this ;
}

/*******************************************************************
* Function Name: internalFunction
********************************************************************/
Model &Vacunatorio::internalFunction( const InternalMessage & )
{
	passivate();
	return *this;
}
/*******************************************************************
* Function Name: outputFunction
********************************************************************/
Model &Vacunatorio::outputFunction( const CollectMessage &msg ) {

    vector<Real> out_value;
    out_value.push_back(Real(static_cast<Value>(vacunados.first))); //vulnerables
    out_value.push_back(Real(static_cast<Value>(vacunados.second))); //NV

    Tuple<Real> outputmsg(&out_value);
    sendOutput(msg.time(), out, outputmsg);

    return *this;
}
