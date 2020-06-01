###############################################################################
# NAME:		    Makefile
#
# AUTHOR:	    Ethan D. Twardy <edtwardy@mtu.edu>
#
# DESCRIPTION:	    This makefile is used to generate the distribution files.
#
# CREATED:	    06/01/2020
#
# LAST EDITED:	    06/01/2020
###

dist:
	python3 setup.py sdist

upload:

###############################################################################
