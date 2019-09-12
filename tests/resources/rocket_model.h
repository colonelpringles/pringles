/*******************************************************************
*
*  DESCRIPCION: Cola Genérica (on demand)
*
*  AUTORES:
*  	    Ing. Carlos Giorgetti
*          Iván A. Melgrati
*          Dra. Ana Rosa Tymoschuk
*	    v2:Alejandro Troccoli
*
*  EMAIL: mailto://cgiorget@frsf.utn.edu.ar
*         mailto://imelgrat@frsf.utn.edu.ar
*         mailto://anrotym@alpha.arcride.edu.ar
*	   mailto://atroccol@dc.uba.ar (v2)
*
*  FECHA: 15/10/1999
*         01/02/2001
*******************************************************************/
#ifndef __ROCKET_H
#define __ROCKET_H

#include <list>
#include "atomic.h"     	// class Atomic
#include "atomicstate.h"	//
#include "value.h"
#include "VTime.h"

#define ROCKET_MODEL_NAME "Rocket"

class RocketState : public AtomicState {

public:

	typedef std::list<value_ptr> ElementList ;
	ElementList elements ;

	RocketState(){};
	virtual ~RocketState(){};

	RocketState& operator=(RocketState& thisState); //Assignment
	void copyState(RocketState *);
	int  getSize() const;

};

/*
@ModelMetadata
name:   Rocket
input_ports: in, done
output_ports: out
*/
class Rocket : public Atomic
{
public:
	Rocket( const std::string &name = "Rocket" );
	virtual std::string className() const {  return "Rocket" ;}
protected:
	Model &initFunction();
	Model &externalFunction( const ExternalMessage & );
	Model &internalFunction( const InternalMessage & );
	Model &outputFunction( const CollectMessage & );

	ModelState* allocateState() {
		return new RocketState;
	}

private:
	const Port &in;
	const Port &done;
	Port &out;

	VTime preparationTime;

	RocketState::ElementList& elements();

};	// class Rocket

/*******************************************************************
* Shortcuts to state paramters
*********************************************************************/
inline
RocketState::ElementList& Rocket::elements() {
	return ((RocketState*)getCurrentState())->elements;
}

#endif   //__ROCKET_H
