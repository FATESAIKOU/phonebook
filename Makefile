CC ?= gcc
CFLAGS_common ?= -Wall -std=gnu99
CFLAGS_orig = -O0
CFLAGS_opt  = -O0

EXEC = phonebook_orig phonebook_opt

GIT_HOOKS := .git/hooks/applied
.PHONY: all
all: $(GIT_HOOKS) $(EXEC)

$(GIT_HOOKS):
	@scripts/install-git-hooks
	@echo

SRCS_common = main.c

phonebook_orig: $(SRCS_common) phonebook_orig.c phonebook_orig.h
	$(CC) $(CFLAGS_common) $(CFLAGS_orig) \
		-DIMPL="\"$@.h\"" -o $@ \
		$(SRCS_common) $@.c

phonebook_opt: $(SRCS_common) phonebook_opt.c phonebook_opt.h
	$(CC) $(CFLAGS_common) $(CFLAGS_opt) \
		-DIMPL="\"$@.h\"" -o $@ \
		$(SRCS_common) $@.c

run: $(EXEC)
	echo 3 | sudo tee /proc/sys/vm/drop_caches
	watch -d -t "./phonebook_orig && echo 3 | sudo tee /proc/sys/vm/drop_caches"

cache-test: $(EXEC)
	perf stat --repeat 100 \
		-e cache-misses,cache-references,instructions,cycles \
		./phonebook_orig
	perf stat --repeat 100 \
		-e cache-misses,cache-references,instructions,cycles \
		./phonebook_opt

output.txt: cache-test calculate
	./calculate


plot: output.txt
	gnuplot scripts/runtime.gp

hash-size-plot: phonebook_orig phonebook_opt
	python genplot_scripts/executer.py "hash" phonebook_opt db hsizes > opt-multi-output.json    # default db_size = 100 ~ max, step +100, foreach hashsize
	python genplot_scripts/data_processor.py opt-multi-output.json
	

integration-plot: phonebook_orig phonebook_opt
	python genplot_scripts/executer.py "performance" phonebook_orig db > orig-multi-output.json  # default db_size = 100 ~ max, step +100, average string length(mu) = 1 ~ 100 -> unlimit
	python genplot_scripts/executer.py "performance" phonebook_opt db > opt-multi-output.json    # default db_size = 100 ~ max, step +100, average string length(mu) = 1 ~ 100 -> unlimit
	python genplot_scripts/data_processor.py orig-multi-output.json opt-multi-output.json


calculate: calculate.c
	$(CC) $(CFLAGS_common) $^ -o $@

.PHONY: clean
clean:
	$(RM) $(EXEC) *.o perf.* \
		calculate orig.txt opt.txt output.txt \
		runtime.png orig-multi-output.json opt-multi-output.json
