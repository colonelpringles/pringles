#ifndef _SIST_PREVENCION_H_
#define _SIST_PREVENCION_H_

#include <string>

#include "atomic.h"
#include "tuple_value.h"

#include "constants.h"



#define ATOMIC_MODEL_SIST_PREVENCION "SistPrevencion"

/*
@ModelMetadata
name: SistPrevencion
input_ports: in 
output_ports: out
*/
class SistPrevencion : public Atomic {
    public:
        SistPrevencion(const string &name = ATOMIC_MODEL_SIST_PREVENCION);
        virtual string className() const {  return ATOMIC_MODEL_SIST_PREVENCION ;}

    protected:
        Model &initFunction();
        Model &externalFunction( const ExternalMessage & );
        Model &internalFunction( const InternalMessage & );
        Model &outputFunction( const CollectMessage & );

    private:
        const Port &in;
        Port &out;

        double prop_infectados_inicio; // Prop a partir del que se activa el sistema de vacunacion
        double prop_infectados_cierre; // Prop a partir del que se desactiva el sistema de vacunacion
        bool sistema_activo;

};

#endif
