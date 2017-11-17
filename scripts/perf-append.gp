reset
set xlabel 'db size(100 * 1.5^x)'
set ylabel 'string length'
set style data lines
set title 'append time'
set term png enhanced font 'Verdana,10'
set pm3d;
set hidden;

set palette model HSV functions gray, 1, 1
set terminal png size 1024,1024

set output 'perf-append.png'
splot 'test_plot-append-avg.txt' lt -3

set view map
set output 'perf-map-append.png'
splot 'test_plot-append-avg.txt' lt -3
