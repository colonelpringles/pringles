#ifndef _POBLACION_H_
#define _POBLACION_H_

#include <string>

#include "atomic.h"
#include "tuple_value.h"

#include "constants.h"



#define ATOMIC_MODEL_POBLACION "Poblacion"

/*
@ModelMetadata
name: Poblacion
input_ports: in_deltavac,in_deltainf 
output_ports: out
*/
class Poblacion : public Atomic {
    public:
        Poblacion(const string &name = ATOMIC_MODEL_POBLACION);
        virtual string className() const {  return ATOMIC_MODEL_POBLACION ;}

    protected:
        Model &initFunction();
        Model &externalFunction( const ExternalMessage & );
        Model &internalFunction( const InternalMessage & );
        Model &outputFunction( const CollectMessage & );

    private:
        const Port &in_deltavac;
        const Port &in_deltainf;
        Port &out; //Manda SIRV

        uint susceptibles_nv;
        uint susceptibles_v;
        uint infectados_nv;
        uint infectados_v;
        uint recuperados_nv;
        uint recuperados_v;
        uint vacunados_nv;
        uint vacunados_v;

        double proba_sana_nv;
        double proba_sana_v;

        Tuple<Real> get_poblacion_serializada();

};

#endif
