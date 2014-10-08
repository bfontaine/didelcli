
JEKYLL=bundle exec jekyll

deps:
	bundle install

preview:
	$(JEKYLL) serve

build:
	$(JEKYLL) build
