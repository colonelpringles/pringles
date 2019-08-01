#ifndef _HELPERS_H_
#define _HELPERS_H_

#include <vector>
#include "tuple_value.h"

#include "constants.h"

using namespace std;

double rand_normal(double mean, double stddev, int min, int max);

int randint_inrange(int min, int max);

Estado randpick(vector<double> poblacion);

int get_cant_poblacion(Tuple<Real> poblacion);

int get_cant_poblacion(vector<double> poblacion);

double get_proporcion_infectados(Tuple<Real> poblacion);

vector<double> from_tuple(Tuple<Real> tupl);

#endif
