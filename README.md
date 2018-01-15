# Accessibility visualizing tool

instructions [here](https://automating-gis-processes.github.io/2017/lessons/FA/final-assignment.html).

## set up
- clone this repo

- download data from [here](http://blogs.helsinki.fi/accessibility/helsinki-region-travel-time-matrix/) to this repo,
to under data folder

- create python 3.5 virtualenv and install requirements


## usage

- This script contains four command line commands.
1. find
- usage: python accessviz.py find --id_list="list, in, quotation, marks"
- example:

                        python .\accessviz.py find --id_list="6013577, foobar"

2. shape
- usage: python accessviz.py shape --YKR_ID=id
- example:

                        python .\accessviz.py shape --YKR_ID=6013577
                        python .\accessviz.py shape --YKR_ID=6013577 --output_folder="data/"

3. create_map
- usage: python accessviz.py create_map --YKR_ID=id --travel_mode=public,walk or car
- example:

                        python .\accessviz.py create_map --YKR_ID=6013577 --travel_mode=public

4. compare
- usage: python accessviz.py compare --YKR_ID=id --comp=time or distance --modes="[mode1, mode2"
- example:

                        python .\accessviz.py compare --YKR_ID=6013577 --comp="time" --modes="[walk, public]"
                        python .\accessviz.py compare --YKR_ID=6013577 --comp="distance" --modes="[public, car]"

