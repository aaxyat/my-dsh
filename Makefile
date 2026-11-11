.PHONY: help check doctor capture apply apply-dry link inventory

help:
	@printf '%s\n' \
	  'make check        Validate the repository (no machine state needed)' \
	  'make doctor       Report environment, symlink and drift health' \
	  'make capture      Copy live profile into the repo and refresh inventory' \
	  'make apply        Deploy repo -> this machine' \
	  'make apply-dry    Show what apply would do' \
	  'make link         Create instruction and skill symlinks'

check:
	./bin/dsh check

doctor:
	./bin/dsh doctor

capture:
	./bin/dsh capture

apply:
	./bin/dsh apply

apply-dry:
	./bin/dsh apply --dry-run

link:
	./bin/dsh link
