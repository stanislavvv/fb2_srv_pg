FLAKE8_ARGS=--max-line-length=120
DATA=data
export FLASK_ENV=prod

# internal name, change to what you want
DOCKERTAG="fb2srv-pg:latest"

help:
	@echo "Run \`make <target>'"
	@echo "Available targets:"
	@echo "  clean    - clean all"
	@echo "  flakeall - check all .py by flake8"
	@echo "  help     - this text"
	@echo "  newpages - recreate data/pages"

clean:
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete

flakeall:
	find . -name '*.py' -print0 | xargs -0 -n 100 flake8 $(FLAKE8_ARGS)

newpages:
	@echo "--- rename old pages ---"
	mv -f data/pages "$(DATA)/pages.rm" ||:
	@echo "------ lists ------"
	./datachew.py new_lists
	@echo "------ stages -----"
	./datachew.py stage1
	./datachew.py stage2
	./datachew.py stage3
	./datachew.py stage4
	@echo "--- remove old pages ---"
	rm -rf "$(DATA)/pages.rm" ||:

dockerbuild:
	docker build -t "$(DOCKERTAG)" .