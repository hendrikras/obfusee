# obfusee
A very simple book cipher encoder/ decoder for the command line

It will take an input file written in plain text, and will try to find the individual words in a key file.
This can include: txt, pdf, epub, word or any other format supported by textract.

The key file needs to have all words mentioned that are also listed in the input file,
or it will exit mentioning the word it can't find.
If successful, a csv output file is created with the references to lines and words from the key file.
The original key file can then be used to decode the message.

Python and the textract package is required to run.
to install textract visit: http://textract.readthedocs.io/en/stable/installation.html

to encode a message run:
python encode.py example_key_doc.epub input.csv

to decode:
python decode.py example_key_doc.epub out.csv
