reset
set ylabel 'count'
set xlabel 'string length'
set style data lines
set title 'db-distribution'
set term png enhanced font 'Verdana,10'
set output 'db.png'

plot 'test_plot-db.txt'
