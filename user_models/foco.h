#ifndef _FOCO_H_
#define _FOCO_H_

#include <string>

#include "atomic.h"
#include "tuple_value.h"
#include "distri.h"

#include "constants.h"



#define ATOMIC_MODEL_FOCO "Foco"

/*
@ModelMetadata
name: Foco
input_ports: in
output_ports: out
*/
class Foco : public Atomic {
    public:
        Foco(const string &name = ATOMIC_MODEL_FOCO);
        virtual string className() const {  return ATOMIC_MODEL_FOCO ;}

    protected:
        Model &initFunction();
        Model &externalFunction( const ExternalMessage & );
        Model &internalFunction( const InternalMessage & );
        Model &outputFunction( const CollectMessage & );

    private:
        const Port &in;
        Port &out;

        std::map<std::pair<Estado,Estado>,uint> parejas;

        // Cantidad de Personas con las que se encuentra cada persona
        Distribution* dist;

        double get_randnorm(int min, int max);
        void resetParejas();
};

#endif
