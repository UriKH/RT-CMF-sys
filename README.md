# RT-CMF-sys

## Installation
Run: `pip install git+https://github.com/UriKH/RT-CMF-sys.git`

## Usage
Interaction with the system is via the System class (`from system import System`) and using the config files.
The configurations are ordered in three layers from most general to per module configs:
1. Per Module config - each module contains a config file describing useful configuration and defining functionality (See the file for description). For example see: `db_stage/DBs/db_v1/config.py`
2. Per Stage config - e.g. in `configs`: `analysis.py`/`database.py`/`search.py`. These define the stage behavior. Notice not to use **stage** configurations that don't match the **modules** you are using.
3. System settings - `configs/system.py`. This file defines things like the visuals of the system and interaction.

**For Concreate usage see the `Example` folder containing a JSON file and a `.db` file for loading data to the system. For code usage see the `main.py` file.**

## Structure and Notes
### Structure:
The system is composed of 3 stages:
1. Database - storing and retrieving mapping from a constant to the inspiration functions.
2. Analysis - analysis of each of the CMFs i.e., filtering and prioritization of shards, borders, etc. 
3. Search - deep and full search within the searchable spaces. This stage (will) contain further logic and particularly ascend logic.

### Database
| Stage                 | Path            | Description     | Example |
| :-------------:       | :-------------: | :-------------: | :-------: |
| Main folder           | `db_stage`      |  Contains a file with schemes of DB **module** and general DB + special errors file| |
| Modules               | `db_stage/DBs`  |  Each module directory contains an implemenation of the **module** in a `X_mod.py`, `config.py` and opionally an implementation of the service. | `db_v1` folder in which there are `db_mod.py`   (implementing the module DBMod class), `db.py` (implementing the DB)|
| Supported functions   |`db_stage/funcs` | All functions are used by the Formatter defined in `formatter.py`. Each inspiration function will be implemented in a file in the same folder. |            |

### Analysis
| Stage                 | Path            | Description     | Example |
| :-------------:       | :-------------: | :-------------: | :-------: |
| Main folder           | `analysis_stage`      |  Contains a file with schemes of Analyzer **module** and general Analyzer + special errors file| |
| Modules               | `analysis_stage/analyzers`  |  See same row in _**Database**_ | |
| Searchable spaces (e.g. shard)   |`analysis_stage/subspaces` | Each subspace has its own directory in which there is an implementaion of the subspace according to `searchable.py` + optional `config.py` |            |

#### More files
- `module.py` - Defines the properties of a basic module (plus some utility decorators)
- `errors.py` - Defines basic and general erros.
- `system.py` - Impelemnts the core of the system.
