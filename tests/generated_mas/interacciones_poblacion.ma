[interacciones_poblacion]
components: foco@Foco contagio@Contagio
out: out_port
in: in_port
link: in_port in@foco
link: out@foco in@contagio
link: out@contagio out_port


[foco]
mean: 2
std: 1


[contagio]
threshold_NV: 30
threshold_V: 80
