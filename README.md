# RT-CMF-sys

## Installation
Run: `pip install git+https://github.com/UriKH/RT-CMF-sys.git`

## Usage
Interaction with the system is via the System class (`from access import System`) and using the config files.
For easy usage preform accessing to configs, errors and functionality via `access.py`.

### Usage examples:
##### main.py
```
from access import System, DBModV1, AnalyzerModV1, SearcherModV1

results = System(
  dbs = [ DBModV1(path='./my_database.db', json_path='./my_data.json') ],
  analyzers = [ AnalyzerModV1 ],
  searcher = SearcherModV1
).run(constants=['pi', 'gamma'])
```
**Note:** 
- Although the example shows way to search multiple constants simultaniously this option is not supported currently.
- If we don't want to load or execute commadns using a JSON file, `json_path` could be ommited from the arguments.

##### data.json
When reading this file, the system will execute the `append` command and will try to add the inspiration function ${}_2F_1(0.5)$ to set of inpiration funcitons for $\pi$ with the shift in start point as $x=0,~y=0,~z=\text{sp.Rational(1,2)}$.
```
{
    "command": "append",
    "data": [
        {
            "constant": "pi",
            "data": {
                "type": "pFq_formatter",
                "data": { "p": 2, "q": 1, "z": "1/2", "shifts": [0, 0, "1/2"] }
            }
        }
    ]
}
```

## Structure and Notes
### Structure:
The system is composed of 3 stages:
1. Database - storing and retrieving mapping from a constant to the inspiration functions.
2. Analysis - analysis of each of the CMFs i.e., filtering and prioritization of shards, borders, etc. 
3. Search - deep and full search within the searchable spaces. This stage (will) contain further logic and particularly ascend logic.

#### Configuration
The configurations are ordered in three layers from most general to per module configs:
1. Per Module config - each module contains a config file describing useful configuration and defining functionality (See the file for description). For example see: `db_stage/DBs/db_v1/config.py`
2. Per Stage config - e.g. in `configs`: `analysis.py`/`database.py`/`search.py`. These define the stage behavior. Notice not to use **stage** configurations that don't match the **modules** you are using.
3. System settings - `configs/system.py`. This file defines things like the visuals of the system and interaction.

Globally the system looks as follows:
```
RT-CMF-sys
│   access.py
│
├─── system
├─── configs
├─── db_stage
├─── analysis_stage
├─── search_stage
└─── utils
```

### Database
| Stage                 | Path            | Description     | Example |
| :-------------:       | :-------------: | :-------------: | :-------: |
| Main folder           | `db_stage`      |  Contains a file with schemes of DB **module** and general DB + special errors file| |
| Modules               | `db_stage/DBs`  |  Each module directory contains an implemenation of the **module** in a `X_mod.py`, `config.py` and opionally an implementation of the service. | `db_v1` folder in which there are `db_mod.py`   (implementing the module DBMod class), `db.py` (implementing the DB)|
| Supported functions   |`db_stage/funcs` | All functions are used by the Formatter defined in `formatter.py`. Each inspiration function will be implemented in a file in the same folder. |            |
```
db_stage
│   db_scheme.py
│   errors.py
│
├─── DBs
│    └─── db_v1
│           config.py
│           db.py
│           db_mod.py
│
└─── funcs
        config.py
        formatter.py
        pFq_fmt.py
```

### Analysis
| Stage                 | Path            | Description     |
| :-------------:       | :-------------: | :-------------: |
| Main folder           | `analysis_stage`      | Contains a file with schemes of Analyzer **module** and general Analyzer + special errors file| 
| Modules               | `analysis_stage/analyzers`  |  See same row in _**Database**_ |
| Searchable spaces (e.g. shard)   |`analysis_stage/subspaces` | Each subspace has its own directory in which contains an implementaion of the subspace according to `searchable.py` + optional `config.py` | 
```
analysis_stage  
│    analysis_scheme.py  
│    errors.py  
│      
├─── analyzers  
│    └─── analyzer_v1  
│             analyzer.py  
│             analyzer_mod.py  
│             config.py  
│  
└─── subspaces  
     │   searchable.py  
     ├─── ev_border  
     └─── shard  
              config.py  
              shard.py  
              shard_extraction.py
 ```

### Searching
| Stage                 | Path            | Description     |
| :-------------:       | :-------------: | :-------------: |
| Main folder           | `search_stage`      | Contains a file with schemes of Searcher **module** and general Searcher | 
| Modules               | `search_stage/searchers`  |  See same row in _**Database**_ |
| Search methods    |`search_stage/methods` | Each method has its own directory in which contins an implementaion of the method according to `searcher_scheme.py` + optional `config.py` | 

```
search_stage
│   data_manager.py
│   searcher_scheme.py
│
├─── methods
│    └─── serial
│             config.py
│             serial_searcher.py
│       
└─── searchers
     └─── searcher_v1
              config.py
              searcher_mod.py
```

### System and utils
- `system` contains system implementation, module implementation and system unique errors.
- `utils` contains utilities like logger and usfull type annotations for most of the code. `geometry` contains more specific utilities regarding geometrical calculations. 
```
system
    errors.py
    system.py
    module.py

utils
│   logger.py
│   types.py
│   
└─── geometry
        plane.py
        point_generator.py
        position.py
```



