#include <random>

#include "distri.h"
#include "helpers.h"

double rand_normal(double mean, double stddev, int min, int max) {
    Distribution *dist = Distribution::create("normal");
    dist->setVar(0, mean);
    dist->setVar(1, stddev);
    float result = dist->get();
    if (result > max) {
        return max;
    } else if (result < min) {
        return min;
    }
    return result;
}


int randint_inrange(int min, int max) {
    return min + (rand() % static_cast<int>(max - min + 1));
}


Estado randpick(vector<double> poblacion) {
    int poblacion_total = 0;
    for (int i=0; i<=7; i++) {
        poblacion_total = poblacion_total + static_cast<int>(poblacion[i]);
    }
    int randomnum = randint_inrange(0, poblacion_total-1);
    int poblacion_acum = 0;
    for (int i=0; i<=7; i++) {
        poblacion_acum += static_cast<int>(poblacion[i]);
        if (randomnum < poblacion_acum) {
            return static_cast<Estado>(i);
        }
    }
}

int get_cant_poblacion(Tuple<Real> poblacion) {
    int poblacion_total = 0;
    for (int i=0; i < poblacion.size(); i++) {
        poblacion_total += poblacion[i].value();
    }
    return poblacion_total;
}

int get_cant_poblacion(vector<double> poblacion) {
    int poblacion_total = 0;
    for (int i=0; i < poblacion.size(); i++) {
        poblacion_total += poblacion[i];
    }
    return poblacion_total;
}

double get_proporcion_infectados(Tuple<Real> poblacion) {
    int poblacion_total = get_cant_poblacion(poblacion);
    int infectados_total = poblacion[1].value() + poblacion[5].value();
    return double(infectados_total)/double(poblacion_total);
}

vector<double> from_tuple(Tuple<Real> tupl) {
    vector<double> ret;
    for (int i=0; i < tupl.size(); i++) {
        ret.push_back(tupl[i].value());
    }
    return ret;
}
