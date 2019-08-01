#include "pmodeladm.h"
#include "register.h"

#include "foco.h"
#include "contagio.h"
#include "vacunatorio.h"
#include "paranoia.h"
#include "sist_prevencion.h"
#include "poblacion.h"


void register_atomics_on(ParallelModelAdmin &admin)
{
	admin.registerAtomic(NewAtomicFunction<Foco>(), ATOMIC_MODEL_FOCO);
	admin.registerAtomic(NewAtomicFunction<Contagio>(), ATOMIC_MODEL_CONTAGIO);
	admin.registerAtomic(NewAtomicFunction<Vacunatorio>(), ATOMIC_MODEL_VACUNATORIO);
	admin.registerAtomic(NewAtomicFunction<Paranoia>(), ATOMIC_MODEL_PARANOIA);
	admin.registerAtomic(NewAtomicFunction<SistPrevencion>(), ATOMIC_MODEL_SIST_PREVENCION);
	admin.registerAtomic(NewAtomicFunction<Poblacion>(), ATOMIC_MODEL_POBLACION);
}
