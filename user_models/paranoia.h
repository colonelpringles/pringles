#ifndef _PARANOIA_H_
#define _PARANOIA_H_


#include <string>

#include "atomic.h"
#include "tuple_value.h"

#include "constants.h"



#define ATOMIC_MODEL_PARANOIA "Paranoia"

/*
@ModelMetadata
name: Paranoia
input_ports: in
output_ports: out
*/
class Paranoia : public Atomic {
    public:
        Paranoia(const string &name = ATOMIC_MODEL_PARANOIA);
        virtual string className() const {  return ATOMIC_MODEL_PARANOIA ;}

    protected:
        Model &initFunction();
        Model &externalFunction( const ExternalMessage & );
        Model &internalFunction( const InternalMessage & );
        Model &outputFunction( const CollectMessage & );

    private:
        const Port &in;
        Port &out;

        double p_inf_NV;
        double p_inf_V;
        double alpha;
        pair<int, int> asistentes_centro;

};

#endif
