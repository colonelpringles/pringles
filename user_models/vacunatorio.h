#ifndef _VACUNATORIO_H_
#define _VACUNATORIO_H_

// #include <map>
// #include <utility>
// #include <vector>
// #include "VTime.h"


#include <string>

#include "atomic.h"
#include "tuple_value.h"

#include "constants.h"



#define ATOMIC_MODEL_VACUNATORIO "Vacunatorio"

/*
@ModelMetadata
name: Vacunatorio
input_ports: in_pacientes, in_activo 
output_ports: out
*/
class Vacunatorio : public Atomic {
    public:
        Vacunatorio(const string &name = ATOMIC_MODEL_VACUNATORIO);
        virtual string className() const {  return ATOMIC_MODEL_VACUNATORIO ;}

    protected:
        Model &initFunction();
        Model &externalFunction( const ExternalMessage & );
        Model &internalFunction( const InternalMessage & );
        Model &outputFunction( const CollectMessage & );

    private:
        const Port &in_pacientes;
        const Port &in_activo;
        Port &out;

        int cant_vacunas_por_dia_activo;
        int cant_vacunas;
        pair<int, int> vacunados;
};

#endif
