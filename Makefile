# makefile
#
PROJECT := viastats

AWS_REGION := us-east-1

DEPENDENCIES := https://github.com/rstms/python-lambda/archive/v2.2.0-fixed.zip chromedriver selenium

GITURL := https://github.com/rstms/serverless-chrome/raw/master/chrome
TARBALL := chrome-headless-lambda-linux-x64.tar.gz

default: depends headless-chrome

depends:
	pip install $(DEPENDENCIES)

$(TARBALL):
	wget $(GITURL)/$(TARBALL)

headless-chrome: $(TARBALL)
	tar zxfv $(TARBALL)
	cp templates/* headless-chrome

clean:
	rm -f *.zip
	rm -f *.pyc
	rm -rf headless-chrome 
	rm -rf dist
	rm -f *.json
	rm -f *.png
	rm -f 

test:
	ssh beaker rm -f $(PROJECT)/*.png
	rm -f *.png
	python3 $(PROJECT).py
	scp *.png beaker:$(PROJECT)
