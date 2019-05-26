[top]
components : sample_queue@Queue
out : emitted_signal
in : incoming_Event

link : out@sample_queue emitted_signal
link : incoming_Event in@sample_queue

[sample_queue]
preparation : 0:0:5:0 
