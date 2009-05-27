ACTIONS_DIR:=$$(kde4-config --install data)/solid/actions

all:
	pyuic4 importdialog.ui -o ui_importdialog.py
	pyuic4 progresspage.ui -o ui_progresspage.py

clean:
	-rm *.pyc ui_*.py

install:
	mkdir -p $(ACTIONS_DIR)
	cp gwenview-importer.desktop $(ACTIONS_DIR)/
