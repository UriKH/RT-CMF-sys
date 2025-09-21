# RT-CMF-sys

### Installation
Run: `pip install git+https://github.com/UriKH/RT-CMF-sys.git`

### Structure and Notes
#### Structure:
The system is composed of 3 stages:
1. Database - storing and retrieving mapping from a constant to the inspiration functions.
2. Analysis - analysis of each of the CMFs i.e., filtering and prioritization of shards, borders, etc. 
3. Search - deep and full search within the searchable spaces. This stage (will) contain further logic and particularly ascend logic.

#### Annotations:
* Directories with name of the format: `s_<name>` are per _stage_ directories.
* `.py` files of the format `m_<name>` are stage module implementation.