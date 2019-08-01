#ifndef _CONTAGIO_H_
#define _CONTAGIO_H_


#include <string>

#include "atomic.h"
#include "tuple_value.h"

#include "constants.h"



#define ATOMIC_MODEL_CONTAGIO "Contagio"


/*
@ModelMetadata
name: Contagio
input_ports: in
output_ports: out
*/
class Contagio : public Atomic {
    public:
        Contagio(const string &name = ATOMIC_MODEL_CONTAGIO);
        virtual string className() const {  return ATOMIC_MODEL_CONTAGIO ;}

    protected:
        Model &initFunction();
        Model &externalFunction( const ExternalMessage & );
        Model &internalFunction( const InternalMessage & );
        Model &outputFunction( const CollectMessage & );

    private:
        const Port &in;
        Port &out;

        int nuevos_enfermos_V;
        int nuevos_enfermos_NV;
        uint threshold_NV; //Porcentaje proba contagio
        uint threshold_V;

        void resetParejas();
};

#endif
